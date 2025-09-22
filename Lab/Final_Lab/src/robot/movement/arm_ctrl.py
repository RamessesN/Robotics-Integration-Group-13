import Lab.Final_Lab.src.robot.vision.video_capture as vc

from simple_pid import PID
import time, threading

pid_y = PID(0.5, 0, 0.03, setpoint = 180)
pid_y.output_limits = (-50, 50)

arm_lifted_event = threading.Event()  # 判断是否抬起机械臂
arm_lowered_event = threading.Event() # 判断机械臂是否放下

stop_aimed_event = threading.Event()  # 判断停止机械臂对齐

pos_x, pos_y = 0, 0

def arm_ctrl(ep_arm, status):
    """
    Control the Robot Arm to lift or lower
    :param ep_arm: the object of the robot arm
    :param status: lifted / lowerer
    """
    global pos_x, pos_y

    ep_arm.sub_position(freq = 20, callback = sub_data_handler_arm)

    if status == "aim":
        stop_aimed_event.clear()
        previous_y = None
        offset = 360 // 5  # 抓取位置修正

        while not stop_aimed_event.is_set():
            if vc.target_x is not None and vc.target_y is not None:
                error_y = vc.target_y - offset  # 上负下正
                y_move = pid_y(error_y)
                if abs(y_move) < 2:  # 滤掉干扰
                    y_move = 0

                if previous_y and abs(y_move - previous_y) <= 0.5:
                    time.sleep(0.02)
                    continue

                x_move = max(200, pos_x)  # 保证横向机械臂不会碰到前壳
                ep_arm.move(x = x_move, y = y_move)
                previous_y = y_move

            time.sleep(0.05)

    elif status == "lift":
        ep_arm.moveto(y = 160)
        time.sleep(2)
        arm_lifted_event.set() # `抬起机械臂`事件设置

    elif status == "lower":
        ep_arm.moveto(x = 190, y = 15)
        time.sleep(2)
        arm_lowered_event.set() # `降下机械臂`事件设置

def sub_data_handler_arm(sub_info):
    """
    Callback Function to Receive Data from the Arm Sensor
    """
    global pos_x, pos_y
    pos_x, pos_y = sub_info