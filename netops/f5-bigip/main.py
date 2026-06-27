import os
import re
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langfuse.langchain import CallbackHandler

from tools import (
    get_virtual_info,
    get_pool_info,
    get_snatpool_info,
    get_profile_info,
)

# Langfuse 默认关闭，可通过环境变量 ENABLE_LANGFUSE=true 启用
langfuse_callback = CallbackHandler() if os.getenv("ENABLE_LANGFUSE", "").lower() == "true" else None

# 使用智谱 GLM-4.5 模型
model = ChatOpenAI(
    model="glm-4.5",
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4",
    callbacks=[langfuse_callback] if langfuse_callback else [],
)

# ============== 状态定义 ==============

class AgentState(TypedDict):
    messages: list
    query_type: str  # "virtual" | "pool" | "snatpool" | "profile" | "all" | "unknown"
    virtual_result: str
    pool_result: str
    snatpool_result: str
    profile_result: str
    final_answer: str

# ============== 节点函数 ==============

def classify_query(state: AgentState) -> dict:
    """使用 LLM 分类用户问题类型"""
    user_message = state["messages"][-1].content if state["messages"] else ""
    
    prompt = f"""请分析以下用户问题，判断用户想查询什么类型的信息。

用户问题：{user_message}

请只返回以下选项之一：
- virtual（查询 Virtual Server 相关信息）
- pool（查询 Pool 相关信息）
- snatpool（查询 SNAT Pool 相关信息）
- profile（查询 Profile、SSL证书 相关信息）
- all（查询所有配置信息）
- unknown（无法判断）

只返回选项，不要其他内容。"""

    response = model.invoke([HumanMessage(content=prompt)])
    query_type = response.content.strip().lower()
    
    return {"query_type": query_type}

def query_virtual(state: AgentState) -> dict:
    """查询 Virtual Server 信息"""
    result = get_virtual_info()
    return {"virtual_result": result}

def query_pool(state: AgentState) -> dict:
    """查询 Pool 信息"""
    result = get_pool_info()
    return {"pool_result": result}

def query_snatpool(state: AgentState) -> dict:
    """查询 SNAT Pool 信息"""
    result = get_snatpool_info()
    return {"snatpool_result": result}

def query_profile(state: AgentState) -> dict:
    """查询 Profile 信息"""
    result = get_profile_info()
    return {"profile_result": result}

def query_all(state: AgentState) -> dict:
    """查询所有信息"""
    return {
        **query_virtual(state),
        **query_pool(state),
        **query_snatpool(state),
        **query_profile(state),
    }

def generate_answer(state: AgentState) -> dict:
    """生成最终回答"""
    query_type = state["query_type"]
    
    parts = []
    
    if query_type == "virtual":
        parts.append(f"Virtual Server 配置信息：\n{state['virtual_result']}")
    elif query_type == "pool":
        parts.append(f"Pool 配置信息：\n{state['pool_result']}")
    elif query_type == "snatpool":
        parts.append(f"SNAT Pool 配置信息：\n{state['snatpool_result']}")
    elif query_type == "profile":
        parts.append(f"Profile 配置信息：\n{state['profile_result']}")
    elif query_type == "all":
        parts.append(f"Virtual Server 配置信息：\n{state['virtual_result']}")
        parts.append(f"Pool 配置信息：\n{state['pool_result']}")
        parts.append(f"SNAT Pool 配置信息：\n{state['snatpool_result']}")
        parts.append(f"Profile 配置信息：\n{state['profile_result']}")
    else:
        parts.append("无法识别您的问题类型，请明确说明要查询 Virtual Server、Pool、SNAT Pool 还是 Profile 信息。")
    
    answer = "\n\n".join(parts)
    return {"final_answer": answer}

# ============== 条件路由函数 ==============

def route_query(state: AgentState) -> Literal["query_virtual", "query_pool", "query_snatpool", "query_profile", "query_all", "generate_answer"]:
    """根据问题类型路由到不同节点"""
    query_type = state["query_type"]
    
    if query_type == "virtual":
        return "query_virtual"
    elif query_type == "pool":
        return "query_pool"
    elif query_type == "snatpool":
        return "query_snatpool"
    elif query_type == "profile":
        return "query_profile"
    elif query_type == "all":
        return "query_all"
    else:
        return "generate_answer"

# ============== 构建流程图 ==============

workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("classify", classify_query)
workflow.add_node("query_virtual", query_virtual)
workflow.add_node("query_pool", query_pool)
workflow.add_node("query_snatpool", query_snatpool)
workflow.add_node("query_profile", query_profile)
workflow.add_node("query_all", query_all)
workflow.add_node("generate_answer", generate_answer)

# 设置入口
workflow.set_entry_point("classify")

# 添加条件边
workflow.add_conditional_edges(
    "classify",
    route_query,
    {
        "query_virtual": "query_virtual",
        "query_pool": "query_pool",
        "query_snatpool": "query_snatpool",
        "query_profile": "query_profile",
        "query_all": "query_all",
        "generate_answer": "generate_answer",
    }
)

# 添加普通边
workflow.add_edge("query_virtual", "generate_answer")
workflow.add_edge("query_pool", "generate_answer")
workflow.add_edge("query_snatpool", "generate_answer")
workflow.add_edge("query_profile", "generate_answer")
workflow.add_edge("query_all", "generate_answer")
workflow.add_edge("generate_answer", END)

# 编译流程图
agent_app = workflow.compile()

# ============== 运行 ==============

if __name__ == "__main__":
    # 生成 LangGraph 完整拓扑图
    agent_app.get_graph().draw_mermaid_png(output_file_path="bigip_graph.png")
    print("已生成拓扑图: bigip_graph.png")
    print()

    # 测试不同问题
    test_queries = [
        "查询所有 Virtual Server 的配置",
        "查询所有 Pool 的信息",
        "查询所有 SNAT Pool",
        "查询所有 Profile 配置",
        "查询所有 BIG-IP 配置信息",
        "今天天气怎么样？",
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"问题: {query}")
        print('='*50)
        
        result = agent_app.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "query_type": "",
                "virtual_result": "",
                "pool_result": "",
                "snatpool_result": "",
                "profile_result": "",
                "final_answer": "",
            },
            config={"callbacks": [langfuse_callback] if langfuse_callback else []},
        )
        
        print(f"问题类型: {result['query_type']}")
        print(f"\n回答:\n{result['final_answer']}")
