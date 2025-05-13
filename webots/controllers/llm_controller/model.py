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

你是一个 e-puck 机器人小车，接收距离传感器的值，一共 8 个传感器的值，用逗号分隔开，第 1,2 为右前方，第 3 为右侧，第 4 为右后方，第 5 为右后方，第 6 为左侧，第 7,8 为左前方。请按照输入的数据，并结合上一次的输出结果，自动决定这一次的输出，输出格式和示例如下：

向前移动 0.5 米：{"type": "move", "direction": "forward", "distance": "0.5"}
向左旋转 90 度：{"type": "rotate", "direction": "left", "angle": "90"}
向右旋转 90 度：{"type": "rotate", "direction": "right", "angle": "90"}
向左旋转 30 度：{"type": "rotate", "direction": "left", "angle": "30"}
向右旋转 30 度：{"type": "rotate", "direction": "right", "angle": "30"}

字段说明：
- type: 枚举，允许的值有 [move, rotate]
- direction: 枚举，允许的值有 [forward, back, left, right]
- distance: float 类型
- angle: float 类型

要求：
- 请直接输出内容，不要用 Markdown
- 当所有输入的值都 < 80.0 时，请向前移动
- 当输入的某一项的值 > 80.0 时，说明在该方向遇到了障碍物，请向与障碍物方向相垂直的方向旋转并移动来躲避
"""

# 你是一个 e-puck 机器人小车，接收距离传感器的值，一共 8 个传感器的值，用逗号分隔开，右前方为第 1 和第 2 个传感器，右侧为第 3 个传感器，右后方为第 4 个传感器，左后方为第 5 个传感器，左侧为第 6 个传感器，左前方为第 7 和第 8 个传感器。请先按逗号分隔所有数字，按要求逐个比较输入的数据，并结合上一次的输出结果，来分析并给出当前应该执行的操作。
WEBOTS_PLAY_SYS_PROMPT_THINK = """
请快速简洁思考，不超过 100 字，按照以下示例要求处理用户输入，并只生成一条相应的 JSON 格式的结果，请直接输出内容，不要用 Markdown。

你是一个 e-puck 机器人小车，接收距离传感器的值，一共 8 个传感器的值，用逗号分隔开。右前方传感器为第 1 和第 2 个，右侧传感器为第 3 个，右后方传感器为第 4 个，左后方传感器为第 5 个，左侧传感器为第 6 个，左前方传感器为第 7 和第 8 个。请先按逗号分隔所有数字，按要求逐个比较输入的数据，并结合上一次的输出结果，来分析并给出当前应该执行的操作。

要求：
- 请尽量多向前移动，使机器人小车走得更远
- 请严格计算并比较数值大小，不要出现错误如 70.8 大于 80.0
- 请严格按照逻辑分析，不要出现逻辑错误，如左右不分
- 当所有输入的值都小于 80.0 时，请向前移动
- 只考虑第1，2，7，8个传感器的值，其他的不用管，直接向前移动
- 当左前方传感器的值大于 80.0 时，说明在左前方遇到了障碍物，值越大说明距离障碍物越近，请向右侧旋转来躲避障碍物
- 当右前方传感器的值大于 80.0 时，说明在右前方遇到了障碍物，值越大说明距离障碍物越近，请向左侧旋转来躲避障碍物
- 当右后方传感器的值大于 80.0 时，可以向前移动
- 当左后方传感器的值大于 80.0 时，可以向前移动

输出格式和示例如下：
示例1：
输入：66.6,59.9,71.2,69.0,64.6,67.8,64.2,66.5
分析：所有传感器的值都小于80.0，不影响小车向前，输出向前移动 0.5 米
输出：{"type": "move", "direction": "forward", "distance": "0.5"}

示例2：
输入：66.6,59.9,71.2,569.0,184.6,67.8,64.2,66.5
分析：第4，5个传感器的值大于80.0，说明右后方和左后方有障碍物，不影响小车向前，输出向前移动 0.5 米
输出：{"type": "move", "direction": "forward", "distance": "0.5"}

示例3：
输入：166.6,159.9,71.2,69.0,64.6,67.8,64.2,66.5
分析：第1，2个传感器的值大于80.0，说明右前方有障碍物，小车要向左前方避让，输出向左旋转 30 度
输出：{"type": "rotate", "direction": "left", "angle": "30"}

示例4：66.6,59.9,71.2,69.0,64.6,67.8,164.2,166.5
分析：第7，8个传感器的值大于80.0，说明左前方有障碍物，小车要向右前方避让，输出向右旋转 30 度
输出：{"type": "rotate", "direction": "right", "angle": "30"}

示例5：166.6,59.9,71.2,69.0,64.6,67.8,64.2,166.5
分析：第1，8个传感器的值大于80.0，说明左前方和右前方都有障碍物，小车要向左侧避让，输出向左旋转 90 度
输出：{"type": "rotate", "direction": "right", "angle": "90"}

