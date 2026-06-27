from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class AgentInfo(BaseModel):
    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    endpoint: str
    health_check_url: str


class A2ARpcParams(BaseModel):
    source_agent_id: str
    target_agent_id: Optional[str] = None
    content: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class A2AJsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: A2ARpcParams
    id: str


class A2AJsonRpcError(BaseModel):
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


class A2AJsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[A2AJsonRpcError] = None
    id: str