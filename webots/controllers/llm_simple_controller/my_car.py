from controller import Robot
import json
import time
import math
from utils import function_to_tool
from functools import partial


class MyRobot:
    def __init__(self, robot: Robot):
        self.webot = robot

    def handle_task(self, task):
        pass

    def stop(self):
        pass


class MyCar(MyRobot):
    def __init__(self, log):
        self.log = log
        self.robot = Robot()

        super().__init__(self.robot)

        self.left_motor = self.robot.getDevice("left wheel motor")
        self.right_motor = self.robot.getDevice("right wheel motor")
        self.gyro = self.robot.getDevice("gyro")
        self.max_speed = 6.28
        self.wheel_speed = 0.5 * self.max_speed
        self.wheel_rotate_speed = 0.5 * self.max_speed
        self.wheel_radius = 0.0205  # 轮子半径 (m)
        self.axle_length = 0.052  # 轴距 (m)
        self.obstacle_threshold = 100
        self.ps_objs = {}
        # 依次从右前方到左前方
        self.ps_names = {
            "ps0": "前方偏右",
            "ps1": "右前方",
            "ps2": "右边",
            "ps3": "右后方",
            "ps4": "左后方",
            "ps5": "左边",
            "ps6": "左前方",
            "ps7": "前方偏左",
        }

        self.init()
        self.bound_funcs()

    def init(self):
        self.timestep = int(self.robot.getBasicTimeStep())
        self.left_motor.setPosition(float("inf"))
        self.right_motor.setPosition(float("inf"))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)
        self.gyro.enable(self.timestep)
        for name, loc in self.ps_names.items():
            d = self.robot.getDevice(name)
            self.ps_objs[loc] = d
            d.enable(self.timestep)

    def get_ps_values(self):
        self.ps_values = {}
        for loc, ps in self.ps_objs.items():
            v = round(ps.getValue(), 1)
            self.ps_values[loc] = v
        return self.ps_values

    def blocked(self, threshold=None):
        """check obstacles"""
        self.get_ps_values()
        if not threshold:
            threshold = self.obstacle_threshold
        block_locs = ["前方偏右", "前方偏左", "右前方", "左前方"]
        for loc in block_locs:
            if self.ps_values[loc] >= threshold:
                return True
        return False

    def ps_values_to_text(self, threshold=None):
        """parse ps values and convert to natual language output"""
        self.get_ps_values()
        obstacle_locations = []
        if not threshold:
            threshold = self.obstacle_threshold
        for loc, v in self.ps_values.items():
            if v >= threshold:
                self.log.debug(f"found obstacle in [{loc}], value={v}")
                obstacle_locations.append(loc)
        if not obstacle_locations:
            return "周围没有障碍物"
        return f'[{",".join(obstacle_locations)}] 存在障碍物'

    def stop(self):
        self.left_motor.setVelocity(0)
        self.right_motor.setVelocity(0)

    def calculate_rotation_time(self, degrees, speed):

        # 将输入的角度转换为弧度
        theta_body = math.radians(degrees)

        # 计算机器人的旋转速度 (原地旋转时，两轮速度相反)
        # ω_body = (r * (ω_right - ω_left)) / L
        # 原地旋转时，ω_right = +wheel_speed, ω_left = -wheel_speed
        omega_body = (self.wheel_radius * abs(speed) * 2) / self.axle_length

        # 计算所需时间: t = θ_body / ω_body
        rotation_time = theta_body / omega_body

        return rotation_time

    def rotate(self, angle: float, speed: float):
        time_to_rotate = round(
            self.calculate_rotation_time(float(angle), speed), 2
        )  # 旋转时间，单位：秒
        self.log.info(f"time_to_rotate: {time_to_rotate}s")
        start = time.time()
        while self.robot.step(self.timestep) != -1:
            self.left_motor.setVelocity(-speed)
            self.right_motor.setVelocity(speed)
            if time.time() - start > time_to_rotate:
                self.log.debug(f"completed rotate {angle} \t {speed}")
                break
        return time_to_rotate

    def move_to_target(self, distance: float, speed: float):
        time_to_travel = round(float(distance) / (abs(speed) * self.wheel_radius), 2)
        self.log.info(f"time_to_travel: {time_to_travel}s")

        start = time.time()
        while self.robot.step(self.timestep) != -1:
            # self.log.debug(f"set velocity {speed} for motor")
            self.left_motor.setVelocity(speed)
            self.right_motor.setVelocity(speed)

            # self.log.debug(f"check blocked")
            if self.blocked(300):
                self.stop()
                self.log.info("****** found obstacle, stopped ******")
                break

            # self.log.debug(f"check travel time")
            if time.time() - start > time_to_travel:
                self.log.debug(f"completed move {distance} \t {speed}")
                break

        return time_to_travel

    def move_forward(self, distance: float):
        """
        向前移动

        Args:
            distance (float): 距离，单位：米 (例如 1.0)

        Returns:
            float: 移动花费的时间
        """
        self.log.info(f"move_forward: {distance}")
        return self.move_to_target(distance, self.wheel_speed)

    def move_back(self, distance: float):
        """
        向后移动

        Args:
            distance (float): 距离，单位：米 (例如 1.0)

        Returns:
            float: 移动花费的时间
        """
        self.log.info(f"move_back: {distance}")
        return self.move_to_target(distance, -self.wheel_speed)

    def turn_left(self, angle: float):
        """
        向左旋转

        Args:
            angle (float): 度数，单位：角度 (例如 90.0)

        Returns:
            float: 旋转花费的时间
        """
        self.log.info(f"turn_left: {angle}")
        return self.rotate(angle, self.wheel_rotate_speed)

    def turn_right(self, angle: float):
        """
        向右旋转

        Args:
            angle (float): 度数，单位：角度 (例如 90.0)

        Returns:
            float: 旋转花费的时间
        """
        self.log.info(f"turn_right: {angle}")
        return self.rotate(angle, -self.wheel_rotate_speed)

    def get_tool_schemas(self):
        return [
            function_to_tool(self.turn_left),
            function_to_tool(self.turn_right),
            function_to_tool(self.move_forward),
            function_to_tool(self.move_back),
        ]

    def bound_funcs(self):
        self.bound_turn_left = partial(self.turn_left)
        self.bound_turn_right = partial(self.turn_right)
        self.bound_move_forward = partial(self.move_forward)
        self.bound_move_back = partial(self.move_back)

    def get_tools(self):
        return {
            "turn_left": self.bound_turn_left,
            "turn_right": self.bound_turn_right,
            "move_forward": self.bound_move_forward,
            "move_back": self.bound_move_back,
        }

    def handle_task(self, task):
        func_name = task.name
        args = json.loads(task.arguments)
        self.log.debug(f"func_name={func_name}")
        if func_name in self.get_tools():
            result = self.get_tools()[func_name](**args)
            self.log.info(f"tool executed completed: {result}")
        else:
            self.log.info(f"invalid task: {task}")
