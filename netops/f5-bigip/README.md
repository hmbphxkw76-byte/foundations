# BIG-IP 配置查询 Agent

本项目是一个基于 LangGraph + Flask 的 BIG-IP 配置查询系统，支持通过自然语言查询 Virtual Server、Pool、SNAT Pool、Profile 等配置信息。

---

## 项目结构

```
bigip/
├── app.py              # Flask Web 应用入口
├── main.py             # LangGraph Agent 定义与编译
├── tools.py            # BIG-IP 配置读取工具函数
├── bigip.conf          # BIG-IP 配置文件
├── templates/
│   └── index.html      # Web UI 页面
└── README.md           # 本文件
```

---

## 完整请求与响应流程

### 时序图

```
用户浏览器
    │
    │ ① 用户在输入框输入查询内容，点击"查询"
    │
    ▼
templates/index.html
    │
    │ ② submitQuery() 获取输入值，发送 POST 请求
    │    fetch('/agent_query', { method: 'POST', body: 'query=...' })
    │
    ▼
app.py (Flask)
    │
    │ ③ @app.route('/agent_query') 接收请求
    │    request.form.get('query') 提取用户输入
    │
    │ ④ 调用 agent_app.invoke()
    │    将用户输入包装为 HumanMessage
    │    {
    │      "messages": [HumanMessage(content=user_query)],
    │      "query_type": "",
    │      ...
    │    }
    │
    ▼
main.py (LangGraph Agent)
    │
    │ ⑤ 执行 LangGraph 流程
    │    __start__ ──→ classify ──→ query_virtual ──→ generate_answer ──→ __end__
    │    (LLM 分类)      (工具查询)        (生成回答)
    │
    │ ⑥ 节点函数调用 tools.py
    │    get_virtual_info() / get_pool_info() / ...
    │
    ▼
tools.py
    │
    │ ⑦ 读取 bigip.conf，解析配置，格式化输出
    │
    ▲
main.py (LangGraph Agent)
    │
    │ ⑧ 生成最终回答，存入 state["final_answer"]
    │
    ▲
app.py (Flask)
    │
    │ ⑨ 返回 JSON 响应
    │    jsonify({ 'query_type': 'virtual', 'final_answer': '...' })
    │
    ▼
templates/index.html
    │
    │ ⑩ JavaScript 解析 JSON，更新 DOM 显示结果
    │    显示识别类型和格式化后的回答内容
    │
    ▼
用户浏览器 (显示结果)
```

---

## 各层详细说明

### 1. 前端层 (templates/index.html)

| 步骤 | 动作 | 关键代码 |
|------|------|----------|
| 用户输入 | 在文本框输入查询内容，点击按钮或按 Enter | `<input id="queryInput">` |
| 触发请求 | `submitQuery()` 函数获取输入值并发送 POST | `fetch('/agent_query', {method: 'POST', body: 'query=...'})` |
| 显示结果 | 解析返回的 JSON，更新结果区域 DOM | `resultDiv.innerHTML = ...` |

### 2. Web 层 (app.py)

| 步骤 | 动作 | 关键代码 |
|------|------|----------|
| 接收请求 | Flask 路由 `/agent_query` 处理 POST 请求 | `@app.route('/agent_query', methods=['POST'])` |
| 提取参数 | 从表单数据中获取用户查询内容 | `request.form.get('query', '').strip()` |
| 调用 Agent | 将用户输入包装成消息列表，调用 LangGraph | `agent_app.invoke({"messages": [HumanMessage(content=query)]})` |
| 返回响应 | 将 Agent 结果封装为 JSON 返回前端 | `jsonify({'query_type': result['query_type'], 'final_answer': result['final_answer']})` |

### 3. Agent 层 (main.py)

| 步骤 | 动作 | 关键代码 |
|------|------|----------|
| 分类意图 | `classify_query` 节点调用 LLM 判断查询类型 | `model.invoke([HumanMessage(content=prompt)])` |
| 条件路由 | `route_query` 根据类型分发到不同查询节点 | `workflow.add_conditional_edges("classify", route_query, {...})` |
| 执行查询 | `query_virtual` 等节点调用 tools.py 获取数据 | `result = get_virtual_info()` |
| 生成回答 | `generate_answer` 节点组装最终输出 | `parts.append(f"Virtual Server 配置信息：\n{state['virtual_result']}")` |

### 4. 工具层 (tools.py)

| 步骤 | 动作 | 关键代码 |
|------|------|----------|
| 读取配置 | 打开 bigip.conf 文件读取全部内容 | `with open(CONFIG_FILE, 'r') as f: content = f.read()` |
| 正则解析 | 使用正则表达式提取各配置块 | `re.findall(r'ltm virtual /Common/([^\s]+)\s*\{([^}]+)\}', content, re.DOTALL)` |
| 格式化输出 | 将解析结果整理为结构化字符串 | `_format_results(results)` |

---

## 启动方式

### 启动 Web 服务

```bash
cd d:\我的文档\Codes\lang\deepagents\bigip
python app.py
```

服务启动后，访问 http://127.0.0.1:5000 打开查询页面。

### 直接运行 Agent（命令行模式）

```bash
cd d:\我的文档\Codes\lang\deepagents\bigip
python main.py
```

直接执行预设的测试查询，无需启动 Web 服务。

---

## 依赖说明

- `flask`: Web 框架
- `langgraph`: Agent 流程编排
- `langchain-openai`: LLM 模型调用
- `langfuse`: 可选，用于追踪 Agent 执行链路
- `python-dotenv`: 环境变量管理

---

## 扩展说明

- **LangGraph 可视化**: `main.py` 运行时会自动生成 `bigip_graph.png`，展示完整的 Agent 拓扑图。
- **Langfuse 追踪**: 如需查看每次请求在 Langfuse 中的 trace，确保环境变量中配置了 `LANGFUSE_SECRET_KEY` 等参数，并在 `app.py` 的 `invoke()` 中传入 `config={"callbacks": [langfuse_callback]}`。
