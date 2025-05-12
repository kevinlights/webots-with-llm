from controller import Robot

# 创建Robot实例
robot = Robot()

# 获取e-puck的电机设备
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')

# 设置电机为位置控制模式
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

# e-puck的轮子直径和轮距（根据实际情况调整）
wheel_diameter = 0.041 # 轮子直径，单位：米
wheel_base = 0.052 # 轮距，单位：米
wheel_circumference = wheel_diameter * 3.14159 # 轮子周长

# 计算旋转30度所需的弧长
rotation_angle = 30 # 旋转角度，单位：度
rotation_radius = wheel_base / 2 # 旋转半径
rotation_distance = (rotation_angle * 3.14159 / 180) * rotation_radius # 弧长

# 设置电机速度以实现左转
left_motor.setVelocity(-5.0) # 左轮逆时针旋转
right_motor.setVelocity(5.0) # 右轮顺时针旋转

# 计算旋转时间
# 注意：这里我们假设左右轮速度差为10，因为left_motor速度为-5，right_motor速度为5
rotation_time = rotation_distance / (wheel_circumference * 10) # 旋转时间，单位：秒

# 记录开始时间
start_time = robot.getTime()

# 控制旋转时间
while robot.step(int(robot.getBasicTimeStep())) != -1:
    if robot.getTime() - start_time > rotation_time:
        # 停止电机
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
        break

# 继续执行其他任务或关闭仿真
