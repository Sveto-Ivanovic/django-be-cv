
import json
import os
from django.conf import settings

def load_json_file(filepath: str) -> dict:
    full_path = os.path.join(settings.BASE_DIR, 'chatbot', filepath)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"The file {full_path} does not exist.")
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from the file {full_path}: {e}")