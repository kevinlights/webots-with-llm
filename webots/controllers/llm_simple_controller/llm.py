from openai import OpenAI
import json

EMPTY_THINK_PTN = "<think>\n\n</think>\n\n"
END_THINK_PTN = "</think>"


class SimpleLLM:
    def __init__(self, log):
        self.log = log
        self.client = self.get_client()
        self.last_output = ""
        self.sys_prompt = """
你是一个智能机器人，接收用户指令，并调用工具来响应指令。
输入的指令为障碍物方向，响应为调用工具和对应参数。
如果周围没有障碍物，则向前移动 0.1m。
"""

    def get_client(self):
        return OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
        )

    def plan(
        self,
        prompt: str,
        tool_schemas: list,
        model: str = "qwen2.5:3b",
    ):
        resp = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.sys_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            seed=0,
            tools=tool_schemas,
            tool_choice="required",
        )
        self.log.debug(resp.choices[0].message)
        # return resp.choices[0].message.content.replace(EMPTY_THINK_PTN, "")
        if resp.choices[0].message.tool_calls:
            tool_call = resp.choices[0].message.tool_calls[0]
            self.log.info(tool_call.function)
            return tool_call.function
            # func_name = tool_call.function.name
            # args = json.loads(tool_call.function.arguments)
            # if func_name in tool_dict:
            #     result = tool_dict[func_name](**args)
            #     return f"tool executed completed: {result}"
            # return f'no tools executed: {resp.choices[0].message.content.replace(EMPTY_THINK_PTN, "")}'
        else:
            raise Exception(
                f'no tool call returned: {resp.choices[0].message.content.replace(EMPTY_THINK_PTN, "")}'
            )
