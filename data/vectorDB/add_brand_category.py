"""
Adds the brand and category fields (if present) to the metadata of the target JSON files, based on the title.
"""

import json, re, pathlib
from typing import Dict, Any, Optional

SOURCE_FILE = "data/add_amazon_link/products_with_amazon.json"     
TARGET_DIR  = pathlib.Path("data/vectorDB/vector_documents") 
DRY_RUN     = False                      


def normalize(text: str) -> str:
    """Removes multiple spaces + lowercases to compare titles."""
    return re.sub(r"\s+", " ", text.strip()).lower()


def extract_title_from_content(raw: str) -> Optional[str]:
    """Gets 'Title: …' in the `content` key if metadata.title does not exist."""
    m = re.search(r"^[Tt]itle:\s*(.+)$", raw, flags=re.MULTILINE)
    return m.group(1).strip() if m else None


# 1) Load the source file and create a dict normalized_title -> partial_metadata
with open(SOURCE_FILE, encoding="utf-8") as f:
    source_items = json.load(f)

title_to_meta: Dict[str, Dict[str, str]] = {}
for item in source_items:
    title = item.get("title")
    if not title:
        continue  # pas de titre = on saute
    partial_meta = {}
    if "brand" in item:
        partial_meta["brand"] = item["brand"]
    if "category" in item:
        partial_meta["category"] = item["category"]
    if partial_meta:
        title_to_meta[normalize(title)] = partial_meta

print(f"[INFO] {len(title_to_meta)} titles to inject into the target files.")

#2) Loop through all JSON in the target folder
for path in TARGET_DIR.glob("*.json"):
    try:
        data: Dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] Impossible de lire {path.name}: {e}")
        continue

    meta = data.get("metadata", {})
    title = meta.get("title") or extract_title_from_content(data.get("content", ""))
    if not title:
        continue  # no title ⇒ we continue

    key = normalize(title)
    if key not in title_to_meta:
        continue  # This product is not in the source list

    wanted = title_to_meta[key]
    updated = False
    for field, value in wanted.items():
        if meta.get(field) != value:
            meta[field] = value
            updated = True

    if updated:
        data["metadata"] = meta
        if DRY_RUN:
            print(f"[DRY-RUN] {path.name} ← added {wanted}")
        else:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[OK] {path.name} ←updated with {wanted}")

print("\nTerminé.")
