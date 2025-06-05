# filename: structured_query_router.py
import os, regex as re, unicodedata
from typing import Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv

# ───────────────────────────────
# Neo4j Configuration
# ───────────────────────────────
load_dotenv()
URI  = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PWD  = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(URI, auth=(USER, PWD))

# ───────────────────────────────
# 1) Normalization of the question
# ───────────────────────────────
def normalize_question(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("ASCII")
    text = re.sub(r"[^\p{L}\p{N}\s]", " ", text.lower())
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ───────────────────────────────
# 2) Detection of structured questions
# ───────────────────────────────
COUNT_KEYWORDS = [
    r"how\s+many", r"number\s+of", r"count\s+of",
    r"combien\s+de", r"nombre\s+de", r"quantite\s+de"
]
PRODUCT_KEYWORDS = [
    r"product[s]?", r"produit[s]?", r"item[s]?"
]

COUNT_RE   = re.compile("|".join(COUNT_KEYWORDS),   re.I)
PRODUCT_RE = re.compile("|".join(PRODUCT_KEYWORDS), re.I)

def detect_structured_query(text: str) -> Optional[dict]:
    text_norm = normalize_question(text)


    if not (COUNT_RE.search(text_norm) and PRODUCT_RE.search(text_norm)):
        return None

   
    text_wo_trigger = COUNT_RE.sub("", text_norm)
    text_wo_trigger = PRODUCT_RE.sub("", text_wo_trigger).strip()

    category   = extract_category(text_wo_trigger)
    brand      = extract_brand(text_wo_trigger)
    ingredient = extract_ingredient(text_wo_trigger)

    return {"category": category, "brand": brand, "ingredient": ingredient}

# ───────────────────────────────
# 3) Extraction of structured elements
# ───────────────────────────────
CATEGORIES = {
    "coffee", "sauce", "nutrition", "quick mix drinks",
    "chocolate", "ice cream"
}
BRANDS = {
    "aero", "after eight", "big turk", "boost", "baci", "carnation",
    "coffee mate", "crunch", "coffee crisp", "del monte", "delissio",
    "drumstick", "drumstick bites", "easter chocolate", "essentia",
    "frozen desserts", "good host", "haagen dazs", "kitkat", "kit kat",
    "lean", "life", "lifesavers", "mackintosh toffee", "maggi", "milo",
    "mirage", "nescafe", "nesfruta", "nesquik", "nestea", "oreo",
    "parlour", "quality street", "real dairy", "rolo", "smarties",
    "sundae", "turtles", "vanilla", "iogo"
}
INGREDIENTS = {
    "milk", "sugar", "cocoa", "hazelnut", "wheat", "gluten",
    "soy lecithin", "vanilla", "salt", "palm oil", "almonds",
    "caramel", "coffee", "chocolate", "honey", "cream", "eggs",
    "butter", "peanuts", "raisins", "corn syrup", "coconut",
    "rice", "oat", "barley malt", "cinnamon", "nutmeg",
    "ginger", "mint", "berries", "strawberry", "raspberry",
    "lemon", "orange", "apple", "banana"
}

def _find_in_set(text: str, lexicon: set[str]) -> Optional[str]:
    for term in lexicon:
        pattern = r"\b" + re.sub(r"\s+", r"[\\s\\-]+", re.escape(term)) + r"\b"
        if re.search(pattern, text, flags=re.I):
            return term
    return None

def extract_category(text: str) -> Optional[str]:
    return _find_in_set(text, CATEGORIES)

def extract_brand(text: str) -> Optional[str]:
    return _find_in_set(text, BRANDS)

def extract_ingredient(text: str) -> Optional[str]:
    return _find_in_set(text, INGREDIENTS)

# ───────────────────────────────
# 4) Executing the Cypher query
# ───────────────────────────────
def execute_structured_query(params: dict) -> str:
    with driver.session() as session:
        if params["category"]:
            query = (
                "MATCH (p:Product)-[:IN_CATEGORY]->(c:Category) "
                "WHERE toLower(c.name) = $category "
                "RETURN count(p) AS total"
            )
            result = session.run(query, category=params["category"])
            count = result.single()["total"]
            return f"There are {count} products in the category '{params['category']}'."
        elif params["brand"]:
            query = (
                "MATCH (p:Product)-[:BRANDED_AS]->(b:Brand) "
                "WHERE toLower(b.name) = $brand "
                "RETURN count(p) AS total"
            )
            result = session.run(query, brand=params["brand"])
            count = result.single()["total"]
            return f"There are {count} products for the brand '{params['brand']}'."
        elif params["ingredient"]:
            query = (
                "MATCH (p:Product)-[:CONTAINS]->(i:Ingredient) "
                "WHERE toLower(i.name) = $ingredient "
                "RETURN count(p) AS total"
            )
            result = session.run(query, ingredient=params["ingredient"])
            count = result.single()["total"]
            return f"There are {count} products containing the ingredient '{params['ingredient']}'."
        else:
            query = "MATCH (p:Product) RETURN count(p) AS total"
            result = session.run(query)
            count = result.single()["total"]
            return f"There are {count} products listed."

# ───────────────────────────────
# 5) Main Router
# ───────────────────────────────
def handle_question(question: str) -> str:
    structured = detect_structured_query(question)
    if structured:
        return execute_structured_query(structured)
    else:
        return False

# ───────────────────────────────
# Exemple 
# ───────────────────────────────
if __name__ == "__main__":
    example_questions = [
        "How many products are under the AEro brand",
        "How many products are there?",
        "How many products under the coffee category?",
        "How many products by Nestle?",
        "How many products contain sugar?",
        "Give me the product count."
    ]
    for q in example_questions:
        print(f"User question: {q}")
        print("Answer:", handle_question(q))
        print("-" * 50)
