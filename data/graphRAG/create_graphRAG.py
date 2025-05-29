import json, os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 1  Connection details ────────────────────────────────────
load_dotenv()
URI  = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PWD  = os.getenv("NEO4J_PASSWORD")

# 2  Constraints & indexes ─────────────────────────────────
CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Recipe)  REQUIRE r.title IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.title IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Nutrient)   REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Feature)    REQUIRE f.text IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (b:Brand)      REQUIRE b.name IS UNIQUE",
]

FULLTEXT_IDX = """
    CREATE FULLTEXT INDEX recipeProductSearch IF NOT EXISTS
    FOR (n:Recipe|Product) ON EACH [n.title, n.description]
"""

# 3  Cypher helpers ────────────────────────────────────────
def insert_recipe(tx, rec):
    tx.run("""
        MERGE (r:Recipe {title:$title})
        SET  r += {
            url:$url, description:$desc, image:$img,
            prep_time:$prep, cook_time:$cook,
            total_time:$total, servings:$serv,
            skill_level:$skill, instructions:$steps
        }
        WITH r
        UNWIND $ingredients AS ing
            MERGE (i:Ingredient {name:ing})
            MERGE (r)-[:CONTAINS]->(i)
    """, title=rec["title"], url=rec["url"], desc=rec.get("description",""),
         img=rec.get("image",""), prep=rec.get("prep_time",""),
         cook=rec.get("cook_time",""), total=rec.get("total_time",""),
         serv=rec.get("servings",""), skill=rec.get("skill_level",""),
         steps=rec.get("instructions",[]), ingredients=rec["ingredients"])

def insert_product(tx, prod):
    nutrients = [n.split(":")[0].strip()
                 for n in prod.get("nutrition", []) if ":" in n]
    nutrition = prod.get("nutrition") or []
    ing_raw = prod.get("ingredients") or ""
    ing_list = [i.strip() for i in ing_raw.split(",") if i.strip()]

    title  = prod.get("title","")
    brand  = title.split()[0] if title else None
    made_ca = any(k in (prod.get("description") or "").lower()
              for k in ["canadian", "crafted in canada", "made in canada"])

    tx.run("""
        MERGE (p:Product {title:$title})
        SET  p += {
            url:$url, description:$desc, size:$size,
            image:$img, ingredients_text:$ing_raw,
            features:$features, nutrition:$nutrition
        }

        WITH p
        UNWIND $features AS f
            MERGE (fNode:Feature {text:f})
            MERGE (p)-[:HAS_FEATURE]->(fNode)

        WITH p
        UNWIND $nutrients AS n
            MERGE (nut:Nutrient {name:n})
            MERGE (p)-[:HAS_NUTRIENT]->(nut)

        WITH p
        UNWIND $ingredients AS ing
            MERGE (i:Ingredient {name:ing})
            MERGE (p)-[:CONTAINS]->(i)

        WITH p
        WHERE $brand IS NOT NULL
            MERGE (b:Brand {name:$brand})
            MERGE (p)-[:BRANDED_AS]->(b)

        WITH p
        WHERE $made_in_canada
            MERGE (c:Country {name:'Canada'})
            MERGE (p)-[:MADE_IN]->(c)
    """, title=title, url=prod["url"], desc=prod["description"],
         size=prod["size"], img=prod["image"], ing_raw=ing_raw,
         features=prod.get("features",[]), nutrition=nutrition, nutrients=nutrients,
         ingredients=ing_list, brand=brand, made_in_canada=made_ca)

# 4  Recipe ↔ Product linking by shared ingredients ────────
LINK_RECIPES_PRODUCTS = """
MATCH (r:Recipe)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(p:Product)
MERGE (r)-[:USES {via:i.name}]->(p)
"""

# 5  Main import script ────────────────────────────────────
def main():
    driver = None
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PWD))
        with driver.session() as sess:

            # Create constraints / index once
            for c in CONSTRAINTS:
                sess.run(c)
            sess.run(FULLTEXT_IDX)

            print("🚀 Connected – importing data…")

            # Recipes
            with open("data/scraping/all_recipes.json", encoding="utf-8") as f:
                for rec in json.load(f):
                    sess.execute_write(insert_recipe, rec)

            # Products
            with open("data/scraping/all_products.json", encoding="utf-8") as f:
                for prod in json.load(f):
                    if prod.get("title"):
                        sess.execute_write(insert_product, prod)

            # Link recipes to products they use
            sess.run(LINK_RECIPES_PRODUCTS)
            print("✅ Import & relationships complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver:
            driver.close()

if __name__ == "__main__":
    main()