字段说明：
- type: 枚举，允许的值有 [move, rotate]
- direction: 枚举，允许的值有 [forward, back, left, right]
- distance: float 类型
- angle: float 类型
"""
# WEBOTS_PLAY_SYS_PROMPT_THINK = """
# 请快速简洁思考，不超过 100 字，按照以下示例要求处理用户输入，并只生成一条相应的 JSON 格式的结果，请直接输出内容，不要用 Markdown。

# 你是一个 e-puck 机器人小车，接收距离传感器的值，一共 8 个传感器的值，用逗号分隔开。右前方传感器为第 1 和第 2 个，右侧传感器为第 3 个，右后方传感器为第 4 个，左后方传感器为第 5 个，左侧传感器为第 6 个，左前方传感器为第 7 和第 8 个。请先按逗号分隔所有数字，按要求逐个比较输入的数据，并结合上一次的输出结果，来分析并给出当前应该执行的操作。

# 要求：
# - 请尽量多向前移动，使机器人小车走得更远
# - 请严格计算并比较数值大小，不要出现错误如 70.8 大于 80.0
# - 请严格按照逻辑分析，不要出现逻辑错误，如左右不分
# - 当所有输入的值都小于 80.0 时，请向前移动
# - 当左前方传感器的值大于 80.0 时，说明在左前方遇到了障碍物，值越大说明距离障碍物越近，请向右侧旋转来躲避障碍物
# - 当右前方传感器的值大于 80.0 时，说明在右前方遇到了障碍物，值越大说明距离障碍物越近，请向左侧旋转来躲避障碍物
# - 当右后方传感器的值大于 80.0 时，可以向前移动
# - 当左后方传感器的值大于 80.0 时，可以向前移动

# 输出格式和示例如下：
# - 向前移动 0.1 米：{"type": "move", "direction": "forward", "distance": "0.1"}
# - 向后移动 0.2 米：{"type": "move", "direction": "back", "distance": "0.2"}
# - 向左旋转 180 度：{"type": "rotate", "direction": "left", "angle": "180"}
# - 向左旋转 90 度：{"type": "rotate", "direction": "left", "angle": "90"}
# - 向右旋转 30 度：{"type": "rotate", "direction": "right", "angle": "30"}

# 字段说明：
# - type: 枚举，允许的值有 [move, rotate]
# - direction: 枚举，允许的值有 [forward, back, left, right]
# - distance: float 类型
# - angle: float 类型
# """

WEBOTS_PLAY_SYS_PROMPT_THINK_HANDLED = """
请快速简洁思考，不超过 100 字，按照以下示例要求处理用户输入，并只生成一条相应的 JSON 格式的结果，请直接输出内容，不要用 Markdown。

你是一个 e-puck 机器人小车，接收距离传感器的值，一共 8 个传感器的值，用逗号分隔开。右前方传感器为第 1 和第 2 个，右侧传感器为第 3 个，右后方传感器为第 4 个，左后方传感器为第 5 个，左侧传感器为第 6 个，左前方传感器为第 7 和第 8 个。请先按逗号分隔所有数字，按要求逐个比较输入的数据，并结合上一次的输出结果，来分析并给出当前应该执行的操作。

要求：
- 请尽量多向前移动，使机器人小车走得更远
- 请严格计算并比较数值大小，不要出现错误如 1==0
- 请严格按照逻辑分析，不要出现逻辑错误，如左右不分
- 当所有输入的值都等于 0 时，请向前移动
- 当左前方传感器的值等于 1 时，说明在左前方遇到了障碍物，请向右侧旋转来躲避障碍物
- 当右前方传感器的值等于 1 时，说明在右前方遇到了障碍物，请向左侧旋转来躲避障碍物
- 当右后方传感器的值等于 1 时，可以向前移动
- 当左后方传感器的值等于 1 时，可以向前移动

示例如下：
- 输入： 0,0,0,0,0,0,0,0 输出：（向前移动 0.1 米）{"type": "move", "direction": "forward", "distance": "0.1"}
- 输入： 0,0,1,0,0,0,0,0 输出：（向前移动 0.1 米）{"type": "move", "direction": "forward", "distance": "0.1"}
- 输入： 0,0,0,0,0,1,0,0 输出：（向前移动 0.1 米）{"type": "move", "direction": "forward", "distance": "0.1"}
- 输入： 1,0,0,0,0,0,0,1 输出：（向左旋转 90 度） {"type": "rotate", "direction": "left", "angle": "90"}
- 输入： 1,1,0,0,0,0,1,1 输出：（向左旋转 90 度） {"type": "rotate", "direction": "left", "angle": "90"}
- 输入： 1,0,0,0,0,0,0,1 输出：（向右旋转 90 度） {"type": "rotate", "direction": "right", "angle": "90"}
- 输入： 0,0,0,0,0,0,1,0 输出：（向右旋转 30 度） {"type": "rotate", "direction": "right", "angle": "30"}
- 输入： 0,0,0,0,0,1,1,0 输出：（向右旋转 30 度） {"type": "rotate", "direction": "right", "angle": "30"}
- 输入： 0,1,0,0,0,0,0,0 输出：（向左旋转 30 度） {"type": "rotate", "direction": "left", "angle": "30"}
- 输入： 0,1,1,0,0,0,0,0 输出：（向左旋转 30 度） {"type": "rotate", "direction": "left", "angle": "30"}

字段说明：
- type: 枚举，允许的值有 [move, rotate]
- direction: 枚举，允许的值有 [forward, back, left, right]
- distance: float 类型
- angle: float 类型
"""

