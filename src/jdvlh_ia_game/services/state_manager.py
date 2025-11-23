import asyncio
import json
import sqlite3
import time
from typing import Any, Dict
from pathlib import Path

import yaml

# Chemin absolu vers config.yaml
BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

DB_PATH = "game.db"


class StateManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.session_ttl = config["server"]["session_ttl"]
        self.max_players = config["server"]["max_players"]
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS game_states (
                player_id TEXT PRIMARY KEY,
                state_json TEXT,
                last_activity REAL
            )
        """
        )
        conn.commit()
        conn.close()

    def load_state(self, player_id: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT state_json FROM game_states WHERE player_id = ?", (player_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return {
            "context": config["prompts"]["system"],
            "history": [],
            "current_location": "la Comté",
        }

    def save_state(self, player_id: str, state: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO game_states (player_id, state_json, last_activity) "
            "VALUES (?, ?, ?)",
            (player_id, json.dumps(state), time.time()),
        )
        conn.commit()
        conn.close()

    async def cleanup_inactive(self):
        while True:
            await asyncio.sleep(60)
            now = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM game_states WHERE last_activity < ?",
                (now - self.session_ttl,),
            )
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            print(f"Nettoyé {deleted} sessions inactives DB.")

    def get_active_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM game_states WHERE last_activity > ?",
            (time.time() - self.session_ttl,),
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
