from collections import deque
import threading

latest_distance: float | None = None
target_closed_event = threading.Event() # 判断是否靠近物体
dist_queue = deque(maxlen = 10) # 连续帧记录

def get_distance(ep_sensor):
    """
    Subscribe the Distance Information from the Distance Sensor
    :param ep_sensor: the object of the distance sensor
    """
    ep_sensor.sub_distance(freq = 10, callback = sub_data_handler_distance)

def sub_data_handler_distance(sub_info):
    """
    Callback Function to Receive the Data from the Distance Sensor
    :param sub_info: the distance info from the distance sensor
    """
    global latest_distance
    latest_distance = sub_info[0]

    in_grasp_range = latest_distance <= 50
    dist_queue.append(in_grasp_range)

    if len(dist_queue) == 10 and all(dist_queue): # 连续10帧距离数据都小于阈值时触发
        target_closed_event.set() # `靠近目标`事件设置