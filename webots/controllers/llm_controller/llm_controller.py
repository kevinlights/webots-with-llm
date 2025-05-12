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

MAX_SPEED = 6.28

wheel_speed = 0.5 * MAX_SPEED
wheel_rotate_speed = 0.5 * MAX_SPEED
wheel_radius = 0.0205  # 轮子半径 (m)
axle_length = 0.052  # 轴距 (m)


# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())


left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
gyro = robot.getDevice("gyro")
ps_list = []
ps_names = [
    "ps0",
    "ps1",
    "ps2",
    "ps3",
    "ps4",
    "ps5",
    "ps6",
    "ps7",
]


def init():
    left_motor.setPosition(float("inf"))
    right_motor.setPosition(float("inf"))
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)
    gyro.enable(timestep)
    for name in ps_names:
        d = robot.getDevice(name)
        ps_list.append(d)
        d.enable(timestep)


def calculate_rotation_time(degrees, speed):

    # 将输入的角度转换为弧度
    theta_body = math.radians(degrees)

    # 计算机器人的旋转速度 (原地旋转时，两轮速度相反)
    # ω_body = (r * (ω_right - ω_left)) / L
    # 原地旋转时，ω_right = +wheel_speed, ω_left = -wheel_speed
    omega_body = (wheel_radius * abs(speed) * 2) / axle_length

    # 计算所需时间: t = θ_body / ω_body
    rotation_time = theta_body / omega_body

    return rotation_time


def rotate(angle: float, speed: float):
    time_to_rotate = round(
        calculate_rotation_time(float(angle), speed), 2
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
    return rotate(angle, wheel_rotate_speed)


def turn_right(angle: float):
    log.info(f"turn_right: {angle}")
    return rotate(angle, -wheel_rotate_speed)


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


# actions = ai.think_chain("正前方有障碍物")
# task_processor.add_batch(actions)

# action = ai.think("向前移动 20 厘米")
# task_processor.add_task(action)

thinking = False

def on_task_completed():
    global thinking
    thinking = False

while robot.step(timestep) != -1:
    # log.debug("main loop is running...")
    try:
        ps_values = []
        found_obstacle = False
        for ps in ps_list:
            v = ps.getValue()
            ps_values.append(v)
            if v > 80.0:
                found_obstacle = True

        if not thinking and found_obstacle:
            thinking = True
            log.info(f"found obstacle: {ps_values}")
            action = ai.drive(",".join([str(num) for num in ps_values]))
            log.info(action)
            task_processor.add_task(action, on_task_completed)
    except Exception as e:
        log.error(f"failed to run main loop: {e}")

    time.sleep(1)
    # if random.random() < 0.1:
    #     action = ai.think("向前移动 20 厘米")
    #     task_processor.add_task(action)
    # log.debug(f"added new task: {action}")

task_processor.stop_processing()
processor_thread.join()
