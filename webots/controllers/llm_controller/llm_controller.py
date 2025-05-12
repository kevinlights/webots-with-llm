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


def rotate(angle: float, speed: float):
    time_to_rotate = round(float(angle) * math.pi / 180 * wheel_radius / abs(speed), 2)
    print(f"time_to_rotate: {time_to_rotate}s")
    left_motor.setVelocity(-speed)
    right_motor.setVelocity(speed)
    return time_to_rotate


def move_to_target(distance: float, speed: float):
    time_to_travel = round(float(distance) / (abs(speed) * wheel_radius), 2)
    print(f"time_to_travel: {time_to_travel}s")

    left_motor.setVelocity(speed)
    right_motor.setVelocity(speed)

    return time_to_travel


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


def move_forward(distance: float):
    print(f"move_forward: {distance}")
    return move_to_target(distance, wheel_speed)


def move_back(distance: float):
    print(f"move_back: {distance}")
    return move_to_target(distance, -wheel_speed)


def turn_left(angle: float):
    print(f"turn_left: {angle}")
    return rotate(angle, wheel_speed)


def turn_right(angle: float):
    print(f"turn_right: {angle}")
    return rotate(angle, -wheel_speed)


def stop():
    left_motor.setPosition(0)
    right_motor.setPosition(0)
    global running_action
    running_action = False
    # print("======== finished action ========")


init()

bot = SimpleBot(
    mv_fwd=move_forward,
    mv_back=move_back,
    turn_left=turn_left,
    turn_right=turn_right,
)
ai = SimpleAi(bot)

spend_time = 0


# Main loop:
# - perform simulation steps until Webots is stopping the controller
# while robot.step(timestep) != -1:
#     # Read the sensors:
#     # Enter here functions to read sensor data, like:
#     #  val = ds.getValue()

#     # Process sensor data here.
#     if not running_action:
#         if loop > 0 and loop % 200 == 0:
#             print(f"\n======== loop: {loop} ========")
#             # actions = ai.think_chain("正前方有障碍物")
#             # running_action = True
#             # start_time = robot.getTime()
#             # spend_time = ai._handle_action_chain(actions)
#             # new thread and loop?
#         elif loop % 300 == 0:
#             print(f"\n======== loop: {loop} ========")
#             action = ai.think("向前移动 20 厘米")
#             running_action = True
#             start_time = robot.getTime()
#             spend_time = ai._handle_action(action)
#     if robot.getTime() - start_time > spend_time:
#         stop()

#     # Enter here functions to send actuator commands, like:
#     #  motor.setPosition(10.0)
#     loop += 1

# # Enter here exit cleanup code.

from task import SimpleTask
import threading
import time
import random
from log import SimpleLog

task_processor = SimpleTask(timestep)
processor_thread = threading.Thread(
    name="task",
    target=task_processor.process_tasks,
    args=(robot,),
)
processor_thread.daemon = True
processor_thread.start()

threading.current_thread().name = "main"

log = SimpleLog()

actions = ai.think_chain("正前方有障碍物")
task_processor.add_batch(actions)
while robot.step(timestep) != -1:
    log.debug("main loop is running...")
    time.sleep(1)
    if random.random() < 0.1:
        action = ai.think("向前移动 20 厘米")
        task_processor.add_task(action)
        log.debug(f"added new task: {action}")

task_processor.stop_processing()
processor_thread.join()