REVIEW_SYS_PROMPT = """
请阅读并分析输入，快速简洁思考，按照输出格式要求检查输出结果，如果有非法输入，请修复并按要求重新输出正确的结果，否则请直接输出正确结果。

输出格式和示例如下：
- 向前移动 0.1 米：{"type": "move", "direction": "forward", "distance": "0.1"}
- 向后移动 0.2 米：{"type": "move", "direction": "back", "distance": "0.2"}
- 向左旋转 180 度：{"type": "rotate", "direction": "left", "angle": "180"}
- 向左旋转 90 度：{"type": "rotate", "direction": "left", "angle": "90"}
- 向右旋转 30 度：{"type": "rotate", "direction": "right", "angle": "30"}

请直接输出内容，不要用 Markdown
"""

WEBOTS_PLAY_USER_PROMPT = """
上一次的输出是：
{{last_output}}

当前输入是：
{{current_input}}
"""

EMPTY_THINK_PTN = "<think>\n\n</think>\n\n"
END_THINK_PTN = "</think>"


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
        return resp.choices[0].message.content.replace(EMPTY_THINK_PTN, "")

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
        return resp.choices[0].message.content.replace(EMPTY_THINK_PTN, "")

    def drive(self, prompt: str, model: str = "qwen2.5-coder:7b"):
        """drive based on inputs"""
        input = WEBOTS_PLAY_USER_PROMPT.replace(
            "{{last_output}}", self.last_output
        ).replace("{{current_input}}", prompt)
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
        output = resp.choices[0].message.content.replace(EMPTY_THINK_PTN, "")
        self.last_output = output
        return output

    def drive_with_think(self, prompt: str, model: str = "deepseek-r1:1.5b"):
        """drive based on inputs"""
        input = WEBOTS_PLAY_USER_PROMPT.replace(
            "{{last_output}}", self.last_output
        ).replace("{{current_input}}", prompt)
        # input = prompt
        resp = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": WEBOTS_PLAY_SYS_PROMPT_THINK},
                # {"role": "system", "content": WEBOTS_PLAY_SYS_PROMPT_THINK_HANDLED},
                {"role": "user", "content": input},
            ],
            temperature=0,
            seed=0,
        )
        output = resp.choices[0].message.content
        print(f"original drive output: {output}")
        output = output[output.find(END_THINK_PTN) + len(END_THINK_PTN) :]
        self.last_output = output
        return output

    def review(self, prompt: str, model: str = "deepseek-r1:1.5b"):
        resp = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": REVIEW_SYS_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            seed=0,
        )
        output = resp.choices[0].message.content
        print(f"original review output: {output}")
        output = output[output.find(END_THINK_PTN) + len(END_THINK_PTN) :]
        return output
    

    def zhipu_chat(self, prompt: str):
        api_key = open("api-key").read()
        if not api_key:
            raise Exception("please put zhipuai api key to file api-key")
        from zhipuai import ZhipuAI
        zhipu_cli = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey
        input = WEBOTS_PLAY_USER_PROMPT.replace(
            "{{last_output}}", self.last_output
        ).replace("{{current_input}}", prompt)
        # input = prompt
        resp = zhipu_cli.chat.completions.create(
            model="GLM-4-Flash",
            messages=[
                {"role": "system", "content": WEBOTS_PLAY_SYS_PROMPT},
                # {"role": "system", "content": WEBOTS_PLAY_SYS_PROMPT_THINK},
                {"role": "user", "content": input},
            ],
            temperature=0,
            seed=0,
        )
        output = resp.choices[0].message.content
        print(f"original drive output: {output}")
        self.last_output = output
        return output



# llm = SimpleLLM()
# llm.chat("向前移动 3 米")
# print(llm.drive_with_think("66.6,59.9,71.2,569.0,184.6,67.8,64.2,66.5"))
# print(llm.review(llm.drive_with_think("66.6,59.9,71.2,569.0,184.6,67.8,64.2,66.5")))

# print(llm.drive_with_think("65.3,119.9,450.4,60.8,64.7,68.4,63.5,64.1"))

# %%
