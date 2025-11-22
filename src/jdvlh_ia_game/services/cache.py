import json
import os
import time
from typing import Any, Dict
from pathlib import Path

import yaml

# Chemin absolu vers config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

CACHE_DIR = config["cache"]["dir"]
os.makedirs(CACHE_DIR, exist_ok=True)


class CacheService:
    def __init__(self):
        self.ttl = config["cache"]["ttl"]
        self.locations = config["locations"]

    async def pregenerate(self):
        print("🟡 Pré-génération cache...")
        for loc in self.locations:
            safe_loc = loc.replace(" ", "_").replace("é", "e").replace("'", "")
            cache_file = os.path.join(CACHE_DIR, f"{safe_loc}.json")
            if not os.path.exists(cache_file):
                prompt = f"Description épique en 3 phrases de {loc} LOTR pour enfants."
                resp = f"Un lieu épique et mystérieux: {loc} dans Terre du Milieu."
                data = {
                    "description": resp,
                    "background": loc.lower().replace(" ", "_"),
                    "animation_trigger": "ambient_start",
                    "sfx": "wind" if "forêt" in loc.lower() else "echo",
                }
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        print("🟢 Cache prêt!")

    def get_location_data(self, location: str) -> Dict[str, Any]:
        safe_loc = location.replace(" ", "_").replace("é", "e").replace("'", "")
        cache_file = os.path.join(CACHE_DIR, f"{safe_loc}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if time.time() - os.path.getmtime(cache_file) > self.ttl:
                os.remove(cache_file)
            return data
        return {
            "description": "Lieu mystérieux...",
            "background": "default",
            "animation_trigger": "none",
            "sfx": "ambient",
        }
