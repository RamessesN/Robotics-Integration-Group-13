import cv2
import action_ctrl
from env_import import *
from ultralytics import YOLO
from robomaster_ultra import camera

annotated_frame = None
prev_time = 0
running = True

fps_list = []

model = YOLO("../cv/mlmodel/pt/cola_v1.pt")

def yolo_predict(frame):
    global prev_time

    results = model(frame, conf=0.25, device=cfg.DEVICE, verbose=False)
    annotated = results[0].plot()

    height, width = frame.shape[:2]

    current_time = cv2.getTickCount()
    fps = cv2.getTickFrequency() / (current_time - prev_time) if prev_time > 0 else 0
    prev_time = current_time

    fps_list.append(fps)
    if len(fps_list) > 10: # 10帧连续帧取平均
        fps_list.pop(0)
    avg_fps = sum(fps_list) / len(fps_list)

    distance_text = "N/A"
    if len(results) > 0 and  action_ctrl.latest_distance is not None:
        distance_text = f"{action_ctrl.latest_distance / 10:.2f} cm"

    cv2.putText(
        annotated, f"RES: {width}x{height}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        1, (0, 0, 255), 2, lineType=cv2.LINE_AA
    )
    cv2.putText(
        annotated, f"FPS: {int(avg_fps)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
        1, (0, 255, 0), 2, lineType=cv2.LINE_AA
    )
    cv2.putText(
        annotated, f"Distance: {distance_text}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX,
        1, (255, 0, 0), 2, lineType=cv2.LINE_AA
    )

    return annotated


def video_capture(ep_camera):
    global latest_frame, annotated_frame, running

    ep_camera.start_video_stream(display = False, resolution = camera.STREAM_360P)

    while True:
        img = ep_camera.read_cv2_image()
        if img is not None:
            latest_frame = img
            annotated_frame = yolo_predict(img)