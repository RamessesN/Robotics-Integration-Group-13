from robomaster_ultra import robot
from env_import import *

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

    ep_gripper.open() # 初始化机械爪状态 - 张开
    time.sleep(3)
    ep_arm.moveto(x = 180, y = 110).wait_for_completed()  # 初始化机械臂状态 - 实测(x: 180, y: 110)视野广

    vc.running = True

    threading.Thread(  # 帧采集在子线程1
        target = vc.video_capture, args = (ep_camera, ep_vision), daemon = True
    ).start()

    threading.Thread(  # 机械臂瞄准控制在子线程2
        target = ac.arm_aim, args = (ep_arm,), daemon = True
    ).start()

    threading.Thread( # 机械臂升降控制在子线程3
        target = ac.arm_ctrl, args = (ep_arm,), daemon = True
    ).start()

    threading.Thread( # 机械爪控制在子线程4
        target = gc.gripper_ctrl, args = (ep_gripper,), daemon = True
    ).start()

    threading.Thread( # 底盘运动控制在子线程5
        target = cc.chassis_ctrl, args = (ep_chassis,), daemon = True
    ).start()

    threading.Thread( # 距离传感在子线程6
        target = ds.get_distance, args = (ep_sensor,), daemon = True
    ).start()

    threading.Thread( # 运行流程workflow在子线程7
        target = wf.workflow, daemon = True
    ).start()

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    cv2.moveWindow(window_name, (screen_width - 640) // 2, (screen_height - 360) // 2) # 画面居中

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

if __name__ == "__main__":
    main()