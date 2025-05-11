"""llm_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from intelligent import SimpleAi
from bot import SimpleBot
import math

# create the Robot instance.
robot = Robot()

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
wheel_radius = 0.02
wheel_speed = 1.0


def init():
    left_motor.setPosition(float("inf"))
    right_motor.setPosition(float("inf"))
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)


def stop():
    left_motor.setPosition(0)
    right_motor.setPosition(0)


def move_to_target(distance: float, speed: float, think_time: float = 0):
    time_to_travel = round(
        float(distance) / (wheel_speed * wheel_radius) + think_time, 2
    )
    print(f"time_to_travel: {time_to_travel}s")

    left_motor.setVelocity(speed)
    right_motor.setVelocity(speed)

    if robot.getTime() - start_time > time_to_travel:
        stop()


# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())


# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

start_time = robot.getTime()
loop = 0
running_action = False


def move_forward(distance: float, think_time: float = 0):
    move_to_target(distance, wheel_speed, think_time)
    global running_action
    running_action = False


def move_back(distance: float, think_time: float = 0):
    move_to_target(distance, -wheel_speed, think_time)
    global running_action
    running_action = False


init()

bot = SimpleBot(
    mv_fwd=move_forward,
    mv_back=move_back,
    turn_left=move_forward,
    turn_right=move_forward,
)
ai = SimpleAi(bot)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.
    if not running_action and loop % 300 == 0:
        print(f"\n======== loop: {loop} ========")
        start_time = robot.getTime()
        if loop > 0 and loop % 200 == 0:
            ai.think("向后移动 15 厘米")
        else:
            ai.think("向前移动 20 厘米")

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    loop += 1

# Enter here exit cleanup code.
