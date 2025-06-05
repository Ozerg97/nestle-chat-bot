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
    Formats records as numbered text (1., 2., …)
    Each line contains: type, title, nutrition_value, ingredients, URL
    """
    lines = []
    for idx, r in enumerate(records, 1):
        parts = [f"{idx}. Category: {r['type']} | Title: {r.get('title', '')}"]
        if r.get("description"):
            parts.append(f"Description: {r['description']}")
        if r.get("nutrition_value"):
            parts.append("Nutrition value: " + "; ".join(r["nutrition_value"]))
        if r.get("ingredients"):
            parts.append("Ingredients: " + ", ".join(r["ingredients"]))
        if r.get("url"):
            parts.append(f"URL: {r['url']}")
        
        lines.append(" | ".join(parts))
    
    return "\n".join(lines)

# 3) LLM wrapper without vector_content
def generate_gemini_response(
    question: str,
    graphRAG_content: str,
    stores_information: str,
    model: str = "gemini-2.0-flash",
) -> str:
    """
    Generates the Gemini response while respecting the styles observed on the UI:
    - Friendly intro sentence.
    - Numbered list with bold titles.
    - Always include the product URL with an engaging label.
    - Three modes: where-to-buy, specific details, and generic response.
    """

    prompt = f"""
You are the MadeWithNestlé AI assistant.

STYLE & FORMAT
==============
• Always start the answer with a short, friendly greeting sentence (e.g., “Here’s what I found for you!”).
• Then, structure the answer into a clear, easy-to-read **numbered list** (1., 2., 3., etc.).
  - For each item:
    - Begin with the **product/recipe title in bold**.
    - On a new line, provide the main detail (depending on intent).
    - If appropriate, add a short description (1-2 sentences) written in a warm, conversational tone.
    - Always include “For more details: <URL>” on a new line.

• Format:
    1. **Title**
       Detail line 1.
       Detail line 2 (if needed).
       For more details: <URL>

• Keep each bullet short and concise (2-4 lines maximum).
• Do NOT use Markdown headings, tables, or code blocks.
• Use line breaks (\\n) to separate each line clearly.
• If a field is missing, write “Not available”.
• Never invent information — use only what’s in **GraphRAG Context** and **Stores Info**.

INTENT DETECTION RULES
======================

• For general questions:
    - Write a short, engaging description (1-2 lines).
    - Finish with “For more details: <URL>”.
• If the question is about a specific detail (e.g. calories, ingredients):
    - Start with a short, friendly phrase introducing the detail (e.g., “Here’s the information you requested about calories:”).
    - Then provide the detail on a new line.
    - Finish with “For more details: <URL>”.
• If the question is about where to buy a product:
    - List the store(s) with name, address, and distance (format: “Store: <name> | Address: <address> | Distance: <X> km”).
    - Include an Amazon link if available.
    - Finish with “For more details: <URL>”.



User Question:
{question}

GraphRAG Context:
{graphRAG_content}

Stores Info:
{stores_information}
"""

    try:
        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Follow the STYLE & FORMAT and INTENT DETECTION RULES exactly. "
                    "Use engaging language for product links (e.g., “For more details on this product: <URL>”) "
                    "and never add information not in the provided context."
                )
            ),
            contents=prompt,
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
