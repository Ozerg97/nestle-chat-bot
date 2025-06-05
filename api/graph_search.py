import os, json
from neo4j import GraphDatabase
from dotenv import load_dotenv
from graph_query import FETCH_GRAPH_QUERY

# ───────── Connexion ─────────────────────────────────────────
load_dotenv()
URI  = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PWD  = os.getenv("NEO4J_PASSWORD")

VECTOR_IDS = [
    "237f46b1-07a3-43a3-955e-b52a59b2c20c",
    "88f5546e-a37a-48d3-b7e7-ceb6a3a32689",
    "add3dbe4-5166-4ee9-8270-5b4f1ea8a431"
]


def clean_record(rec: dict) -> dict:
    
    return {k: v for k, v in rec.items()
            if v not in (None, "", [])}

def fetch_graphrag_data(vector_ids, query=FETCH_GRAPH_QUERY):
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    with driver.session() as session:
        raw = session.run(query, ids=vector_ids)
        return [clean_record(r.data()) for r in raw]

def main():
    results = fetch_graphrag_data(VECTOR_IDS, query=FETCH_GRAPH_QUERY)
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
