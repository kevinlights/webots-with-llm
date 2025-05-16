import gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
import numpy as np

# 自定义 Gym 环境
class WebotsEnv(gym.Env):
    def __init__(self):
        super(WebotsEnv, self).__init__()
        self.action_space = gym.spaces.Discrete(3)  # 左转/直行/右转
        self.observation_space = gym.spaces.Box(low=0, high=1000, shape=(8,))  # 8 个传感器
        
    def reset(self):
        # 重置 Webots 场景
        return np.random.rand(8)  # 示例
    
    def step(self, action):
        # 执行动作并返回 (state, reward, done, info)
        state = np.random.rand(8)  # 示例
        reward = 1.0 if action == 1 else -0.1  # 鼓励直行
        done = False
        return state, reward, done, {}

# 训练 PPO
env = WebotsEnv()
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
model.save("ppo_webots_autonomous_car")