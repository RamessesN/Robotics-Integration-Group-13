import threading, cv2

from object_follow import *
from robomaster_ultra import robot

window_name = "on Live"

def main():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type = "ap")

    ep_camera = ep_robot.camera
    ep_arm = ep_robot.robotic_arm
    ep_gripper = ep_robot.gripper
    ep_sensor = ep_robot.sensor
    ep_chassis = ep_robot.chassis

    ep_gripper.open() # 机械爪初始化：张开
    time.sleep(3)

    vc.running = True

    thread1 = threading.Thread( # 帧采集在子线程1
        target = vc.video_capture, args = (ep_camera,), daemon = True
    )
    thread1.start()

    thread2 = threading.Thread( # 底盘运动控制在子线程2
        target = chassis_ctrl, args = (ep_chassis,), daemon = True
    )
    thread2.start()

    thread3 = threading.Thread( # 机械臂控制在子线程3
        target = ac.arm_ctrl, args = (ep_arm,), daemon = True
    )
    thread3.start()

    thread4 = threading.Thread( # 机械爪控制在子线程4
        target = ac.gripper_ctrl, args = (ep_gripper,), daemon = True
    )
    thread4.start()

    thread5 = threading.Thread( # 距离传感在子线程5
        target = ac.get_distance, args = (ep_sensor,), daemon = True
    )
    thread5.start()

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    window_central(1920, 1080) # 画面居中

    while True:  # 视频流画面显示在主线程
        if vc.annotated_frame is not None:
           cv2.imshow(window_name, vc.annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            ep_gripper.open()
            time.sleep(3)
            break

    vc.running = False
    time.sleep(0.5)

    ep_camera.stop_video_stream()
    ep_gripper.unsub_status()
    ep_robot.close()
    cv2.destroyAllWindows()

def window_central(screen_width, screen_height):
    cv2.moveWindow(window_name, (screen_width - 640) // 2, (screen_height - 360) // 2)

if __name__ == '__main__':
    main()