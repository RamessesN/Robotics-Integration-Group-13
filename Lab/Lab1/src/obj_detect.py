import cv2
from ultralytics import YOLO
from env_config import COMBINED_DATA_YAML, COMBINED_BEST_MODEL_PATH, DEVICE

def validate_model():
    print("Checking model Performance...")
    model = YOLO(COMBINED_BEST_MODEL_PATH)
    metrics = model.val(data = COMBINED_DATA_YAML, device = DEVICE)
    print(f"Results: mAP50: {metrics.box.map50:.3f}, mAP50-95: {metrics.box.map:.3f}")
    return model

def detect_from_camera(model):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera open failed")
        return

    # RES config
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera resolution: {width}x{height}")

    prev_time = 0

    # Window
    window_name = "on Live"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    screen_width = 1512
    screen_height = 982

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    cv2.moveWindow(window_name, int(x), int(y))

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Read frames failed")
            break

        current_time = cv2.getTickCount()

        results = model.predict(frame, conf = 0.25, device = DEVICE, verbose = False)
        annotated_frame = results[0].plot()

        # FPS config
        fps = cv2.getTickFrequency() / (current_time - prev_time)
        prev_time = current_time

        # RES & FPS show
        cv2.putText(annotated_frame, f"Res: {width}x{height}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(annotated_frame, f"FPS: {int(fps)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow(window_name, annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    model = validate_model()
    if model is not None:
        detect_from_camera(model)