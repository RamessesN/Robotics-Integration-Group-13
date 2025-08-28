import cv2
from obj_detect import validate_model
from env_config import DEVICE

def detect_from_video(model, video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open video file: {video_path}")
        return

    # Video config
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Video resolution: {width}x{height}, FPS: {fps}")

    win_name = "on Live"

    cv2.namedWindow(win_name, cv2.WINDOW_AUTOSIZE)

    screen_width = 1512
    screen_height = 982
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    cv2.moveWindow(win_name, int(x), int(y))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"Saving annotated video to: {output_path}")

    prev_time = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or cannot read frame.")
            break

        current_time = cv2.getTickCount()

        results = model.predict(frame, conf=0.25, device=DEVICE, verbose=False)
        annotated_frame = results[0].plot()

        fps_calc = cv2.getTickFrequency() / (current_time - prev_time)
        prev_time = current_time

        cv2.putText(annotated_frame, f"FPS: {int(fps_calc)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"Res: {width}x{height}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow(win_name, annotated_frame)
        out.write(annotated_frame)

        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"Finished processing {frame_count} frames.")
    print(f"Annotated video saved to: {output_path}")

if __name__ == "__main__":
    model = validate_model()
    if model is not None:
        detect_from_video(model, "./video/input_360p.mp4", "video/output_v3.mp4")