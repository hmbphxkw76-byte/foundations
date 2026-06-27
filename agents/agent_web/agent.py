import os, json, openai, random
from dotenv import load_dotenv
from zai import ZhipuAiClient
from openai.types.chat import ChatCompletionMessage
load_dotenv()   

client = ZhipuAiClient(api_key=os.getenv("ZHIPU_API_KEY"))

def get_weather(city):
    return f"你查询的{city}天气是{random.choice(['晴天','阴天','雨天'])}."

def get_knowledge(query):
    if "文档" in query:
        return f"产品{query}的文档地址是https://www.microshield.com.cn，敬请访问"
    elif "参数" in query:
        return f"产品{query}的技术参数很权威，详情请参考产品文档。"
    elif "价格" in query:
        return f"产品{query}的价格是{random.randint(10000000, 90000000)}元,物美价廉，值得购买。"
    else:
        return "资料正在更新中，请稍后查询"
    return f"你查询的{query}是行业用户选择的主流产品"

FUNCTION_MAP = {
    "get_weather": get_weather,
    "get_knowledge": get_knowledge
}

TOOLS =[
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather in a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_knowledge",
            "description": "个人知识助理，查询产品文档、技术参数、产品价格等信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询内容，如产品文档、技术参数、产品价格"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def process_ai_response(message: ChatCompletionMessage, messages: list):
    steps = []
    if message.tool_calls:
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                      "id": tool_call.id,
                      "type": "function",
                      "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                      }
                    } for tool_call in message.tool_calls
                ]
            }
        )
        for tool_call in message.tool_calls: 
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments
            
            steps.append({
                "type": "tool_call",
                "name": function_name,
                "arguments": arguments
            })

            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}
            function_to_run = FUNCTION_MAP.get(function_name)
            if function_to_run is None:
                steps.append({
                    "type": "tool_result",
                    "name": function_name,
                    "result": f"未知函数: {function_name}"
                })
                continue
            try:
                result = function_to_run(**arguments)
            except Exception as e:
                result = f"函数执行失败: {str(e)}"
            
            steps.append({
                "type": "tool_result",
                "name": function_name,
                "result": result
            })

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result
                }
            )
        final_response, final_steps = call_ai(messages)
        steps.extend(final_steps)
        return final_response, steps
    else:
        messages.append({"role": "assistant", "content": message.content})
        return message.content, steps


def call_ai(messages: list):
    response = client.chat.completions.create(
        model=os.getenv("ZHIPU_API_MODEL"),
        messages=messages,
        temperature=0.9,
        tools=TOOLS
    )
    return process_ai_response(response.choices[0].message, messages)


def chat_with_agent(user_input: str, messages: list = None):
    if messages is None:
        messages = []
    messages.append({
        "role": "user",
        "content": user_input
    })
    response, steps = call_ai(messages)
    return response, steps, messages


if __name__ == "__main__":
    messages = []
    while True:
        user_input = input("Send a message to the LLM:")
        if user_input == "exit" or user_input == "quit" or user_input =="q":
            break
        response, steps, messages = chat_with_agent(user_input, messages)
        print(f"AI回复: {response}")
        for step in steps:
            if step["type"] == "tool_call":
                print(f"调用工具: {step['name']}，参数: {step['arguments']}")
            elif step["type"] == "tool_result":
                print(f"工具返回: {step['name']} -> {step['result']}")
