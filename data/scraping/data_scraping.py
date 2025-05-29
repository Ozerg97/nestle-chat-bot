import csv, json, re
from pathlib import Path
from urllib.parse import urljoin

import cloudscraper
from bs4 import BeautifulSoup
from tqdm import tqdm

#───────────────────────────
#  Folder Path
#───────────────────────────
LINKS_FILE  = Path("data/scraping/body_classes.csv")
PRODUCT_OUT = Path("data/scraping/all_products.json")
RECIPE_OUT  = Path("data/scraping/all_recipes.json")

scraper = cloudscraper.create_scraper()


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

#───────────────────────────
#  SCRAPE PRODUCT
#───────────────────────────
def scrape_product(url: str) -> dict | None:
    try:
        html = scraper.get(url, timeout=15).text
    except Exception as e:
        print(f"❌ {url} -> {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one("h1.coh-heading.product-title,"
                                "h1.coh-heading.global-product-title")
    title = clean(title_tag.text) if title_tag else None

    # image : <div.magnifier> puis <div.field--name-field-media-image>
    image = None
    img_tag = soup.select_one("div.magnifier img")
    if img_tag and img_tag.get("src"):
        image = urljoin(url, img_tag["src"])
    else:
        img_tag = soup.select_one("div.field--name-field-media-image img")
        if img_tag and img_tag.get("src"):
            image = urljoin(url, img_tag["src"])

    size_tag = soup.select_one("div.field--name-field-size.field__item")
    size = clean(size_tag.text) if size_tag else None

    desc_tag = soup.select_one("div.field--name-field-description")
    description = desc_tag.get_text("\n", strip=True) if desc_tag else None

    features = [clean(li.get_text())
                for li in soup.select("ul.coh-list-container li")]

   
    ingredients = None
    ing_tag = soup.select_one("div.sub-ingredients")

    if ing_tag:
        
        p = ing_tag.find("p")
        if p:
            ingredients = clean(p.text)
        else:
            ingredients = clean(ing_tag.text)


    nutrition = []


    nutri_box = soup.select_one("div.nutrients-container")
    if nutri_box:
        for row in nutri_box.select("div.coh-row-inner"):
            label = row.select_one(".label-column")
            amount = row.select_one(".first-column .amount-value")
            dv = row.select_one(".second-column .nutrient-value")

 
            if label and amount:
                qty = amount.text.strip()
                unit = amount.find_parent().text.replace(qty, "").strip()
                dvpt = f"{dv.text.strip()}%" if dv else "N/A"
                nutrition.append(f"{clean(label.text)}: {qty} {unit} ({dvpt})")

      
            elif label and dv:
                nutrition.append(f"{clean(label.text)}: N/A (DV: {dv.text.strip()}%)")

    return {
        "url": url,
        "title": title,
        "size": size,
        "image": image,
        "description": description,
        "categorie": "Product",
        "features": features,
        "ingredients": ingredients,
        "nutrition": nutrition,
    }

#───────────────────────────
#  SCRAPER RECIPES
#───────────────────────────
def scrape_recipe(url: str) -> dict | None:
    try:
        html = scraper.get(url, timeout=15).text
    except Exception as e:
        print(f"❌ {url} -> {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")

    # title
    title_tag = soup.select_one(
        "h1.coh-heading.coh-style-small-header-text-haagen-daz,"
        "h1.coh-heading.global-recipe-title"
    )
    title = clean(title_tag.text) if title_tag else None

    # image 
    img_tag = soup.select_one(
        "img.coh-image.coh-image-responsive-xl,"
        "div.field--name-field-media-image img"
    )
    image = urljoin(url, img_tag["src"]) if img_tag and img_tag.get("src") else None

    # description 
    desc_tag = soup.select_one("div.coh-ce-60395c97 p,"
                               "div.coh-ce-8b94fd33 p")
    description = clean(desc_tag.text) if desc_tag else None

    # time & portions
    stats = {}
    for stat in soup.select("div.stat"):
        label_span = stat.select_one(".stat-label")
        value_span = stat.select_one(".value")
        if label_span and value_span:
            key = clean(label_span.text).rstrip(":").lower().replace(" ", "_")
            stats[key] = clean(value_span.text)

    # ingredients
    ingredients = []
    if box := soup.select_one("div.coh-ce-5a95001"):
        ing_tags = box.select("div.field--name-field-ingredient-fullname")
        for it in ing_tags:
            link = it.find("a")
            txt  = link.text if link else it.text
            if txt.strip():
                ingredients.append(clean(txt))
    if not ingredients:
        box = soup.select_one("div.what-you-need-content")
        if box:
            ingredients = [clean(t.text) for t in
                           box.select("div.field--name-field-ingredient-fullname")
                           if t.text.strip()]

    # instructions
    instructions = []
    instr_boxes = soup.select("div.coh-ce-5a95001")
    if len(instr_boxes) >= 2:
        instructions = [clean(p.text) for p in
                        instr_boxes[1].select("p.coh-paragraph") if p.text.strip()]
    if not instructions:
        box = soup.select_one("div.coh-ce-de569f14")
        if box:
            instructions = [clean(p.text) for p in
                            box.select("p.coh-paragraph") if p.text.strip()]

    return {
        "url": url,
        "title": title,
        "image": image,
        "categorie": "Recipe",
        "description": description,
        **stats,                 # prep_time, cook_time, total_time, servings…
        "ingredients": ingredients,
        "instructions": instructions,
    }

#───────────────────────────
#  READ CSV & SCRAP
#───────────────────────────
products, recipes = [], []
total_lines = 0


products, recipes = [], []

with LINKS_FILE.open(newline="", encoding="utf-8") as f:
    reader = list(csv.reader(f))  
    total_lines = len(reader)
    print(f"📄 Nombre total de lignes dans le CSV : {total_lines}")

    for row in tqdm(reader, desc="🔎 Scraping pages", unit="page", total=total_lines):
        if len(row) < 2:
            continue
        url, body_class = row[0].strip(), row[1]

        if "page-node-type-dsu-product" in body_class:
            data = scrape_product(url)
            if data:
                products.append(data)

        elif "page-node-type-recipe" in body_class:
            data = scrape_recipe(url)
            if data:
                recipes.append(data)

print(f"✅ {len(products)} produits  |  {len(recipes)} recettes sur {total_lines} lignes totales.")

#───────────────────────────
#  WRITING JSON
#───────────────────────────
PRODUCT_OUT.write_text(json.dumps(products, ensure_ascii=False, indent=2), "utf-8")
RECIPE_OUT.write_text(json.dumps(recipes,  ensure_ascii=False, indent=2), "utf-8")

print(f"→ Fichiers écrits : {PRODUCT_OUT.name}  &  {RECIPE_OUT.name}")
