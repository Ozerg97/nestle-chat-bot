from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from graph_search     import fetch_graphrag_data 
from graph_query import FETCH_GRAPH_QUERY
from llm import format_graph_content


from vector_search import run_query
from content_from_embedding import find_datapoint_contents

from llm import generate_gemini_response 

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')

    # 1. vector search, we'll get the datapoints, the emdedding
    ids = run_query(question, 10) # datapoints = [...,...,...,...] vectors inside

    # 2. Searching content from graph database
    graph_records = fetch_graphrag_data(ids, query=FETCH_GRAPH_QUERY)  

    # 3. text format for LLM
    graph_context = format_graph_content(graph_records)

    # 4. send every content to LLM
    response = generate_gemini_response(question, graph_context) # fixer 
    
    return jsonify({'answer': response})

if __name__ == '__main__':
    app.run(port=8000)
