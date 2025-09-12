import time
from collections import deque

target_lost = False
gripper_closed = False
arm_lifted = False
latest_distance: float | None = None
gripper_status: str | None = None # opened / closed / normal

def arm_ctrl(ep_arm):
    """
    Controls the robot arm
    :param ep_arm: the object of the robot arm
    """
    global gripper_closed, arm_lifted

    last_gripper_state = False

    while not arm_lifted:
        if gripper_closed and not last_gripper_state and not arm_lifted:
            ep_arm.move(x = 50, y = 150).wait_for_completed()
            arm_lifted = True

        last_gripper_state = gripper_closed
        time.sleep(0.05)

def gripper_ctrl(ep_gripper):
    """
    Controls the robot gripper
    :param ep_gripper: the object of the robot gripper
    """
    global gripper_closed, target_lost

    ep_gripper.sub_status(freq = 5, callback = sub_data_handler_gripper)
    dist_queue = deque(maxlen = 10) # 连续帧记录

    while not gripper_closed:
        if target_lost:
            ep_gripper.open()
            time.sleep(0.1)
            continue

        if latest_distance is not None and latest_distance >= 13:
            dist_queue.append(latest_distance < 46)
            if len(dist_queue) == 10 and all(dist_queue): # 连续15帧距离数据都小于阈值时触发
                ep_gripper.close()
                timeout = 0
                while gripper_status != "closed" and timeout < 20:
                    time.sleep(0.1)
                    timeout += 1
                if gripper_status == "closed":
                    gripper_closed = True
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