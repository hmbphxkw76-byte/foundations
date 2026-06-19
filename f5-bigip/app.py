from flask import Flask, render_template, request, jsonify
from langchain_core.messages import HumanMessage
from main import agent_app

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agent_query', methods=['POST'])
def agent_query():
    user_query = request.form.get('query', '').strip()
    
    if not user_query:
        return jsonify({'error': '请输入查询内容'})
    
    try:
        result = agent_app.invoke({
            "messages": [HumanMessage(content=user_query)],
            "query_type": "",
            "virtual_result": "",
            "pool_result": "",
            "snatpool_result": "",
            "profile_result": "",
            "final_answer": "",
        })
        
        return jsonify({
            'query_type': result['query_type'],
            'final_answer': result['final_answer']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
