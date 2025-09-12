import time
import action_ctrl as ac
import video_capture as vc
from simple_pid import PID

pid_x = PID(0.4, 0.01, 0.1, setpoint = 0)  # 居中
pid_x.output_limits = (-50, 50)

pid_z = PID(0.5, 0.1, 0.05, setpoint = 13) # 靠近
pid_z.output_limits = (-40, 40)

def chassis_ctrl(ep_chassis):
    while vc.running:
        if ac.gripper_closed:
            chassis_stop(ep_chassis)
            time.sleep(0.1)
            continue

        if vc.target_x is not None:
            pid_chassis(ep_chassis)
        else:
            chassis_stop(ep_chassis)

        time.sleep(0.02)

    chassis_stop(ep_chassis)

def pid_chassis(ep_chassis):
    frame_width = 640
    error_x = vc.target_x - (frame_width // 2)
    current_distance = ac.latest_distance
    distance = current_distance if current_distance is not None else 8848

    if 10 < distance <= 55:
        chassis_stop(ep_chassis)
        return

    if abs(error_x) < 40 and (10 < distance < 45):
        chassis_stop(ep_chassis)
    else:
        turn_speed = pid_x(error_x)
        forward_speed = -pid_z(distance)
        drive_chassis(ep_chassis, forward_speed, turn_speed)

def chassis_stop(ep_chassis):
    ep_chassis.drive_wheels(w1 = 0, w2 = 0, w3 = 0, w4 = 0)

def drive_chassis(ep_chassis, forward_speed, turn_speed):
    left_speed = forward_speed - turn_speed
    right_speed = forward_speed + turn_speed

    ep_chassis.drive_wheels(
        w1 = right_speed, # 右前
        w2 = left_speed,  # 左前
        w3 = left_speed,  # 右后
        w4 = right_speed  # 左后
    )