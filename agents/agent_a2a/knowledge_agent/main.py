import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from fastapi import FastAPI
from common.a2a_protocol import (
    A2AJsonRpcRequest, 
    A2AJsonRpcResponse, 
    A2AJsonRpcError,
    AgentInfo
)

app = FastAPI(title="Knowledge Agent", description="知识查询Agent服务")

KNOWLEDGE_DATA = {
    "juniper": {"name": "Juniper产品", "price": "1000万", "website": "www.microshield.com.cn"},
    "f5": {"name": "F5产品", "price": "500万", "website": "f5.microshield.com.cn"},
    "aruba": {"name": "Aruba产品", "price": "800万", "website": "aruba.microshield.com.cn"},
}


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "healthy", "service": "knowledge_agent"}


@app.post("/a2a/query", tags=["A2A Protocol"])
async def a2a_query(request: A2AJsonRpcRequest):
    try:
        product = request.params.content.get("product", "").lower()
        
        if product in KNOWLEDGE_DATA:
            data = KNOWLEDGE_DATA[product]
            response = A2AJsonRpcResponse(
                jsonrpc="2.0",
                result={
                    "knowledge": data,
                    "source_agent_id": "knowledge_agent",
                    "target_agent_id": request.params.source_agent_id,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "metadata": {"service": "knowledge_agent"}
                },
                id=request.id
            )
        else:
            response = A2AJsonRpcResponse(
                jsonrpc="2.0",
                error=A2AJsonRpcError(
                    code=-32602,
                    message="Invalid params",
                    data={"error": "正在更新中"}
                ),
                id=request.id
            )
        
        return response.model_dump()
    except Exception as e:
        response = A2AJsonRpcResponse(
            jsonrpc="2.0",
            error=A2AJsonRpcError(
                code=-32603,
                message="Internal error",
                data={"error": str(e)}
            ),
            id=request.id if hasattr(request, 'id') else ""
        )
        return response.model_dump()


@app.get("/a2a/info", tags=["A2A Protocol"])
async def get_agent_info():
    return AgentInfo(
        agent_id="knowledge_agent",
        name="知识查询Agent",
        description="提供产品知识查询服务",
        capabilities=["知识查询", "产品信息", "价格查询"],
        endpoint="http://localhost:8001/a2a/query",
        health_check_url="http://localhost:8001/health"
    ).model_dump()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)