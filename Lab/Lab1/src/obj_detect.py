import cv2
from ultralytics import YOLO
from env_config import MOUSE_DATA_YAML, MOUSE_BEST_MODEL_PATH, DEVICE

def validate_model():
    print("Checking model Performance...")
    model = YOLO(MOUSE_BEST_MODEL_PATH)
    metrics = model.val(data = MOUSE_DATA_YAML, device = DEVICE)
    print(f"Results: mAP50: {metrics.box.map50:.3f}, mAP50-95: {metrics.box.map:.3f}")
    return model

def detect_from_camera(model):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera open failed")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Read frames failed")
            break

        results = model.predict(frame, conf = 0.25, device = DEVICE, verbose = False)
        annotated_frame = results[0].plot()

        cv2.imshow("on Live", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    model = validate_model()
    if model is not None:
        detect_from_camera(model)