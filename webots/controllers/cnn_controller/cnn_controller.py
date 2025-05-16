import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from controller import Robot, Camera, DistanceSensor, Motor

# 初始化机器人
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# 初始化摄像头
camera = robot.getDevice("camera")
camera.enable(timestep)
width, height = camera.getWidth(), camera.getHeight()

# 初始化距离传感器
num_sensors = 8
sensors = [robot.getDevice(f"ps{i}") for i in range(num_sensors)]
for sensor in sensors:
    sensor.enable(timestep)

# 初始化电机
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)


# 定义 CNN + PPO 策略网络
class CNNPolicy(nn.Module):
    def __init__(self):
        super(CNNPolicy, self).__init__()
        # CNN 部分（输入 3x64x64）
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=8, stride=4),  # [3, 64, 64] -> [32, 15, 15]
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),  # [32, 15, 15] -> [64, 6, 6]
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),  # [64, 6, 6] -> [64, 4, 4]
            nn.ReLU(),
            nn.Flatten(),  # 输出: 64 * 4 * 4 = 1024
        )
        # 适配层（将 1024 维映射到 576 维）
        self.adapter = nn.Linear(1024, 576)
        # 融合传感器数据
        self.fc = nn.Sequential(
            nn.Linear(576 + num_sensors, 128),  # 576 (CNN) + 8 (sensors)
            nn.ReLU(),
            nn.Linear(128, 3),
            nn.Softmax(dim=-1),
        )

    def forward(self, img, sensor_data):
        img_feat = self.cnn(img)
        img_feat = self.adapter(img_feat)  # 统一维度
        combined = torch.cat([img_feat, sensor_data], dim=1)
        return self.fc(combined)


# 初始化策略和优化器
policy = CNNPolicy()
optimizer = optim.Adam(policy.parameters(), lr=0.0001)
gamma = 0.99


# 图像预处理
def process_image(image):
    img = np.frombuffer(image, dtype=np.uint8).reshape((height, width, 4))
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)  # Webots 返回 BGRA，转为 RGB
    img = cv2.resize(img, (64, 64))  # 缩放到 64x64
    img = torch.FloatTensor(img).permute(2, 0, 1) / 255.0  # [C, H, W] 并归一化
    return img.unsqueeze(0)  # 添加 batch 维度


# 计算奖励的函数
def calculate_reward(sensor_values):
    max_sensor_value = max(sensor_values[0])
    collision_threshold = 100  # 根据传感器特性调整
    normalized_distance = max_sensor_value / collision_threshold
    collision_penalty = -1.0 if normalized_distance > 0.5 else 0.0
    forward_reward = 0.1
    return forward_reward + collision_penalty


loop = 0
# 训练循环
while robot.step(timestep) != -1:
    # 获取摄像头数据
    camera_data = camera.getImage()
    img_tensor = process_image(camera_data)

    # 获取传感器数据
    sensor_values = torch.FloatTensor([s.getValue() for s in sensors]).unsqueeze(0)

    # 选择动作
    action_probs = policy(img_tensor, sensor_values)
    dist = Categorical(action_probs)
    action = dist.sample()

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

    # 计算奖励（避障 + 前进奖励）
    reward = calculate_reward(sensor_values)

    if loop % 100 == 0:
        print(
            f"max(sensor_values)={max(sensor_values[0])}, sensor_values={sensor_values[0]}"
        )
        print(f"loop={loop}, action={action}")
        print(f"当前奖励: {reward:.2f}")

    # PPO 更新（简化版，完整训练需存储轨迹）
    optimizer.zero_grad()
    loss = -dist.log_prob(action) * reward
    loss.backward()
    optimizer.step()

    loop += 1
