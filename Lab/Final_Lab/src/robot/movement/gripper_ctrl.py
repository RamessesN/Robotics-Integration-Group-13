import time, threading

gripper_status: str | None = None # opened-张开; closed-闭合; normal-中间

gripper_closed_event = threading.Event() # 判断是否夹住物体
gripper_opened_event = threading.Event() # 判断是否松开物体

def gripper_ctrl(ep_gripper, status):
    """
    Controls the Robot Gripper
    :param ep_gripper: the object of the robot gripper
    :param status: closed / opened
    """
    ep_gripper.sub_status(freq = 10, callback = sub_data_handler_gripper)
    time.sleep(0.05)

    global gripper_status

    if status == "close":
        gripper_closed_event.clear()
        ep_gripper.close()
        previous_time = time.time()
        while gripper_status != "closed":
            if time.time() - previous_time >= 6:
                break
            time.sleep(0.01)
        gripper_closed_event.set() # `抓住目标`事件设置

    elif status == "open":
        gripper_opened_event.clear()
        ep_gripper.open()
        previous_time = time.time()
        while gripper_status != "opened":
            if time.time() - previous_time >= 6:
                break
            time.sleep(0.01)
        gripper_opened_event.set() # `松开目标`事件设置

def sub_data_handler_gripper(sub_info):
    """
    Callback Function to Receive the Data from the Gripper Sensor
    :param sub_info: the status of the gripper
    """
    global gripper_status
    gripper_status = sub_info