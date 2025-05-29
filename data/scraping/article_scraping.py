import csv, json, re
from pathlib import Path
from urllib.parse import urljoin

import cloudscraper
from bs4 import BeautifulSoup
from tqdm import tqdm

#─────────────────────────────
#  PATH
#─────────────────────────────
LINKS_FILE  = Path("data/scraping/body_classes.csv")
ARTICLE_OUT = Path("data/scraping/all_articles.json")
ARTICLE_OUT.parent.mkdir(parents=True, exist_ok=True)

scraper = cloudscraper.create_scraper()

def clean(text: str) -> str:
    
    return re.sub(r"\s+", " ", text).strip()

def scrape_article(url: str) -> dict | None:
   
    try:
        html = scraper.get(url, timeout=15).text
    except Exception as e:
        print(f"❌ {url} -> {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.select_one("h1.coh-heading.coh-style-standard-small-header-text")
    if not h1:
        print(f"⚠️  Title not found for {url}")
        return None

    return {
        "url": url,
        "title": clean(h1.text),
        "categorie": "Article",
    }

#─────────────────────────────
#  READING CSV & scraping
#─────────────────────────────
articles = []

with LINKS_FILE.open(newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    urls = [
        row[0].strip()
        for row in reader
        if len(row) >= 2 and "page-node-type-article" in row[1]
    ]

print(f"🔎 {len(urls)} filtered links to scrape...")
articles = []

for url in tqdm(urls, desc="📰 Scraping articles"):
    if data := scrape_article(url):
        articles.append(data)
#─────────────────────────────
#  JSON
#─────────────────────────────
ARTICLE_OUT.write_text(json.dumps(articles, ensure_ascii=False, indent=2),
                       encoding="utf-8")
print(f"→ Fichier écrit : {ARTICLE_OUT.resolve()}")
