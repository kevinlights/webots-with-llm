# %%
from openai import OpenAI

WEBOTS_PLAN_SYS_PROMPT = """
/no_think
请不要思考，按照以下示例要求处理用户输入，并生成相应的 JSON 格式的结果：

示例1：
用户：正前方有障碍物
输出：["向左转 80 度", "向前移动 20 厘米", "向右转 80 度"]

数据说明：
输出字符串列表，并按照实际躲避障碍物的逻辑顺序输出，障碍物宽度为 10 厘米

请直接输出内容，不要用 Markdown
"""

WEBOTS_MOVE_SYS_PROMPT = """
/no_think
请不要思考，按照以下示例要求处理用户输入，并生成相应的 JSON 格式的结果：

示例1：
用户：向前移动 1 米
输出：{"type": "move", "direction": "forward", "distance": "1"}
示例2：
用户：向前移动 10 厘米
输出：{"type": "move", "direction": "forward", "distance": "0.1"}
示例3：
用户：向左转 90 度
输出：{"type": "rotate", "direction": "left", "angle": "90"}

字段说明：
- type: 枚举，允许的值有 [move, rotate]
- direction: 枚举，允许的值有 [forward, back, left, right]
- distance: float 类型
- angle: float 类型

请直接输出内容，不要用 Markdown
"""

WEBOTS_DRIVE_SYS_PROMPT = """
/no_think
请不要思考，按照以下示例要求处理用户输入，并生成相应的 JSON 格式的结果：

解释用户输入：
输入为 e-puck 的距离传感器的值，当某一项的值 > 80.0 时，说明在该方向遇到了障碍物，需要向相反的方向旋转避开。
默认情况下都应该向前移动 0.1 米，输出 {"type": "move", "direction": "forward", "distance": "0.1"}

示例1：
用户： 64.2372960348239,64.43472856799397,60.673098996510696,64.68005449001203,66.93555935014602,64.23424360041922,63.998718518724935,65.72668119056857
输出：{"type": "move", "direction": "forward", "distance": "0.1"}
解释：所有方向都没有障碍物，则向前移动 0.1 米
示例2：
用户： 131.2372960348239,64.43472856799397,60.673098996510696,64.68005449001203,66.93555935014602,64.23424360041922,63.998718518724935,126.72668119056857
输出：{"type": "rotate", "direction": "left", "angle": "90"}
解释：前方两个传感器 0 和 7 的值都 > 80.0，说明在前方有障碍物，需要向左转 90 度避开
示例3：
用户： 64.2372960348239,64.43472856799397,120.673098996510696,79.68005449001203,66.93555935014602,64.23424360041922,63.998718518724935,65.72668119056857
输出：{"type": "move", "direction": "forward", "distance": "0.1"}
解释：右侧有障碍物，但正前方没有障碍物，则向前移动 0.1米

字段说明：
- type: 枚举，允许的值有 [move, rotate]
- direction: 枚举，允许的值有 [forward, back, left, right]
- distance: float 类型
- angle: float 类型

请直接输出内容，不要用 Markdown
"""

WEBOTS_PLAY_SYS_PROMPT = """
/no_think
请不要思考，按照以下示例要求处理用户输入，并生成相应的 JSON 格式的结果：

你是一个 e-puck 机器人小车，接收距离传感器的值，一共 8 个传感器的值，用逗号分隔开，依次是从右前方到左前方绕车身一周，请按照输入的数据，并结合上一次的输出结果，自动决定这一次的输出，输出格式和示例如下：

向前移动 0.1 米：{"type": "move", "direction": "forward", "distance": "0.1"}
向后移动 0.2 米：{"type": "move", "direction": "back", "distance": "0.2"}
向左旋转 90 度：{"type": "rotate", "direction": "left", "angle": "90"}
向右旋转 30 度：{"type": "rotate", "direction": "right", "angle": "30"}

字段说明：
- type: 枚举，允许的值有 [move, rotate]
- direction: 枚举，允许的值有 [forward, back, left, right]
- distance: float 类型
- angle: float 类型

要求：
- 请直接输出内容，不要用 Markdown
- 当所有输入的值都 < 80.0 时，请向前移动
- 当输入的某一项的值 > 80.0 时，说明在该方向遇到了障碍物，请向相反的方向旋转并移动来躲避
"""

WEBOTS_PLAY_USER_PROMPT = """
上一次的输出是：
{{last_output}}

当前输入是：
{{current_input}}
"""

THINK_PTN = "<think>\n\n</think>\n\n"


class SimpleLLM:
    def __init__(self):
        self.client = self.get_client()
        self.last_output = ""

    def get_client(self):
        return OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
        )

    def plan(self, prompt: str, model: str = "qwen3:4b"):
        resp = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": WEBOTS_PLAN_SYS_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            seed=0,
        )
        return resp.choices[0].message.content.replace(THINK_PTN, "")

    def chat(self, prompt: str, model: str = "qwen3:4b"):
        resp = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": WEBOTS_MOVE_SYS_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            seed=0,
        )
        return resp.choices[0].message.content.replace(THINK_PTN, "")


    def drive(self, prompt: str, model: str = "qwen2.5-coder:3b"):
        """drive based on inputs"""
        input = WEBOTS_PLAY_USER_PROMPT.replace("{{last_output}}", self.last_output).replace("{{current_input}}", prompt)
        resp = self.client.chat.completions.create(
            model=model,
            messages=[
                # {"role": "system", "content": WEBOTS_DRIVE_SYS_PROMPT},
                {"role": "system", "content": WEBOTS_PLAY_SYS_PROMPT},
                {"role": "user", "content": input},
            ],
            temperature=0,
            seed=0,
        )
        output = resp.choices[0].message.content.replace(THINK_PTN, "")
        self.last_output = output
        return output


# %%
# llm = SimpleLLM()
# llm.chat("向前移动 3 米")

# %%
# llm.chat("向后移动 3 米")

# %%
