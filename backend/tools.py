import json
import os
import re
from functools import lru_cache
from typing import Dict

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "book_summaries.json")

@lru_cache(maxsize=1)
def _load_book_map() -> Dict[str, str]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)
    return {item["title"].strip(): item["full_summary"].strip() for item in items}

def get_summary_by_title(title: str) -> str:
    title_norm = title.strip().lower()
    for k, v in _load_book_map().items():
        if k.lower() == title_norm:
            return v
    return "Rezumat indisponibil pentru titlul solicitat."

PROFANITY_WORDS = {
    "idiot", "prost", "fuck", "shit", "damn"
}

def contains_profanity(text: str) -> bool:
    tokens = re.findall(r"\w+", text.lower())
    return any(tok in PROFANITY_WORDS for tok in tokens)
