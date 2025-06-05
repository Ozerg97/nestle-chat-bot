import math
from typing import List, Dict, Any, Tuple

def generate_graph_context(
    graph_records: List[Dict[str, Any]],
    user_latitude: float,
    user_longitude: float,
    max_stores: int = 5
) -> str:
    """
    • Keeps only records whose type == 'Product'.
    • For each product, calculates the distance between the user and
    each of the associated stores.
    • Does not recalculate the distance for stores already visited.
    • Adds the Amazon link if present.
    • Returns a string where each line describes a product and its stores
    (sorted by increasing distance, max_stores first).
    """

    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371.0  
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    lines: List[str] = []

   
    store_distance_cache: Dict[Tuple[str, str], float] = {}

    for record in graph_records:
        if record.get("type", "").lower() != "product":
            continue

        product_name = record.get("title", "Unknown Product")
        amazon_link = record.get("amazon_link")

        stores_raw = record.get("stores", [])

        enriched = []
        for s in stores_raw:
            try:
                key = (s["name"], s["address"])
                if key in store_distance_cache:
                    dist = store_distance_cache[key]
                else:
                    dist = haversine_distance(
                        user_latitude,
                        user_longitude,
                        float(s["latitude"]),
                        float(s["longitude"])
                    )
                    store_distance_cache[key] = dist

                enriched.append((dist, s))
            except (KeyError, TypeError, ValueError):
                continue

        if not enriched:
            product_line = f"graph_context: Product: {product_name} | No store with geo-data."
        else:
            enriched.sort(key=lambda t: t[0])
            enriched = enriched[:max_stores]

            store_fragments = [
                f"{idx}. Store: {s['name']} | Address: {s['address']} | Distance: {round(d, 2)} km"
                for idx, (d, s) in enumerate(enriched, 1)
            ]

            product_line = (
                f"graph_context: Product: {product_name} | " + " | ".join(store_fragments)
            )

        if amazon_link:
            product_line += f" | Amazon Link: {amazon_link}"

        lines.append(product_line)

    return "\n".join(lines)


# ─────────────────────────────
# Exemple
# ─────────────────────────────
if __name__ == "__main__":
    user_latitude, user_longitude = 43.780000, -79.400000
    # print(generate_graph_context(graph_records, user_latitude, user_longitude))
