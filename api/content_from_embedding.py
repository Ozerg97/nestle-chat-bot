import json
from pathlib import Path
from typing import List, Dict

def find_datapoint_contents(folder_path: str, datapoint_ids: List[str]) -> Dict[str, str]:
    """
    Searches for content associated with a list of datapoint_ids in JSON files in a folder.

    :param folder_path: Path to the folder containing the JSON files
    :param datapoint_ids: List of IDs to search for
    :return: Dictionary {id: content}
    """
    folder = Path(folder_path)
    found_contents = {}

    for file in folder.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                file_id = data.get("id") or data.get("datapoint_id")

                if file_id in datapoint_ids:
                    found_contents[file_id] = {
                        "content": data.get("content", "(content not found)"),
                        "url": data.get("url")
                    }

                    if len(found_contents) == len(datapoint_ids):
                        break

        except Exception as e:
            print(f"❌ Error in {file.name}: {e}")

    return found_contents

# Exemple:
if __name__ == "__main__":
    datapoint_ids = [
        'a832caaa-d861-4b43-afb8-6e0e4f17a835',
        'f96bf786-06da-4c5b-a48b-b78603e86ac1',
        'ca5b7b54-0254-4b33-8a8b-883e6cc13763',
        '4b43687b-a7c2-407c-afa3-fc54c1524318',
        'fc26976f-b763-43ac-8095-f75dc54f5401'
    ]
    folder_path = "data/vectorDB/vector_documents"
    results = find_datapoint_contents(folder_path, datapoint_ids)

    print("\n🎯 Results found :\n")
    for dp_id in datapoint_ids:
        content = results.get(dp_id)
        if content:
            print(f"🟢 {dp_id}\n{content}...\n")
        else:
            print(f"🔴 {dp_id} not found.\n")
