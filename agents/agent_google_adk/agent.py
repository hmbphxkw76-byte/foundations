"""
Google ADK Multi-Agent 示例
架构：
- 根 Agent (assistant)：chat 模式，作为用户的主要交互入口
- Aruba Agent (aruba_agent)：返回 Aruba 产品介绍
- Juniper Agent (juniper_agent)：返回Juniper合作信息
模型：DeepSeek (通过 LiteLLM + OpenAI 兼容模式接入)
运行方式：
    运行命令: adk web   
"""

import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google_adk.sub_agents import create_aruba_agent, create_juniper_agent

load_dotenv()

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_api_base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
deepseek_api_model = os.getenv("DEEPSEEK_API_MODEL", "deepseek-chat")

if deepseek_api_key:
    os.environ["LITELLM_MODE"] = "PRODUCTION"
    LlmAgent.set_default_model(
        LiteLlm(
            model=f"openai/{deepseek_api_model}",
            api_base=deepseek_api_base_url,
            api_key=deepseek_api_key,
            temperature=0.7,
        )
    )

root_agent = LlmAgent(
    name="assistant",
    mode="chat",
    description="主助手，负责理解用户意图并转交给合适的专家处理。",
    instruction=(
        "你是主助手，负责理解用户意图并转交给合适的专家。\n\n"
        "可用的专家：\n"
        "- aruba_agent：Aruba 无线产品专家（无线网络、Instant On、中小型企业网络）\n"
        "- juniper_agent：Juniper 合作专家（Juniper 设备、MS技术团队、专业服务）\n\n"
        "决策规则：\n"
        "1. Aruba相关问题（无线网络、Instant On、SMB网络需求等）→ 转交给 aruba_agent\n"
        "2. Juniper相关问题（网络设备、合作服务、MS技术团队等）→ 转交给 juniper_agent\n"
        "3. 其他问题 → 尝试直接回复\n\n"
        "注意：只有需要专家处理时才转交，简单问题可直接回复。"
    ),
    sub_agents=[
        create_aruba_agent(),
        create_juniper_agent(),
    ],
)
