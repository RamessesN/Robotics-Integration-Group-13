from Lab.Final_Lab.src.robot.env_import import *

pid_x = PID(0.3, 0, 0.03, setpoint = 0)  # (object) 居中
pid_x.output_limits = (-50, 50)

pid_z = PID(0.5, 0.1, 0.05, setpoint = 13) # (object) 靠近
pid_z.output_limits = (-40, 40)

pid_z_area = PID(0.5, 0, 0, setpoint = 13) # (marker) 靠近
pid_z_area.output_limits = (-40, 40)

object_closed_event = threading.Event() # 判断是否靠近物体
marker_closed_event = threading.Event() # 判断是否靠近marker

frame_width = 640
current_target: str | None = None

def chassis_ctrl(ep_chassis):
    """
    Control the Chassis to approach the Target
    :param ep_chassis: the object of the robot chassis
    """
    global current_target

    while vc.running:
        current_target = "object" if not ac.arm_lifted_event.is_set() else "marker"

        target_valid = False
        if current_target == "object":
            target_valid = vc.target_x is not None and vc.target_y is not None
        elif current_target == "marker":
            target_marker = mc.get_specified_marker(mc.target_info)
            target_valid = target_marker is not None

        if target_valid:
            pid_chassis(ep_chassis, current_target)
        else:
            chassis_stop(ep_chassis)

        time.sleep(0.02)

    chassis_stop(ep_chassis)

def pid_chassis(ep_chassis, status):
    """
    Chassis PID controller
    :param ep_chassis: the object of the robot chassis
    :param status: target (object / marker)
    """
    if status == "object":
        error_x = vc.target_x - (frame_width // 2)
        current_distance = ds.latest_distance
        distance = current_distance if current_distance is not None else 8848

        if distance <= 70:
            chassis_stop(ep_chassis)
            object_closed_event.set() # `靠近object`事件设置
            return

        if abs(error_x) < 40 and (10 < distance < 45):
            chassis_stop(ep_chassis)
        else:
            turn_speed = pid_x(error_x)
            forward_speed = -pid_z(distance)
            drive_chassis(ep_chassis, forward_speed, turn_speed)

    elif status == "marker":
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