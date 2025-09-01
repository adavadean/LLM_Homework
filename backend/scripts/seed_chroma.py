import json, os
from rag import upsert_items

def main():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "book_summaries.json")
    with open(data_path, "r", encoding="utf-8") as f:
        items = json.load(f)
    count = upsert_items(items)
    print(f"Inserted/updated {count} items.")

if __name__ == "__main__":
    main()
