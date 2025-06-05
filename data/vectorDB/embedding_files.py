import json, pathlib, uuid, os
from typing import List
from dotenv import load_dotenv

import vertexai
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput

#─────────────────────────────
#  ENV
#─────────────────────────────
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION     = "us-central1"
MODEL_NAME = "text-embedding-004"
EMBED_DIM  = 768

vertexai.init(project=PROJECT_ID, location=REGION)
model = TextEmbeddingModel.from_pretrained(MODEL_NAME)

#─────────────────────────────
#  INPUT OUTPUT
#─────────────────────────────
DATA_DIR   = pathlib.Path("data/scraping/")
OUTPUT_DIR = pathlib.Path("data/vectorDB/vector_documents")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR_PRODUCT = pathlib.Path("data/add_amazon_link/")

PRODUCTS_JSON = DATA_DIR_PRODUCT / "products_with_amazon.json"
RECIPES_JSON  = DATA_DIR / "all_recipes.json"
ARTICLES_JSON = DATA_DIR / "all_articles.json"
BASICS_JSON   = DATA_DIR / "all_basics.json"
BRANDS_JSON   = DATA_DIR / "all_brands.json"

#─────────────────────────────
#  BUILD TEXT FUNCTIONS
#─────────────────────────────

def build_product_text(p: dict) -> str:
    "Returns the string that will be vectorized for a product."
    return " \n".join(filter(None, [
        "[TYPE: product]",
        "Title: " + str(p.get("title", "") or ""),
        "Description: " + str(p.get("description", "") or ""),
        "Ingredients: " + str(p.get("ingredients", "") or "")
    ]))


def build_recipe_text(r: dict) -> str:
    "Returns the string that will be vectorized for a recipe."
    return " \n".join(filter(None, [
        "[TYPE: recipe]",
        "Title: " + str(r.get("title", "") or ""),
        "Description: " + str(r.get("description", "") or ""),
        (
            "Ingredients: \n" + " \n".join(r.get("ingredients", []))
            if isinstance(r.get("ingredients"), list)
            else str(r.get("ingredients", "") or "")
        )
    ]))


def build_article_text(a: dict) -> str:
    return " \n".join(filter(None, [
        "[TYPE: article]",
        ("Title: "+ a.get("title", ""))
    ]))


def build_basic_text(b: dict) -> str:
    return " \n".join(filter(None, [
        "[TYPE: information]",
        ("Title: "+ b.get("title", ""))
    ]))


def build_brand_text(br: dict) -> str:
    if br.get("Brands"):
        return " \n".join(filter(None, [
            "[TYPE: brand-list]",
            ("Title: "+ br.get("title", "")),
            ("Brands: "+ " | ".join(br.get("Brands", [])) if isinstance(br.get("Brands"), list) else br.get("Brands", ""))
        ]))
    
    return " \n".join(filter(None, [
        "[TYPE: brand]",
       ("Title: "+  br.get("title", ""))
    ]))

#─────────────────────────────
#  UTILITIES
#─────────────────────────────

def load_json(path: pathlib.Path) -> List[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

#─────────────────────────────
#  EMBEDDING + EXPORT
#─────────────────────────────
index = 0

def embed_and_export(items: List[dict], build_fn, item_type: str, start_idx: int = 0) -> int:
    """Embeds each item, exports one .json file per vector."""
    global index
    for item in items:
        doc_text = build_fn(item)

        embedding = model.get_embeddings([
            TextEmbeddingInput(text=doc_text, task_type="RETRIEVAL_DOCUMENT")
        ], output_dimensionality=EMBED_DIM)[0].values

        doc = {
            "id": item.get("id") or str(uuid.uuid4()),
            "embedding": embedding,
            "content": doc_text,
            "metadata": item,         
            "restricts": [{"namespace": "type", "allow": [item_type]}]
        }

        out_file = OUTPUT_DIR / f"vector_{index}.json"
        out_file.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        index += 1
    return index

#─────────────────────────────
#  TRAITEMENT
#─────────────────────────────
products = load_json(PRODUCTS_JSON)
recipes  = load_json(RECIPES_JSON)
articles = load_json(ARTICLES_JSON)
basics   = load_json(BASICS_JSON)
brands   = load_json(BRANDS_JSON)

embed_and_export(products, build_product_text, "product")
embed_and_export(recipes,  build_recipe_text,  "recipe")
embed_and_export(articles, build_article_text, "article")
embed_and_export(basics,   build_basic_text,   "information")
embed_and_export(brands,   build_brand_text,   "brand")

print(f"✅ {index} documents traités et exportés dans '{OUTPUT_DIR}'.")
