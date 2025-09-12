import cv2, time
import action_ctrl as ac
from env_import import *
from ultralytics import YOLO
from robomaster_ultra import camera

latest_frame = None
annotated_frame = None
target_x = None
target_y = None
prev_time = 0
running = True
fps_list = []

model = YOLO("../cv/mlmodel/pt/cola_v2.pt")

def yolo_predict(frame):
    global prev_time, target_x, target_y

    results = model(frame, conf=0.25, device=cfg.DEVICE, verbose=False)
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
        cv2.circle(annotated, (target_x, target_y), 5, (0, 255, 255), -1)

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

def video_capture(ep_camera):
    global latest_frame, annotated_frame, target_x, target_y, running

    ep_camera.start_video_stream(display = False, resolution = camera.STREAM_360P)

    while running:
        img = ep_camera.read_cv2_image()
        if img is not None:
            latest_frame = img
            annotated_frame, target_x, target_y = yolo_predict(img)