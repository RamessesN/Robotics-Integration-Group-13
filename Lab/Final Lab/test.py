import time
from robomaster_ultra import robot
from robomaster_ultra import led

def robot_connect(ep_robot):
    ep_robot.initialize(conn_type = "ap")

def version_print(ep_robot):
    version = ep_robot.get_version()
    print("Robot version: {0}".format(version))

def led_config(ep_robot):
    ep_led = ep_robot.led
    ep_led.set_led(
        comp = led.COMP_ALL,
        r = 255,
        g = 255,
        b = 0,
        effect = led.EFFECT_ON
    )

def move_config(ep_robot):
    ep_chassis = ep_robot.chassis
    ep_chassis.drive_speed(
        x = 0.5,
        y = 0,
        z = 0,
        timeout = 5
    )


if __name__ == '__main__':
    ep_robot = robot.Robot()
    robot_connect(ep_robot)

    ep_robot.set_robot_mode(mode = robot.CHASSIS_LEAD)

    version_print(ep_robot)
    led_config(ep_robot)
    move_config(ep_robot)

    time.sleep(3)

    ep_robot.close()