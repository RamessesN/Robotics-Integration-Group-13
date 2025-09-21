from robomaster_ultra import robot
import cv2, time, threading

import Lab.Final_Lab.src.robot.vision.video_capture as vc
import Lab.Final_Lab.src.robot.other.distance_sub as ds
import Lab.Final_Lab.src.robot.workflow as wf

window_name = "on Live"
screen_width = 1512
screen_height = 982

def main():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type = "ap")

    ep_camera = ep_robot.camera
    ep_arm = ep_robot.robotic_arm
    ep_gripper = ep_robot.gripper
    ep_sensor = ep_robot.sensor
    ep_chassis = ep_robot.chassis
    ep_vision = ep_robot.vision

    Thread1 = threading.Thread( # 视频采集在子线程1
        target = vc.video_capture, args = (ep_camera, ep_vision), daemon = True
    )
    Thread1.start()

    Thread2 = threading.Thread( # 距离传感线程在子线程2
        target = ds.get_distance, args = (ep_sensor,), daemon = True
    )
    Thread2.start()

    Thread3 = threading.Thread( # 动作控制线程在子线程3
        target = wf.action_ctrl, args = (ep_chassis, ep_arm, ep_gripper,), daemon = True
    )
    Thread3.start()

    vc.running = True
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(window_name, (screen_width - 640) // 2, (screen_height - 360) // 2) # 画面居中

    while True: # 视频流画面显示在主线程
        if vc.annotated_frame is not None:
            cv2.imshow(window_name, vc.annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            ep_gripper.open()
            time.sleep(3)
            break

    # 资源释放
    vc.running = False
    Thread3.join()

    ep_camera.stop_video_stream()
    ep_gripper.unsub_status()
    ep_robot.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()