"""llm_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from intelligent import SimpleAi
from bot import SimpleBot
import math
from task import SimpleTask
import threading
import time
from log import SimpleLog

# create the Robot instance.
robot = Robot()
log = SimpleLog()

wheel_speed = 1.0

wheel_radius = 0.02
wheel_diameter = wheel_radius * 2
wheel_base = 0.052  # 轮距，单位：米
wheel_circumference = wheel_diameter * math.pi  # 轮子周长

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())


left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
gyro = robot.getDevice("gyro")
gyro.enable(timestep)


def init():
    left_motor.setPosition(float("inf"))
    right_motor.setPosition(float("inf"))
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)


def rotate(angle: float, speed: float):
    rotation_radius = wheel_base / 2  # 旋转半径
    rotation_distance = (float(angle) * math.pi / 180) * rotation_radius  # 弧长
    # 计算旋转时间
    # 注意：这里我们假设左右轮速度差为10，因为left_motor速度为-5，right_motor速度为5
    time_to_rotate = round(
        rotation_distance / (wheel_circumference * 2 * abs(speed)), 2
    )  # 旋转时间，单位：秒
    log.info(f"time_to_rotate: {time_to_rotate}s")
    start = time.time()
    while robot.step(timestep) != -1:
        left_motor.setVelocity(-speed)
        right_motor.setVelocity(speed)
        if time.time() - start > time_to_rotate:
            log.debug(f"completed rotate {angle} \t {speed}")
            break
    return time_to_rotate


def move_to_target(distance: float, speed: float):
    time_to_travel = round(float(distance) / (abs(speed) * wheel_radius), 2)
    log.info(f"time_to_travel: {time_to_travel}s")

    start = time.time()
    while robot.step(timestep) != -1:
        left_motor.setVelocity(speed)
        right_motor.setVelocity(speed)
        if time.time() - start > time_to_travel:
            log.debug(f"completed move {distance} \t {speed}")
            break

    return time_to_travel


def move_forward(distance: float):
    log.info(f"move_forward: {distance}")
    return move_to_target(distance, wheel_speed)


def move_back(distance: float):
    log.info(f"move_back: {distance}")
    return move_to_target(distance, -wheel_speed)


def turn_left(angle: float):
    log.info(f"turn_left: {angle}")
    return rotate(angle, wheel_speed)


def turn_right(angle: float):
    log.info(f"turn_right: {angle}")
    return rotate(angle, -wheel_speed)


def stop():
    left_motor.setVelocity(0)
    right_motor.setVelocity(0)


init()

bot = SimpleBot(
    mv_fwd=move_forward,
    mv_back=move_back,
    turn_left=turn_left,
    turn_right=turn_right,
    stop=stop,
)
ai = SimpleAi(bot)

task_processor = SimpleTask(ai, timestep)
processor_thread = threading.Thread(
    name="task",
    target=task_processor.process_tasks,
    args=(robot,),
)
processor_thread.daemon = True
processor_thread.start()

threading.current_thread().name = "main"


actions = ai.think_chain("正前方有障碍物")
task_processor.add_batch(actions)

# action = ai.think("向前移动 20 厘米")
# task_processor.add_task(action)

while robot.step(timestep) != -1:
    # log.debug("main loop is running...")
    time.sleep(1)
    # if random.random() < 0.1:
    #     action = ai.think("向前移动 20 厘米")
    #     task_processor.add_task(action)
    # log.debug(f"added new task: {action}")

task_processor.stop_processing()
processor_thread.join()
