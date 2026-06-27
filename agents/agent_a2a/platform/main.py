import streamlit as st
import requests
import time
import uuid
import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from common.a2a_protocol import (
    A2AJsonRpcRequest, 
    A2AJsonRpcResponse,
    A2ARpcParams,
    AgentInfo
)

load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ZHIPU_API_MODEL = os.getenv("ZHIPU_API_MODEL", "glm-4")

DISPATCH_AGENT_ID = "dispatch_agent"


def register_agent(agent_url):
    try:
        response = requests.get(f"{agent_url}/a2a/info", timeout=5)
        if response.status_code == 200:
            agent_info = AgentInfo(**response.json())
            st.session_state.registered_agents[agent_info.agent_id] = agent_info.model_dump()
            return {"success": True, "message": f"{agent_info.name} 注册成功"}
        else:
            return {"success": False, "message": f"获取Agent信息失败，HTTP状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"注册失败: {str(e)}"}


def unregister_agent(agent_id):
    if agent_id in st.session_state.registered_agents:
        del st.session_state.registered_agents[agent_id]
        return {"success": True, "message": "注销成功"}
    else:
        return {"success": False, "message": "Agent不存在"}


def dispatch_with_zhipu(user_query):
    if not ZHIPU_API_KEY:
        return {"success": False, "target_agent_id": None, "message": "智谱API Key未配置，请检查.env文件"}
    
    agent_list = [{"id": aid, "name": info["name"], "capabilities": info["capabilities"]} 
                  for aid, info in st.session_state.registered_agents.items()]
    
    if not agent_list:
        return {"success": False, "target_agent_id": None, "message": "没有已注册的Agent"}
    
    agent_descriptions = "\n".join([
        f"- Agent ID: {a['id']}, 名称: {a['name']}, 能力: {', '.join(a['capabilities'])}"
        for a in agent_list
    ])
    
    prompt = f"""你是一个智能调度器。请根据用户的查询，选择最合适的Agent来处理。
    
可用的Agent列表:
{agent_descriptions}

用户查询: "{user_query}"

请分析用户查询的意图，然后选择最适合处理该查询的Agent ID。

返回格式要求: 只返回选中的Agent ID，不要包含其他任何内容。如果没有合适的Agent，返回"none"。"""

    try:
        client = ZhipuAI(api_key=ZHIPU_API_KEY)
        response = client.chat.completions.create(
            model=ZHIPU_API_MODEL,
            messages=[
                {"role": "system", "content": "你是一个智能调度器，负责根据用户查询选择最合适的Agent。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        target_agent_id = response.choices[0].message.content.strip()
        
        if target_agent_id == "none":
            return {"success": False, "target_agent_id": None, "message": "没有找到合适的Agent"}
        
        return {"success": True, "target_agent_id": target_agent_id, "message": f"调度到Agent: {target_agent_id}"}
    
    except Exception as e:
        return {"success": False, "target_agent_id": None, "message": f"调度失败: {str(e)}"}


def send_a2a_request(target_agent_id, content):
    if target_agent_id not in st.session_state.registered_agents:
        return {"success": False, "content": {"error": "目标Agent未注册"}}
    
    agent_info = st.session_state.registered_agents[target_agent_id]
    endpoint = agent_info["endpoint"]
    
    request_id = str(uuid.uuid4())
    a2a_request = A2AJsonRpcRequest(
        jsonrpc="2.0",
        method="query",
        params=A2ARpcParams(
            source_agent_id=DISPATCH_AGENT_ID,
            target_agent_id=target_agent_id,
            content=content,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metadata={"source": "dispatch_agent"}
        ),
        id=request_id
    )
    
    try:
        response = requests.post(endpoint, json=a2a_request.model_dump(), timeout=10)
        if response.status_code == 200:
            response_json = response.json()
            a2a_response = A2AJsonRpcResponse(**response_json)
            if a2a_response.error:
                return {"success": False, "content": a2a_response.error.model_dump()}
            return {"success": True, "content": a2a_response.result or {}}
        else:
            return {"success": False, "content": {"error": f"Agent响应失败，HTTP状态码: {response.status_code}"}}
    except Exception as e:
        return {"success": False, "content": {"error": f"A2A通信失败: {str(e)}"}}


def extract_product_from_query(query):
    products = ["juniper", "f5", "aruba", "Juniper", "F5", "Aruba"]
    for product in products:
        if product.lower() in query.lower():
            return product.lower()
    return None


def main():
    st.title("A2A协议演示平台")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "registered_agents" not in st.session_state:
        st.session_state.registered_agents = {}
    
    with st.sidebar:
        st.header("Agent注册")
        agent_url = st.text_input("Agent地址", placeholder="http://localhost:8001")
        
        if st.button("注册Agent"):
            if agent_url:
                result = register_agent(agent_url)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])
            else:
                st.warning("请输入Agent地址")
        
        st.header("已注册的Agent")
        if st.session_state.registered_agents:
            for agent_id, info in st.session_state.registered_agents.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{info['name']}** ({agent_id})")
                with col2:
                    if st.button("注销", key=f"unregister_{agent_id}"):
                        unregister_agent(agent_id)
                        st.rerun()
        else:
            st.write("暂无注册的Agent")
    
    st.subheader("对话")
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "system":
            st.chat_message("assistant").write(msg["content"])
        elif msg["role"] == "agent":
            st.chat_message("assistant").write(f"**{msg['agent_name']}** 回复:\n{msg['content']}")
    
    user_input = st.chat_input("请输入你的问题（如：Juniper的价格是多少？）")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        if not st.session_state.registered_agents:
            st.error("请先注册至少一个Agent")
            st.session_state.chat_history.append({"role": "system", "content": "错误：请先注册至少一个Agent"})
            return
        
        with st.chat_message("assistant"):
            with st.spinner("正在查询..."):
                dispatch_result = dispatch_with_zhipu(user_input)
                
                if not dispatch_result["success"]:
                    st.write(f"❌ {dispatch_result['message']}")
                    st.session_state.chat_history.append({"role": "system", "content": f"错误: {dispatch_result['message']}"})
                    return
                
                target_agent_id = dispatch_result["target_agent_id"]
                agent_name = st.session_state.registered_agents[target_agent_id]["name"]
                
                product = extract_product_from_query(user_input)
                if not product:
                    product = "juniper"
                
                a2a_result = send_a2a_request(target_agent_id, {"product": product})
                
                if a2a_result["success"]:
                    a2a_response = a2a_result["content"]
                    knowledge_data = a2a_response.get("knowledge", {})
                    
                    if knowledge_data:
                        response_text = f"""
**{agent_name}** 查询结果：

📦 产品：{knowledge_data.get('name', '')}
💰 价格：{knowledge_data.get('price', '')}
🌐 网站：{knowledge_data.get('website', '')}
"""
                    else:
                        response_text = str(a2a_response)
                    
                    st.write(response_text)
                    st.session_state.chat_history.append({
                        "role": "agent", 
                        "agent_name": agent_name, 
                        "content": response_text
                    })
                else:
                    error_msg = a2a_result["content"].get("error", "未知错误")
                    st.write(f"❌ Agent调用失败: {error_msg}")
                    st.session_state.chat_history.append({"role": "system", "content": f"错误: {error_msg}"})


if __name__ == "__main__":
    main()