import time
import action_ctrl as ac
import video_capture as vc
from simple_pid import PID

pid_x = PID(0.5, 0.01, 0.1, setpoint=0)
pid_x.output_limits = (-50, 50)

pid_z = PID(0.5, 0.1, 0.05, setpoint=13)
pid_z.output_limits = (-45, 45)

def chassis_ctrl(ep_chassis, ep_arm):
    state = "TRACKING" # TRACKING / LOST
    lost_target_count = 0

    while vc.running:
        if ac.gripper_closed:
            chassis_stop(ep_chassis)
            time.sleep(0.1)
            continue

        if vc.target_x is not None:
            lost_target_count = 0
            if state == "LOST":
                state = "TRACKING"
                ac.target_lost = False
        else:
            lost_target_count += 1
            if not ac.gripper_closed:
                if lost_target_count > 5 and state == "TRACKING":
                    state = "LOST"
                    ac.target_lost = True

        if state == "TRACKING":
            if vc.target_x is None:
                chassis_stop(ep_chassis)
                time.sleep(0.01)
                continue

            frame_width = 640
            error_x = vc.target_x - (frame_width // 2)
            current_distance = ac.latest_distance
            distance = current_distance if current_distance is not None else 8848

            if abs(error_x) < 40 and (10 < distance < 45):
                chassis_stop(ep_chassis)
            else:
                turn_speed = pid_x(error_x)
                forward_speed = -pid_z(distance)

                left_speed = forward_speed - turn_speed
                right_speed = forward_speed + turn_speed

                w1 = right_speed  # 右前
                w2 = left_speed   # 左前
                w3 = right_speed  # 右后
                w4 = left_speed   # 左后

                ep_chassis.drive_wheels(w1, w2, w3, w4)

        elif state == "LOST":
            chassis_stop(ep_chassis)

            if lost_target_count == 10:
                ep_arm.move(x = 30, y = 150).wait_for_completed()

        time.sleep(0.02)

    chassis_stop(ep_chassis)

def chassis_stop(ep_chassis):
    ep_chassis.drive_wheels(w1 = 0, w2 = 0, w3 = 0, w4 = 0)