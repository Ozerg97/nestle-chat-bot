import cloudscraper
import xml.etree.ElementTree as ET
from pathlib import Path

# Sitemap URL
url = "https://www.madewithnestle.ca/sitemap.xml"

# cloudscraper
scraper = cloudscraper.create_scraper()
response = scraper.get(url)

#
if response.status_code != 200:
    print(f"❌ Échec de la récupération du sitemap : {response.status_code}")
    exit()

# XML parsing
namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
root = ET.fromstring(response.content)

# URL EXTRACTION
links = [loc.text.strip() for loc in root.findall(".//ns:loc", namespace)]


outfile = Path("data/scraping/sitemap_links.txt")
with outfile.open("w", encoding="utf-8") as f:
    for link in links:
        f.write(link + "\n")

print(f"✅ {len(links)} links extracted and saved in: {outfile.resolve()}")
