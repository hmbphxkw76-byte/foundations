import streamlit as st
from agent import chat_with_agent

st.set_page_config(
    page_title="Agent 基本工作原理演示",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agent 基本工作原理演示")

st.markdown("""
**Agent 工作流程：** 用户输入 → AI分析和理解用户需求 → 根据用户需求决定是否调用相关工具 → 生成最终内容回复用户
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    st.markdown(f"**👤 用户:** {chat['user']}")
    
    if chat['steps']:
        with st.expander("🔧 工具调用过程"):
            for step in chat['steps']:
                if step['type'] == 'tool_call':
                    st.markdown(f"**调用工具:** `{step['name']}`")
                    st.markdown(f"**参数:** `{step['arguments']}`")
                elif step['type'] == 'tool_result':
                    st.markdown(f"**工具返回:** `{step['result']}`")
    
    st.markdown(f"**🤖 AI:** {chat['ai']}")
    st.markdown("---")

user_input = st.text_input("请输入您的问题:", key="user_input")

if st.button("发送") and user_input:
    with st.spinner("AI 正在思考..."):
        response, steps, st.session_state.messages = chat_with_agent(user_input, st.session_state.messages)
    
    st.session_state.chat_history.append({
        'user': user_input,
        'ai': response,
        'steps': steps
    })
    
    st.rerun()