import time
import action_ctrl as ac
import video_capture as vc
import marker_config as mc
from simple_pid import PID

pid_x = PID(0.3, 0, 0.03, setpoint = 0)  # (object) 居中
pid_x.output_limits = (-50, 50)

pid_z = PID(0.5, 0.1, 0.05, setpoint = 13) # (object) 靠近
pid_z.output_limits = (-40, 40)

pid_z_area = PID(1, 0, 0, setpoint = 50000) # (marker) 靠近
pid_z_area.output_limits = (-40, 40)

frame_width = 640
current_target = "object"

def chassis_ctrl(ep_chassis):
    global current_target
    while vc.running:
        if not ac.arm_lifted_event.is_set():
            current_target = "object"
            if vc.target_x is not None and vc.target_y is not None:
                pid_chassis(ep_chassis, current_target)
            else:
                chassis_stop(ep_chassis)
            time.sleep(0.02)
            continue
        else:
            current_target = "marker"
            if mc.closest_marker is not None:
                pid_chassis(ep_chassis, current_target)
            else:
                chassis_stop(ep_chassis)

        time.sleep(0.02)

    chassis_stop(ep_chassis)

def pid_chassis(ep_chassis, status):
    if status == "object":
        if vc.target_x is None and vc.target_y is None:
            chassis_stop(ep_chassis)
            return

        error_x = vc.target_x - (frame_width // 2)
        current_distance = ac.latest_distance
        distance = current_distance if current_distance is not None else 8848

        if distance <= 70:
            chassis_stop(ep_chassis)
            return

        if abs(error_x) < 40 and (10 < distance < 45):
            chassis_stop(ep_chassis)
        else:
            turn_speed = pid_x(error_x)
            forward_speed = -pid_z(distance)
            drive_chassis(ep_chassis, forward_speed, turn_speed)

    elif status == "marker":
        if mc.closest_marker is None:
            chassis_stop(ep_chassis)
            return

        center_x, center_y = mc.closest_marker.center
        marker_area = mc.closest_marker.area

        error_x = center_x - (frame_width // 2)
        turn_speed = pid_x(error_x)
        forward_speed = -pid_z_area(marker_area)

        if abs(error_x) < 20 and marker_area >= 50000:
            chassis_stop(ep_chassis)
            return

        drive_chassis(ep_chassis, forward_speed, turn_speed)

    else:
        chassis_stop(ep_chassis)

def chassis_stop(ep_chassis):
    ep_chassis.drive_wheels(w1 = 0, w2 = 0, w3 = 0, w4 = 0)
    time.sleep(0.02)

def drive_chassis(ep_chassis, forward_speed, turn_speed):
    left_speed = forward_speed - turn_speed
    right_speed = forward_speed + turn_speed

    ep_chassis.drive_wheels(
        w1 = right_speed, # 右前
        w2 = left_speed,  # 左前
        w3 = left_speed,  # 右后
        w4 = right_speed  # 左后
    )