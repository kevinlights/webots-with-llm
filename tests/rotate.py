#%%
import math
wheel_speed = 1.0

wheel_radius = 0.02
wheel_diameter = wheel_radius * 2
wheel_base = 0.052  # 轮距，单位：米
wheel_circumference = wheel_diameter * math.pi  # 轮子周长


rotation_radius = wheel_base / 2  # 旋转半径
rotation_distance = (float(30) * math.pi / 180) * rotation_radius  # 弧长
# 计算旋转时间
# 注意：这里我们假设左右轮速度差为10，因为left_motor速度为-5，right_motor速度为5
time_to_rotate = round(
    rotation_distance / (wheel_circumference * 2 * abs(1)), 2
)  # 旋转时间，单位：秒
print(f"time_to_rotate: {time_to_rotate}s")
#%%
import math

def calculate_rotation_time(degrees):
    # 机器人参数
    wheel_radius = 0.0205  # 轮子半径 (m)
    axle_length = 0.052    # 轴距 (m)
    wheel_speed = 3.14     # 轮子旋转速度 (rad/s)
    
    # 将输入的角度转换为弧度
    theta_body = math.radians(degrees)
    
    # 计算机器人的旋转速度 (原地旋转时，两轮速度相反)
    # ω_body = (r * (ω_right - ω_left)) / L
    # 原地旋转时，ω_right = +wheel_speed, ω_left = -wheel_speed
    omega_body = (wheel_radius * (wheel_speed - (-wheel_speed))) / axle_length
    
    # 计算所需时间: t = θ_body / ω_body
    rotation_time = theta_body / omega_body
    
    return rotation_time

# 示例：计算旋转90度所需的时间
degrees = 150
time = calculate_rotation_time(degrees)
print(f"旋转 {degrees} 度所需的时间: {time:.4f} 秒")
# %%
import math
wheel_radius = 0.0205  # 轮子半径 (m)
axle_length = 0.052    # 轴距 (m)
wheel_speed = 3.14     # 轮子旋转速度 (rad/s)
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
degrees = 150
time = calculate_rotation_time(degrees, -wheel_speed)
print(f"旋转 {degrees} 度所需的时间: {time:.4f} 秒")
# %%
