import time, threading

gripper_status: str | None = None # opened-张开; closed-闭合; normal-中间

gripper_closed_event = threading.Event() # 判断是否夹住物体
gripper_opened_event = threading.Event() # 判断是否松开物体

def gripper_ctrl(ep_gripper, status):
    """
    Controls the robot gripper
    :param ep_gripper: the object of the robot gripper
    :param status: closed / opened
    """
    ep_gripper.sub_status(freq = 20, callback = sub_data_handler_gripper)

    timeout = 0

    if status == "closed":
        ep_gripper.close()
        while gripper_status != "closed" and timeout < 20:
            time.sleep(0.1)
            timeout += 1
        if gripper_status == "closed":
            gripper_closed_event.set() # `抓住目标`事件设置

    elif status == "opened":
        ep_gripper.open()
        while gripper_status != "opened" and timeout < 20:
            time.sleep(0.1)
            timeout += 1
        if gripper_status == "opened":
            gripper_opened_event.set() # `松开目标`事件设置

def sub_data_handler_gripper(sub_info):
    """
    Callback function to receive the data from the gripper
    :param sub_info: the status of the gripper
    """
    global gripper_status
    gripper_status = sub_info