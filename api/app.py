from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from graph_search     import fetch_graphrag_data 
from graph_query import FETCH_GRAPH_QUERY
from llm import format_graph_content
import os
from dotenv import load_dotenv
from intelligent_count import handle_question
from stores_distance import generate_graph_context

from vector_search import run_query
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

from llm import generate_gemini_response 

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me")  
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True
)

CORS(
    app,
    origins=["https://nestle-ui-158884498350.us-central1.run.app"],
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.route("/user_location",  methods=["POST", "OPTIONS"])
def user_location():
    if request.method == "OPTIONS":   
        return '', 204
    payload = request.get_json(silent=True) or {}
    session["latitude"]  = payload.get("latitude")
    session["longitude"] = payload.get("longitude")
    print("SESSION après /user_location:", dict(session))

    return jsonify({"status": "ok"})



@app.route('/ask',  methods=["POST", "OPTIONS"])
def ask():
    if request.method == "OPTIONS":  
        return '', 204
    data   = request.get_json(silent=True) or {}

    question = data.get('question')  # user question
    latitude  = data.get("latitude")  # user lat
    longitude = data.get("longitude") # user long
    
    # 1. intelligent product count handler skip everything if product count question
    structured_answer = handle_question(question)
    if structured_answer:
        return jsonify({'answer': structured_answer})
    
    # 2. vector search, we'll get the datapoints, the emdedding
    ids = run_query(question, 5) # datapoints = [...,...,...,...] vectors inside

    # 3. Searching content from graph database
    graph_records = fetch_graphrag_data(ids, query=FETCH_GRAPH_QUERY)  
    
    # 4. Calculate distance from user and stores + stores informations 
    stores_information = generate_graph_context(graph_records, latitude, longitude)
    
    
    # 5. text format for LLM
    graph_context = format_graph_content(graph_records)
    
    
    # 6. send every content to LLM
    response = generate_gemini_response(question, graph_context, stores_information)  
    
    return jsonify({'answer': response})




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)