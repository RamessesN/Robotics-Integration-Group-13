import time, threading
import video_capture as vc
import object_follow as of
from collections import deque
from simple_pid import PID

pid_y = PID(0.5, 0, 0.03, setpoint = 180)
pid_y.output_limits = (-50, 50)

gripper_closed_event = threading.Event() # 判断是否夹住物体
arm_lifted_event = threading.Event() # 判断是否抬起机械臂
arm_lowered_event = threading.Event() # 判断机械臂是否放下

latest_distance: float | None = None # 距离测量
gripper_status: str | None = None # opened-张开; closed-闭合; normal-中间

pos_x, pos_y = 0, 0
last_pos_x = None
stable_counter = 0

def arm_ctrl(ep_arm):
    """
    Controls the robot arm
    :param ep_arm: the object of the robot arm
    """
    global pos_x, pos_y

    ep_arm.sub_position(freq = 20, callback = sub_data_handler_arm)

    previous_y = None
    offset = 360 // 5 # 抓取位置修正

    while not gripper_closed_event.is_set():
        if vc.running and vc.target_y is not None:
            error_y = vc.target_y - offset # 上负下正
            y_move = pid_y(error_y)
            if abs(y_move) < 2: # 滤掉干扰
                y_move = 0

            if previous_y and abs(y_move - previous_y) <= 0.5:
                time.sleep(0.02)
                continue

            x_move = max(200, pos_x) # 保证横向机械臂不会碰到前壳
            ep_arm.move(x = x_move, y = y_move)

            previous_y = y_move

        time.sleep(0.05)

    ep_arm.moveto(x = 170, y = 150)
    time.sleep(2)
    arm_lifted_event.set()

    of.marker_closed_event.wait() # 等待标签靠近

    ep_arm.moveto(x = 190, y = 10)
    time.sleep(1)
    arm_lowered_event.set()

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
    global gripper_closed_event

    ep_gripper.sub_status(freq = 20, callback = sub_data_handler_gripper)
    dist_queue = deque(maxlen = 15) # 连续帧记录

    while not gripper_closed_event.is_set():
        if latest_distance is not None:
            in_grasp_range = latest_distance <= 50
            dist_queue.append(in_grasp_range)

            if len(dist_queue) == 15 and all(dist_queue): # 连续15帧距离数据都小于阈值时触发
                ep_gripper.close()
                time.sleep(3)
                timeout = 0

                while gripper_status != "closed" and timeout < 20:
                    time.sleep(0.1)
                    timeout += 1

                if gripper_status == "closed":
                    gripper_closed_event.set()
                    break

        time.sleep(0.05)

    arm_lowered_event.wait() # 等待机械臂放下
    ep_gripper.open()
    time.sleep(3)

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
    ep_sensor.sub_distance(freq = 20, callback = sub_data_handler_distance)
    while True:
        time.sleep(0.1)

def sub_data_handler_distance(sub_info):
    """
    Callback function to receive the data from the distance sensor
    :param sub_info: the distance info from the distance sensor
    """
    global latest_distance
    latest_distance = sub_info[0]