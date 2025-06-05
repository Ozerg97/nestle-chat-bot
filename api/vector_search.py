import os
from dotenv import load_dotenv

from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from google.cloud import aiplatform_v1



# ──────────────────────────────────────────────────────────────
# 1) Load environment variables
# ──────────────────────────────────────────────────────────────
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

PROJECT_ID        = os.getenv("PROJECT_ID")
LOCATION          = os.getenv("LOCATION", "us-central1")
API_ENDPOINT      = os.getenv("API_ENDPOINT")  
INDEX_ENDPOINT    = os.getenv("INDEX_ENDPOINT")  
DEPLOYED_INDEX_ID = os.getenv("DEPLOYED_INDEX_ID") 
TOP_K             = 5

# Verification
if not all([PROJECT_ID, API_ENDPOINT, INDEX_ENDPOINT, DEPLOYED_INDEX_ID]):
    raise ValueError("❌ Certaines variables d'environnement sont manquantes.")

# ──────────────────────────────────────────────────────────────
# 2) Function to embed a text
# ──────────────────────────────────────────────────────────────
def embed_query(text: str) -> list[float]:
    model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    inp = TextEmbeddingInput(text=text, task_type="RETRIEVAL_QUERY")
    embedding = model.get_embeddings([inp])[0].values
    return embedding

# ──────────────────────────────────────────────────────────────
# 3) Vector Search Query Function (Low Level)
# ──────────────────────────────────────────────────────────────
def run_query(text: str, num_neighbors: int = TOP_K):
    print(f"\n🔍 Recherche pour : « {text} »\n")

    # Embedding
    vector = embed_query(text)

    # Create the MatchService client
    client_options = {"api_endpoint": API_ENDPOINT}
    match_client = aiplatform_v1.MatchServiceClient(client_options=client_options)

    # Build the query
    datapoint = aiplatform_v1.IndexDatapoint(feature_vector=vector)
    query = aiplatform_v1.FindNeighborsRequest.Query(
        datapoint=datapoint,
        neighbor_count=num_neighbors,
    )
    request = aiplatform_v1.FindNeighborsRequest(
        index_endpoint=INDEX_ENDPOINT,
        deployed_index_id=DEPLOYED_INDEX_ID,
        queries=[query],
        return_full_datapoint=False,
    )

    # Query
    response = match_client.find_neighbors(request=request)
    
    
   # Filter results (distance >= 0.5)
    neighbors = response.nearest_neighbors[0].neighbors
    datapoint_ids = [
        n.datapoint.datapoint_id
        for n in neighbors
        if n.distance > 0.6
    ]
    
    return datapoint_ids



    

# ──────────────────────────────────────────────────────────────
# 4) Interactive interface
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    question = input("❓ Pose ta question : ")
    resultat = run_query(question)
    print(resultat)