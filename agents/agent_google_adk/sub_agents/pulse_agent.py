"""Pulse Agent - 固定内容回复"""

from google.adk.agents.base_agent import BaseAgent
from google.adk.events.event import Event
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from collections.abc import AsyncGenerator


class PulseAgent(BaseAgent):
    """Pulse Agent，返回固定的 WIKI 知识库信息"""
    
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        yield Event(
            content=types.Content(
                role="model",
                parts=[types.Part(text="相关资料，查询公司WIKI知识库，http://space.microshield.com.cn 网址信息。")]
            ),
            turn_complete=True,
        )


def create_pulse_agent() -> PulseAgent:
    """创建 Pulse Agent"""
    return PulseAgent(
        name="pulse_agent",
        description="Pulse 知识库专家，提供 WIKI 知识库查询服务。",
    )
