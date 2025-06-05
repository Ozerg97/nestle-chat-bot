from __future__ import annotations
import json, os, pathlib, re
from typing import Any, Dict, List
from dotenv import load_dotenv
from neo4j import GraphDatabase, Transaction

# ─────────────────────────────
# 1) Configuration & helpers
# ─────────────────────────────
load_dotenv()
URI  = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PWD  = os.getenv("NEO4J_PASSWORD")

VECTORS_DIR = pathlib.Path("data/vectorDB/vector_documents")
assert VECTORS_DIR.exists(), f"Dossier {VECTORS_DIR} introuvable"

_SPLIT_ING = re.compile(r",|;")

def _split_ingredients(raw: str | None) -> List[str]:
    """Return a clean list of individual ingredient strings."""
    if not raw:
        return []
    return [i.strip() for i in _SPLIT_ING.split(raw) if i.strip()]

# ─────────────────────────────
# 2) Schema (constraints / indexes)
# ─────────────────────────────
CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Recipe)   REQUIRE n.vector_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Product)  REQUIRE n.vector_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Brand)    REQUIRE n.name      IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Category) REQUIRE n.name      IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Ingredient) REQUIRE n.name   IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Feature)  REQUIRE n.text      IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Article)  REQUIRE n.vector_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Information) REQUIRE n.vector_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Store)    REQUIRE (s.name, s.address) IS UNIQUE",
]

FULLTEXT_IDX = (
    "CREATE FULLTEXT INDEX searchTitles IF NOT EXISTS "
    "FOR (n:Recipe|Product|Article) ON EACH [n.title, n.description, n.features]"
)

POINT_IDX = (
    "CREATE POINT INDEX storeLocation IF NOT EXISTS FOR (s:Store) ON (s.location)"
)

# ─────────────────────────────
# 3) Write‑transactions (Cypher)
# ─────────────────────────────

def insert_recipe(tx: Transaction, meta: Dict[str, Any], vector_id: str):
    if not meta.get("title"):
        return
    tx.run(
        """
        MERGE (r:Recipe {title:$title})
        ON CREATE SET r.vector_id=$vid
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
        """,
        title=meta.get("title", ""),
        url=meta.get("url", ""),
        desc=meta.get("description", ""),
        img=meta.get("image", ""),
        prep=meta.get("prep_time", ""),
        cook=meta.get("cook_time", ""),
        total=meta.get("total_time", ""),
        serv=meta.get("servings", ""),
        skill=meta.get("skill_level", ""),
        steps=meta.get("instructions", []),
        ingredients=meta.get("ingredients", []),
        vid=vector_id,
    )


def insert_product(tx: Transaction, meta: Dict[str, Any], vector_id: str):
    if not meta.get("title"):
        return

    # ── Pre‑processing ────────────────────────────────────────────────
    ing_raw: str = meta.get("ingredients") or ""
    ingredients = _split_ingredients(ing_raw)

    title: str = meta.get("title", "")
    brand: str | None = meta.get("brand") or (title.split()[0] if title else None)
    category: str | None = meta.get("category")

    tx.run(
        """
        MERGE (p:Product {title:$title})
        ON CREATE SET p.vector_id=$vid
        SET  p += {
            url:$url, description:$desc, size:$size, image:$img,
            ingredients_text:$ing_raw, features:$features,
            nutrition:$nutrition_lines, amazon_link:$amazon_link
        }

        // ── Features ─────────────────────────
        WITH p
        UNWIND $features AS f
            MERGE (fNode:Feature {text:f})
            MERGE (p)-[:HAS_FEATURE]->(fNode)

        // ── Ingredients ───────────────────────
        WITH p
        UNWIND $ingredients AS ing
            MERGE (i:Ingredient {name:ing})
            MERGE (p)-[:CONTAINS]->(i)

        // ── Brand (optional) ──────────────────
        WITH p
        WHERE $brand IS NOT NULL
            MERGE (b:Brand {name:$brand})
            MERGE (p)-[:BRANDED_AS]->(b)

        // ── Category (optional) ───────────────
        WITH p
        WHERE $category IS NOT NULL
            MERGE (c:Category {name:$category})
            MERGE (p)-[:IN_CATEGORY]->(c)

        // ── Stores ────────────────────────────
        WITH p
        UNWIND $stores AS sData
            MERGE (s:Store {name:sData.name, address:sData.address})
            ON CREATE SET s.location = point({latitude:sData.lat, longitude:sData.lon})
            MERGE (p)-[:SOLD_AT]->(s)
        """,
        title=title,
        url=meta.get("url", ""),
        desc=meta.get("description", ""),
        size=meta.get("size", ""),
        img=meta.get("image", ""),
        ing_raw=ing_raw,
        features=meta.get("features", []),
        nutrition_lines=meta.get("nutrition", []),
        ingredients=ingredients,
        brand=brand,
        category=category,
        amazon_link=meta.get("amazon_link"),
        stores=[
            {
                "name": s.get("name"),
                "address": s.get("address"),
                "lat": s.get("latitude"),
                "lon": s.get("longitude"),
            }
            for s in meta.get("stores", [])
            if s.get("name") and s.get("address")
        ],
        vid=vector_id,
    )


