"""Juniper Agent - 根据内容路由到 Pulse Agent 或直接回复"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .pulse_agent import create_pulse_agent


def create_juniper_agent() -> LlmAgent:
    """创建 Juniper Agent"""
    return LlmAgent(
        name="juniper_agent",
        mode="chat",
        description="Juniper 合作专家，处理 Juniper 相关问题，包含 Pulse 知识库查询。",
        instruction=(
            "你是 Juniper 合作专家。\n\n"
            "可用的专家：\n"
            "- pulse_agent：Pulse 知识库专家（查询公司 WIKI 知识库）\n\n"
            "决策规则：\n"
            "1. 如果用户查询包含 'pulse' 或 'Pulse' 相关内容 → 转交给 pulse_agent\n"
            "2. 其他 Juniper 相关问题 → 直接回复：公司与Juniper正式合作数十年，MS技术团队，为Junper用户提供专业化服务。\n\n"
            "注意：只有涉及 pulse 内容时才转交，其他直接回复。"
        ),
        sub_agents=[
            create_pulse_agent(),
        ],
    )
