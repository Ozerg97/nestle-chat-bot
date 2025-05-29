import cloudscraper
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import time

#  FOLDER PATH
input_file = "data/scraping/sitemap_links.txt"
output_file = "data/scraping/body_classes.csv"

# Cloudflare
scraper = cloudscraper.create_scraper()

#  READ URL
with open(input_file, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

#
with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["URL", "Body Class"])  # En-têtes

    for i, url in enumerate(urls):
        try:
            print(f"🔎 ({i + 1}/{len(urls)}) Traitement de : {url}")
            response = scraper.get(url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                body_tag = soup.find("body")
                body_class = " ".join(body_tag.get("class", [])) if body_tag else "No <body> found"
                writer.writerow([url, body_class])
                print(body_class)
            else:
                print(f"⚠️ Échec ({response.status_code}) pour : {url}")
                writer.writerow([url, f"HTTP {response.status_code}"])

        except Exception as e:
            print(f"❌ Erreur sur {url} : {e}")
            writer.writerow([url, f"Erreur : {str(e)}"])

        time.sleep(0.5)  

print(f"✅ Terminé. Résultats sauvegardés dans {output_file}")
