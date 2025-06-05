import json
import urllib.parse

# Input Output 
input_file = "data/add_stores/products_with_stores.json"
output_file = "data/add_amazon_link/products_with_amazon.json"

# Function to generate the Amazon link
def generate_amazon_search_link(product_name):
    base_url = "https://www.amazon.ca/s?k="
    query = urllib.parse.quote_plus(product_name)
    search_url = f"{base_url}{query}"
    return search_url

# Load existing JSON file
with open(input_file, 'r', encoding='utf-8') as f:
    products = json.load(f)

# Browse each product and add the Amazon link
for product in products:
    product_name = product.get('title', '')
    amazon_link = generate_amazon_search_link(product_name)
    product['amazon_link'] = amazon_link

# Write the new JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"Nouveau fichier JSON créé : {output_file}")
