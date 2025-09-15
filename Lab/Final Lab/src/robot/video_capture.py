import cv2, time
import numpy as np
import action_ctrl as ac
import marker_config as mc
from env_import import *
from typing import Optional
from ultralytics import YOLO
from robomaster_ultra import camera

latest_frame: Optional[np.ndarray] = None
annotated_frame: Optional[np.ndarray] = None

target_x = None
target_y = None
prev_time = 0
running = True
fps_list = []

model = YOLO("../cv/mlmodel/pt/cola_v2.pt")

def yolo_predict(frame):
    global prev_time, target_x, target_y

    results = model(frame, conf = 0.25, device = cfg.DEVICE, verbose = False)
    annotated = results[0].plot()

    height, width = frame.shape[:2]
    center_x = width // 2

    target_x, target_y = None, None

    if len(results[0].boxes) > 0:
        box = results[0].boxes[0] # 取置信度最高的目标
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        target_x = (x1 + x2) // 2
        target_y = (y1 + y2) // 2
        if not (10 <= target_x <= width - 10) or not (10 <= target_y <= height - 10): # 滤掉干扰
            target_x = None
            target_y = None
    else:
        target_x = None
        target_y = None

    cv2.line(annotated, (center_x, 0), (center_x, height), (255, 255, 255), 1)
    cv2.line(annotated, (0, height // 2), (width, height // 2), (255, 255, 255), 1)

    if target_x is not None and target_y is not None:
        cv2.circle(annotated, (target_x, target_y), 5, (255, 0, 0), -1)

    current_time = time.time()
    fps = 1.0 / (current_time - prev_time) if prev_time > 0 else 0
    prev_time = current_time

    fps_list.append(fps)
    if len(fps_list) > 10: # 10帧连续帧取平均
        fps_list.pop(0)
    avg_fps = sum(fps_list) / len(fps_list)

    distance_text = "N/A"
    if ac.latest_distance is not None:
        distance_text = f"{ac.latest_distance / 10:.2f} cm"

    cv2.putText( # 打印分辨率
        annotated, f"RES: {width}x{height}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        1, (0, 0, 255), 2, lineType=cv2.LINE_AA
    )
    cv2.putText( # 打印帧率
        annotated, f"FPS: {int(avg_fps)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
        1, (0, 255, 0), 2, lineType=cv2.LINE_AA
    )
    cv2.putText( # 打印距离
        annotated, f"Distance: {distance_text}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX,
        1, (255, 0, 0), 2, lineType=cv2.LINE_AA
    )

    return annotated, target_x, target_y

def video_capture(ep_camera, ep_vision):
    global latest_frame, annotated_frame, target_x, target_y, running

    ep_vision.sub_detect_info(name = "marker", callback = mc.sub_data_handler_vision)
    ep_camera.start_video_stream(display = False, resolution = camera.STREAM_360P)

    while running:
        img = ep_camera.read_cv2_image()
        if img is not None:
            latest_frame = img
            annotated_frame, target_x, target_y = yolo_predict(img)

            if mc.closest_marker is not None:
                x1, y1 = mc.closest_marker.pt1
                center_x, center_y = mc.closest_marker.center

                cv2.rectangle(
                    annotated_frame, mc.closest_marker.pt1, mc.closest_marker.pt2, (0, 255, 0), 2
                )
                cv2.circle(
                    annotated_frame, (center_x, center_y), 5, (0, 255, 0), -1
                )
                cv2.putText(
                    annotated_frame, f"Marker {mc.closest_marker.info}", (center_x - 30, max(0, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )