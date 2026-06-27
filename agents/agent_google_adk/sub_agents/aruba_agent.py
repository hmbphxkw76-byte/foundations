from google.adk.agents.base_agent import BaseAgent
from google.adk.events.event import Event
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from collections.abc import AsyncGenerator

class ArubaAgent(BaseAgent):
    """Aruba Agent，返回固定的产品介绍内容"""
    
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        yield Event(
            content=types.Content(
                role="model",
                parts=[types.Part(text="Aruba重磅推出了Instant On全新无线产品及解决方案，以满足快速成长的中小型企业（SMB）市场对无线网络的需求。")]
            ),
            turn_complete=True,
        )

def create_aruba_agent() -> ArubaAgent:
    """创建 Aruba Agent"""
    return ArubaAgent(
        name="aruba_agent",
        description="Aruba 无线产品专家，提供众多无线产品及解决方案信息。",
    )
