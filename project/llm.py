# ─────────── dependencies ───────────────────────────────────
import os, json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from vector_search       import run_query          
from graph_search     import fetch_graphrag_data  
from graph_query import FETCH_GRAPH_QUERY
# -----------------------------------------------------------

# 1)  ENV + Gemini client
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
client = genai.Client(api_key=os.getenv("GEMINI_API"))

# 2) Utility: Transforms GraphRAG dict list into compact text
def format_graph_content(records: list[dict]) -> str:
    """
    Formatte les enregistrements en texte numéroté (1., 2., …)
    Chaque ligne contient : type, titre, nutrition, ingrédients, produits, marques, URL
    """
    lines = []
    for idx, r in enumerate(records, 1):
        parts = [f"{idx}. Category: {r['type']} | Title: {r.get('title', '')}"]
        if r.get("nutrition"):
            parts.append("Nutrition: " + "; ".join(r["nutrition"]))
        if r.get("ingredients"):
            parts.append("Ingredients: " + ", ".join(r["ingredients"]))
        if r.get("products"):
            parts.append("Products: " + ", ".join(r["products"]))
        if r.get("brands"):
            parts.append("Brands: " + ", ".join(r["brands"]))
        if r.get("url"):
            parts.append(f"URL: {r['url']}")
        lines.append(" | ".join(parts))
    
    return "\n".join(lines)

# 3) LLM wrapper sans vector_content
def generate_gemini_response(question: str,
                             graphRAG_content: str,
                             model: str = "gemini-2.0-flash") -> str:
    
   
    prompt = f"""
You are the MadeWithNestlé AI chatbot.
Answer **only** with the information found in the *GraphRAG Context*.
Format as a numbered list (1., 2., …).  
Each bullet : **title**, short description, **URL** if available.

User Question:
{question}

GraphRAG Context:
{graphRAG_content}
"""
    try:
        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction="Answer clearly and only using the provided context."
            ),
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ Error generating response: {e}"

# 4)  Exemple
if __name__ == "__main__":
    question = "Give me Smarties recipes"
    # 4-a  vector search → ids 
    ids = run_query(question, 10)           
    # 4-b  Graph → records
    graph_records = fetch_graphrag_data(ids, query=FETCH_GRAPH_QUERY)  # list[dict]
    # 4-c  text format for LLM
    graph_context = format_graph_content(graph_records)
    # 4-d  Appel LLM
    answer = generate_gemini_response(question, graph_context)
    print(answer)