def insert_article(tx: Transaction, meta: Dict[str, Any], vector_id: str):
    if not meta.get("title"):
        return
    tx.run(
        """
        MERGE (a:Article {title:$title})
        ON CREATE SET a.vector_id=$vid
        SET  a += {url:$url, categorie:$cat}
        """,
        title=meta.get("title", ""),
        url=meta.get("url", ""),
        cat=meta.get("categorie", "Article"),
        vid=vector_id,
    )


def insert_information(tx: Transaction, meta: Dict[str, Any], vector_id: str):
    if not meta.get("title"):
        return
    tx.run(
        """
        MERGE (i:Information {title:$title})
        ON CREATE SET i.vector_id=$vid
        SET i.url=$url
        """,
        title=meta.get("title", ""),
        url=meta.get("url", ""),
        vid=vector_id,
    )

# ─────────────────────────────
# 4) Cross‑entity links (recipes ↔ products via ingredients)
# ─────────────────────────────
LINK_RECIPES_PRODUCTS = (
    "MATCH (r:Recipe)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(p:Product)\n"
    "MERGE (r)-[:USES {via:i.name}]->(p)"
)

# ─────────────────────────────
# 5) Main import
# ─────────────────────────────

def main(batch_size: int = 1000):
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    try:
        with driver.session() as sess:
            # Schema -------------------------------------------------------------
            for c in CONSTRAINTS:
                sess.run(c)
            sess.run(FULLTEXT_IDX)
            sess.run(POINT_IDX)

            print("🚀 Connected – importing vector documents…")

            files = list(VECTORS_DIR.glob("*.json"))
            total = len(files)
            processed = 0

            while processed < total:
                chunk = files[processed : processed + batch_size]
                with sess.begin_transaction() as tx:
                    for fp in chunk:
                        try:
                            data = json.loads(fp.read_text(encoding="utf-8"))
                        except Exception as e:
                            print(f"⚠️  Skip {fp.name}: {e}")
                            continue

                        meta = data.get("metadata", {})
                        v_id = data.get("id")
                        node_type = (
                            data.get("restricts", [{}])[0].get("allow", ["unknown"])[0]
                        )

                        if not meta.get("title"):
                            print(f"⛔ Skip {fp.name}: no title")
                            continue

                        if node_type == "recipe":
                            insert_recipe(tx, meta, v_id)
                        elif node_type == "product":
                            insert_product(tx, meta, v_id)
                        elif node_type == "article":
                            insert_article(tx, meta, v_id)
                        elif node_type == "information":
                            insert_information(tx, meta, v_id)
                        elif node_type == "brand":
                            # We intentionally ignore standalone brand files now.
                            print(f"↷ Ignore standalone brand file {fp.name}")
                        else:
                            print(f"❓ Unknown type '{node_type}' for {fp.name}, skipped.")

                    tx.commit()

                processed += len(chunk)
                print(f"   … {processed}/{total} processed")

            # Post‑processing links ---------------------------------------------
            sess.run(LINK_RECIPES_PRODUCTS)
            print("✅ Import terminé + liens ingrédients établis !")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
