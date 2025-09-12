import time
import video_capture as vc
from collections import deque
from simple_pid import PID

pid_y = PID(0.2, 0.01, 0.05, setpoint = 180)
pid_y.output_limits = (-25, 25)

gripper_closed = False
lift_request = False
latest_distance: float | None = None
gripper_status: str | None = None    # opened-张开; closed-闭合; normal-中间

pos_x, pos_y = 0, 0
last_pos_x, last_pos_y = None, None
stable_counter = 0

def arm_ctrl(ep_arm):
    """
    Controls the robot arm
    :param ep_arm: the object of the robot arm
    """
    global pos_y, last_pos_y, gripper_closed, lift_request

    ep_arm.sub_position(freq = 5, callback = sub_data_handler_arm)

    previous_y = None
    offset = 360 // 10

    while True:
        if gripper_closed and lift_request:
            print("WTF!!! LIFT REQUEST DETECTED")
            ep_arm.move(y = 100).wait_for_completed()
            lift_request = False
            continue

        if not vc.running or vc.target_y is None:
            time.sleep(0.02)
            continue

        error_y = vc.target_y + offset
        y_move = pid_y(error_y)
        if abs(y_move) < 2: # 滤掉干扰
            y_move = 0

        if previous_y and abs(y_move - previous_y) <= 0.5:
                time.sleep(0.02)
                # continue

        ep_arm.move(y = y_move).wait_for_completed()

        previous_y = y_move
        last_pos_y = pos_y

        time.sleep(0.05)

def sub_data_handler_arm(sub_info):
    """
    Callback function to receive data from the arm sensor
    """
    global pos_x, pos_y
    pos_x, pos_y = sub_info

def gripper_ctrl(ep_gripper):
    """
    Controls the robot gripper
    :param ep_gripper: the object of the robot gripper
    """
    global gripper_closed, lift_request

    ep_gripper.sub_status(freq = 5, callback = sub_data_handler_gripper)
    dist_queue = deque(maxlen = 15) # 连续帧记录

    while not gripper_closed:
        if latest_distance is not None:
            in_grasp_range = 5 <= latest_distance <= 46
            dist_queue.append(in_grasp_range)

            if len(dist_queue) == 15 and all(dist_queue): # 连续15帧距离数据都小于阈值时触发
                ep_gripper.close()
                timeout = 0
                while gripper_status != "closed" and timeout < 20:
                    time.sleep(0.1)
                    timeout += 1
                if gripper_status == "closed":
                    gripper_closed = True
                    lift_request = True
                break

        time.sleep(0.05)

    while True:
        time.sleep(1)

def sub_data_handler_gripper(sub_info):
    """
    Callback function to receive the data from the gripper
    :param sub_info: the status of the gripper
    """
    global gripper_status
    gripper_status = sub_info

def get_distance(ep_sensor):
    """
    Subscribe the distance information from the distance sensor
    :param ep_sensor: the object of the distance sensor
    """
    ep_sensor.sub_distance(freq = 5, callback = sub_data_handler_distance)
    while True:
        time.sleep(0.1)

def sub_data_handler_distance(sub_info):
    """
    Callback function to receive the data from the distance sensor
    :param sub_info: the distance info from the distance sensor
    """
    global latest_distance
    latest_distance = sub_info[0]