import Lab.Final_Lab.src.robot.movement.gripper_ctrl as gc
import Lab.Final_Lab.src.robot.movement.chassis_ctrl as cc
import Lab.Final_Lab.src.robot.vision.marker_config as mc
import Lab.Final_Lab.src.robot.vision.video_capture as vc
import Lab.Final_Lab.src.robot.other.distance_sub as ds
import Lab.Final_Lab.src.robot.movement.arm_ctrl as ac

import time, threading

states = {
    "Robot_Init": 0,                # Initialize the robot
    "Start_Marker_Searching": 1,    # search the start marker
    "Object_Searching": 2,          # search objects under the start marker
    "Object_Approaching": 3,        # approach the object
    "Object_Grabbing": 4,           # grip the object
    "Object_Lifting": 5,            # lift the object
    "End_Marker_Searching": 6,      # search the end marker
    "Marker_Approaching": 7,        # approach the marker
    "Object_Lowering": 8,           # lower the object
    "Object_Releasing": 9,          # release the object
    "Object_Away": 10               # away from the object
}

def workflow(current_state, ep_chassis, ep_gripper, ep_arm):
    if current_state == states["Robot_Init"]:
        init_robot(ep_gripper, ep_arm)
        return states["Start_Marker_Searching"]

    elif current_state == states["Start_Marker_Searching"]:
        mc.target_info = "3"
        found = cc.search_marker(ep_chassis, "3")
        if found:
            return states["Object_Searching"]
        return states["Start_Marker_Searching"]

    elif current_state == states["Object_Searching"]:
        if mc.object_under_marker("3"):
            return states["Object_Approaching"]
        return states["Object_Searching"]

    elif current_state == states["Object_Approaching"]:
        if ds.target_closed_event.is_set():
            ds.target_closed_event.clear()
            ac.stop_aimed_event.set() # `停止机械臂对齐`事件设置
            return states["Object_Grabbing"]
        return states["Object_Approaching"]

    elif current_state == states["Object_Grabbing"]:
        gc.gripper_closed_event.clear()
        gc.gripper_ctrl(ep_gripper, "close")
        time.sleep(3)
        gc.gripper_closed_event.wait()
        return states["Object_Lifting"]

    elif current_state == states["Object_Lifting"]:
        ac.arm_lifted_event.clear()
        cc.chassis_stop(ep_chassis)
        ac.arm_ctrl(ep_arm, "lift")
        time.sleep(4)
        ac.arm_lifted_event.wait()
        return states["End_Marker_Searching"]

    elif current_state == states["End_Marker_Searching"]:
        mc.target_info = "heart"
        found = cc.search_marker(ep_chassis, "heart")
        if found:
            return states["Marker_Approaching"]
        return states["End_Marker_Searching"]

    elif current_state == states["Marker_Approaching"]:
        if cc.marker_closed_event.is_set():
            cc.marker_closed_event.clear()
            return states["Object_Lowering"]
        return states["Marker_Approaching"]

    elif current_state == states["Object_Lowering"]:
        ac.arm_lowered_event.clear()
        ac.arm_ctrl(ep_arm, "lower")
        time.sleep(4)
        ac.arm_lowered_event.wait()
        return states["Object_Releasing"]

    elif current_state == states["Object_Releasing"]:
        gc.gripper_opened_event.clear()
        gc.gripper_ctrl(ep_gripper, "open")
        time.sleep(3)
        gc.gripper_opened_event.wait()
        return states["Object_Away"]

    elif current_state == states["Object_Away"]:
        ep_chassis.move(x = -0.15, y = 0, xy_speed = 1).wait_for_completed() # 远离物体防止碰倒
        ep_arm.moveto(x = 180, y = 110) # 初始化机械臂状态 - 实测(x: 180, y: 110)视野广
        time.sleep(1)

        gc.gripper_closed_event.clear()
        gc.gripper_opened_event.clear()
        ac.arm_lifted_event.clear()
        ac.arm_lowered_event.clear()
        ds.target_closed_event.clear()
        ac.stop_aimed_event.clear()
        cc.marker_closed_event.clear()

        return states["Start_Marker_Searching"]

    return current_state

def action_ctrl(ep_chassis, ep_arm, ep_gripper):
    current_state = states["Start_Marker_Searching"]

    approach_threads_started = False
    marker_threads_started = False
    start_marker_thread_started = False

    init_robot(ep_gripper, ep_arm)

    while vc.running:
        if current_state != states["Object_Approaching"]:
            approach_threads_started = False
        if current_state != states["Marker_Approaching"]:
            marker_threads_started = False
        if current_state != states["Start_Marker_Searching"]:
            start_marker_thread_started = False

        if current_state == states["Start_Marker_Searching"]:
            mc.target_info = "3"
            if not start_marker_thread_started:
                cc.marker_closed_event.clear()
                threading.Thread(target = cc.chassis_ctrl, args = (ep_chassis, "marker")).start()
                start_marker_thread_started = True

            next_state = workflow(current_state, ep_chassis, ep_gripper, ep_arm)

        elif current_state == states["Object_Approaching"]:
            if not approach_threads_started:
                ds.target_closed_event.clear()
                ac.stop_aimed_event.clear()

                threading.Thread(
                    target = cc.chassis_ctrl, args = (ep_chassis, "object")
                ).start()
                threading.Thread(
                    target = ac.arm_ctrl, args = (ep_arm, "aim")
                ).start()

                approach_threads_started = True

            next_state = workflow(current_state, ep_chassis, ep_gripper, ep_arm)

        elif current_state == states["Marker_Approaching"]:
            if not marker_threads_started:
                cc.marker_closed_event.clear()

                threading.Thread(
                    target = cc.chassis_ctrl, args = (ep_chassis, "marker")
                ).start()

                marker_threads_started = True

            next_state = workflow(current_state, ep_chassis, ep_gripper, ep_arm)

        else:
            next_state = workflow(current_state, ep_chassis, ep_gripper, ep_arm)

        if next_state == states["Object_Away"]:
            approach_threads_started = False
            marker_threads_started = False
            start_marker_thread_started = False

        current_state = next_state
        time.sleep(0.1)

def init_robot(ep_gripper, ep_arm):
    """
    Initialize the robot
    :param ep_gripper: the object of the robot gripper
    :param ep_arm: the object of the robot arm
    """
    ds.target_closed_event.clear()
    ac.stop_aimed_event.clear()
    ac.arm_lifted_event.clear()
    ac.arm_lowered_event.clear()
    gc.gripper_closed_event.clear()
    gc.gripper_opened_event.clear()
    cc.marker_closed_event.clear()

    ep_gripper.open()  # 初始化机械爪状态 - 张开
    time.sleep(3)
    ep_arm.moveto(x = 180, y = 110).wait_for_completed()  # 初始化机械臂状态 - 实测(x: 180, y: 110)视野广