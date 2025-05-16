from controller import Robot, Motor, DistanceSensor
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import random

# 初始化 Webots 机器人
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# 初始化传感器
num_sensors = 8
sensors = []
for i in range(num_sensors):
    sensor = robot.getDevice(f"ps{i}")
    sensor.enable(timestep)
    sensors.append(sensor)

# 初始化电机
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# 定义 PPO 网络
class PolicyNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(PolicyNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, output_size),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.fc(x)

# 初始化 RL 参数
input_size = num_sensors  # 8 个距离传感器
output_size = 3  # 动作空间：[左转, 直行, 右转]
policy = PolicyNetwork(input_size, output_size)
optimizer = optim.Adam(policy.parameters(), lr=0.001)
gamma = 0.99  # 折扣因子

loop = 0
# 训练循环
while robot.step(timestep) != -1:
    # 获取传感器数据
    sensor_values = np.array([sensor.getValue() for sensor in sensors])
    
    # 标准化输入
    state = torch.FloatTensor(sensor_values).unsqueeze(0)
    
    # 选择动作
    action_probs = policy(state)
    dist = Categorical(action_probs)
    action = dist.sample()

    if loop % 100 == 0:
        print(f"min(sensor_values)={min(sensor_values)}, sensor_values={sensor_values}")
        print(f"loop={loop}, action={action}\n")
    
    # 执行动作
    if action == 0:  # 左转
        left_motor.setVelocity(-1.0)
        right_motor.setVelocity(1.0)
    elif action == 1:  # 直行
        left_motor.setVelocity(3.0)
        right_motor.setVelocity(3.0)
    else:  # 右转
        left_motor.setVelocity(1.0)
        right_motor.setVelocity(-1.0)
    
    # 计算奖励（示例：鼓励前进，惩罚碰撞）
    if min(sensor_values) < 50:  # 靠近障碍物
        reward = -1.0
    else:
        reward = 0.1  # 鼓励前进
    
    # PPO 更新（简化版，完整训练需存储轨迹）
    optimizer.zero_grad()
    loss = -dist.log_prob(action) * reward
    loss.backward()
    optimizer.step()
    loop += 1