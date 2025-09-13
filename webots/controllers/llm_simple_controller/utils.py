import inspect
import json
from typing import get_type_hints, get_origin, get_args, Optional, List


def function_to_tool(func) -> dict:
    """将Python函数转换为OpenAI Tool Schema"""
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""
    type_hints = get_type_hints(func)

    # 解析参数
    properties = {}
    required = []

    for name, param in sig.parameters.items():
        param_type = type_hints.get(name, str)
        param_default = param.default

        # 处理类型提示
        if get_origin(param_type) is Optional:
            actual_type = get_args(param_type)[0]
            is_required = False
        else:
            actual_type = param_type
            is_required = param_default is inspect.Parameter.empty

        # 映射Python类型到JSON Schema类型
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            List: "array",
        }
        json_type = type_map.get(actual_type, "string")

        # 构建参数属性
        properties[name] = {
            "type": json_type,
            "description": f"参数: {name}",  # 可从docstring提取更详细描述
        }

        if param_default is not inspect.Parameter.empty:
            properties[name]["default"] = param_default

        if is_required:
            required.append(name)

    # 生成Tool Schema
    tool_schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": doc.split("\n\n")[0],  # 取首行作为描述
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }
    return tool_schema


# from typing import Optional, List

# def get_weather(
#     city: str,
#     units: Optional[str] = "celsius",
#     forecast_days: Optional[int] = 1
# ) -> str:
#     """
#     获取指定城市的天气预报信息。

#     Args:
#         city (str): 城市名称（例如："北京"、"上海"）
#         units (str, optional): 温度单位，可选 "celsius" 或 "fahrenheit"。默认为 "celsius"。
#         forecast_days (int, optional): 预报天数（1-7天）。默认为 1。

#     Returns:
#         str: 天气预报描述文本
#     """
#     # 实际业务逻辑（示例）
#     return f"{city}未来{forecast_days}天天气：晴天，温度25{units[0].upper()}"

# 使用示例
# class WeatherService:
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         self.cache = {}  # 实例状态

#     def get_weather(
#         self,
#         city: str,
#         units: Optional[str] = "celsius",
#         forecast_days: Optional[int] = 1
#     ) -> str:
#         """获取指定城市的天气预报信息

#         Args:
#             city: 城市名称，例如"北京"
#             units: 温度单位，可以是"celsius"或"fahrenheit"，默认为"celsius"
#             forecast_days: 预报天数，默认为1天

#         Returns:
#             天气预报信息的字符串描述
#         """
#         # 使用实例属性
#         print(f"Using API key: {self.api_key}")
#         return f"{city}的天气: 25°C, 晴天, 预报{forecast_days}天"
# # 使用示例
# w = WeatherService(api_key="test")
# tool_schema = function_to_tool(w.get_weather)
# print(json.dumps(tool_schema, indent=2))
