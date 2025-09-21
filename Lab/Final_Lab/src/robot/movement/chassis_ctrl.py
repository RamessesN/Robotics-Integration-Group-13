import Lab.Final_Lab.src.robot.vision.video_capture as vc
import Lab.Final_Lab.src.robot.vision.marker_config as mc
import Lab.Final_Lab.src.robot.other.distance_sub as ds

from simple_pid import PID
import time, threading

pid_x = PID(0.3, 0, 0.03, setpoint = 0)  # (object) 居中
pid_x.output_limits = (-50, 50)

pid_z = PID(0.5, 0.1, 0.05, setpoint = 13) # (object) 靠近
pid_z.output_limits = (-40, 40)

pid_z_area = PID(0.5, 0, 0, setpoint = 13) # (marker) 靠近
pid_z_area.output_limits = (-40, 40)

marker_closed_event = threading.Event() # 判断是否靠近marker

frame_width = 640

def chassis_ctrl(ep_chassis, current_target: str | None = None):
    """
    Control the Chassis to approach the Target
    :param ep_chassis: the object of the robot chassis
    :param current_target: target (object / marker)
    """
    while True:
        target_valid = False

        if current_target == "object":
            if ds.target_closed_event.is_set(): # 如果已经靠近了物体
                break
            target_valid = vc.target_x is not None and vc.target_y is not None
        elif current_target == "marker":
            if marker_closed_event.is_set(): # 如果已经靠近了marker
                break
            target_marker = mc.get_specified_marker(mc.target_info)
            target_valid = target_marker is not None

        if target_valid:
            pid_chassis(ep_chassis, current_target)
        else:
            chassis_stop(ep_chassis)

        time.sleep(0.02)

    chassis_stop(ep_chassis)

def pid_chassis(ep_chassis, target: str | None = None):
    """
    Chassis PID controller
    :param ep_chassis: the object of the robot chassis
    :param target: target (object / marker)
    """
    if target == "object":
        error_x = vc.target_x - (frame_width // 2)
        current_distance = ds.latest_distance
        distance = current_distance if current_distance is not None else 8848

        if distance <= 65:
            chassis_stop(ep_chassis)
            return

        if abs(error_x) < 40 and (10 < distance < 45):
            chassis_stop(ep_chassis)
        else:
            turn_speed = pid_x(error_x)
            forward_speed = -pid_z(distance)
            drive_chassis(ep_chassis, forward_speed, turn_speed)

    elif target == "marker":
        target_marker = mc.get_specified_marker(mc.target_info)

        center_x, center_y = target_marker.center
        marker_area = target_marker.area

        error_x = center_x - (frame_width // 2)

        if abs(error_x) < 20 and marker_area >= 12000: # 面积12000时停止合适
            chassis_stop(ep_chassis)
            marker_closed_event.set() # `靠近marker`事件设置
        else:
            turn_speed = pid_x(error_x)
            forward_speed = max(-pid_z_area(marker_area), 0)
            drive_chassis(ep_chassis, forward_speed, turn_speed)

def search_marker(ep_chassis, target: str | None = None):
    """
    Search the specified marker
    :param ep_chassis: the object of the robot chassis
    :param target: the target marker
    :return: whether the specified marker is found
    """
    rotate_speed = 35
    rotated_angle = 0
    counter = 0

    while rotated_angle < 720:
        marker = mc.get_specified_marker(target)
        if marker:
            counter += 1
            center_x, _ = marker.center
            if center_x < 150:
                ep_chassis.drive_wheels(w1 = -10, w2 = 10, w3 = 10, w4 = -10)
            elif center_x > 490:
                ep_chassis.drive_wheels(w1 = 10, w2 = -10, w3 = -10, w4 = 10)
            else:
                ep_chassis.drive_wheels(w1 = 0, w2 = 0, w3 = 0, w4 = 0)
        else:
            counter = 0
            ep_chassis.drive_wheels(w1 = rotate_speed, w2 = -rotate_speed, w3 = -rotate_speed, w4 = rotate_speed)

        if counter >= 3:
            ep_chassis.drive_wheels(w1 = 0, w2 = 0, w3 = 0, w4 = 0)
            return True

        time.sleep(0.05)
        rotated_angle += rotate_speed * 0.05

    ep_chassis.drive_wheels(w1 = 0, w2 = 0, w3 = 0, w4 = 0)

    return False

def chassis_stop(ep_chassis):
    """
    Full Stop the Robot
    :param ep_chassis: the object of the robot chassis
    """
    ep_chassis.drive_wheels(w1 = 0, w2 = 0, w3 = 0, w4 = 0)
    time.sleep(0.02)

def drive_chassis(ep_chassis, forward_speed, turn_speed):
    """
    Mecanum Wheel Control System based on PID
    :param ep_chassis: the object of the chassis
    :param forward_speed: the forward speed of the chassis
    :param turn_speed: the turn speed of the chassis
    """
    left_speed = forward_speed - turn_speed
    right_speed = forward_speed + turn_speed

    ep_chassis.drive_wheels(
        w1 = right_speed, # 右前
        w2 = left_speed,  # 左前
        w3 = left_speed,  # 右后
        w4 = right_speed  # 左后
    )