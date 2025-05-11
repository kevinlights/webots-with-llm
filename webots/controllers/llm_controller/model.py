# %%
from openai import OpenAI

WEBOTS_PLAN_SYS_PROMPT = """
/no_think
请不要思考，按照以下示例要求处理用户输入，并生成相应的 JSON 格式的结果：

示例1：
用户：正前方有障碍物
输出：["向左转 30 度", "向前移动 20 厘米", "向右转 150 度"]

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

THINK_PTN = "<think>\n\n</think>\n\n"


class SimpleLLM:
    def __init__(self):
        self.client = self.get_client()

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


# %%
# llm = SimpleLLM()
# llm.chat("向前移动 3 米")

# %%
# llm.chat("向后移动 3 米")

# %%
