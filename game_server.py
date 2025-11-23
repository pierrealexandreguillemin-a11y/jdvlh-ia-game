import asyncio
import json
import os
import time
import yaml
import sqlite3
import re
from typing import Dict, Any, List
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
import ollama
# Load config (chemin absolu)
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "src" / "jdvlh_ia_game" / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# CORS for client
app = FastAPI(title="JDVLH IA Game Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# Pydantic models
class NarrativeResponse(BaseModel):
    narrative: str
    choices: List[str]
    location: str
    animation_trigger: str = "none"
    sfx: str = "ambient"


class GameState(BaseModel):
    context: str = (
        config["prompts"]["system"]
        if "prompts" in config
        else "Maître du jeu pour enfants."
    )
    history: List[str] = []
    current_location: str = "la Comté"
    last_save: str = ""


# Global state
game_states: Dict[str, Dict[str, Any]] = (
    {}
)  # player_id -> {'state': GameState, 'last_activity': float, 'ws': WebSocket}
DB_PATH = "game.db"


# Init DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
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


# Load state from DB
def load_state(player_id: str) -> GameState:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT state_json FROM game_states WHERE player_id = ?", (player_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        data = json.loads(row[0])
        return GameState(**data)
    return GameState()


# Save state to DB
def save_state(player_id: str, state: GameState):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO game_states "
        "(player_id, state_json, last_activity) VALUES (?, ?, ?)",
        (player_id, state.model_dump_json(), time.time()),
    )
    conn.commit()
    conn.close()


# Sanitize input
def sanitize_choice(choice: str) -> str:
    choice = re.sub(r'[<>;{}()\\\\"]', "", choice.strip())[:100]
    return choice


# Content filter
def is_safe_content(text: str) -> bool:
    text_lower = text.lower()
    return not any(word in text_lower for word in config.get("blacklist_words", []))


# Cache functions
CACHE_DIR = config["cache"]["dir"]
os.makedirs(CACHE_DIR, exist_ok=True)


async def pregenerate_cache():
    print("[CACHE] Pré-génération cache...")
    for loc in config["locations"]:
        safe_loc = loc.replace(" ", "_").replace("é", "e").replace("'", "")
        cache_file = os.path.join(CACHE_DIR, f"{safe_loc}.json")
        if not os.path.exists(cache_file):
            prompt = f"Description épique en 3 phrases de {loc} LOTR pour enfants."
            try:
                resp = ollama.generate(model=config["ollama"]["model"], prompt=prompt)[
                    "response"
                ]
            except Exception:
                resp = f"Lieu mystérieux: {loc}."
            data = {
                "description": resp,
                "background": loc.lower().replace(" ", "_"),
                "animation_trigger": "ambient_start",
                "sfx": "wind" if "forêt" in loc.lower() else "echo",
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    print("[CACHE] Cache prêt!")


def get_location_data(location: str) -> Dict[str, Any]:
    safe_loc = location.replace(" ", "_").replace("é", "e").replace("'", "")
    cache_file = os.path.join(CACHE_DIR, f"{safe_loc}.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "description": "Lieu mystérieux...",
        "background": "default",
        "animation_trigger": "none",
        "sfx": "ambient",
    }


# Narrative generation with retry
async def generate_narrative(player_id: str, choice: str) -> Dict[str, Any]:
    data = game_states.get(player_id, {})
    state = data.get("state", GameState())
    choice = sanitize_choice(choice)

    # Prompt renforcé pour narratif riche EN FRANÇAIS
    narrative_structure = """
STRUCTURE NARRATIVE OBLIGATOIRE (8-12 phrases minimum):
1. CONTEXTE: Décrire l'environnement actuel (2-3 phrases)
2. ACTION: Raconter ce qui se passe suite au choix (3-4 phrases)
3. CONSÉQUENCE: Montrer le résultat de l'action (2-3 phrases)
4. SUSPENSE: Terminer par une question ou un cliffhanger (1-2 phrases)

LANGUE: FRANÇAIS uniquement. JAMAIS d'anglais.
TON: Épique, immersif, adapté enfants 10-14 ans.
SÉCURITÉ: JAMAIS de violence graphique, mort explicite, contenu adulte.
"""

    prompt = f"""{state.context}

{narrative_structure}

Historique récent:
{chr(10).join(state.history[-10:])}

Le joueur choisit: {choice}


Raconte maintenant la suite en FRANÇAIS avec une narrative
RICHE et STRUCTURÉE (8-12 phrases minimum).

Réponds EXACTEM(
    ENT en JSON valide:"
    "
  )
{{
  "narrative": (
    "Récit structuré en français de 8-12 phrases: contexte détaillé, "
    "action immersive, conséquence claire, suspense final. TOUJOURS en français."
  ),
  "choices": [
    "Action concrète en français",
    "Exploration détaillée en français",
    "Dialogue ou interaction en français"
  ],
  "location": "nom du lieu actuel ou nouveau",
  "animation_trigger": "none|fade_in|shake|glow",
  "sfx": "ambient|wind|echo|magic"
}}"""

    fallback = {
        "narrative": "L'aventure continue de manière mystérieuse...",
        "choices": ["Continuer", "Explorer", "Retourner"],
        "location": state.current_location,
        "animation_trigger": "none",
        "sfx": "ambient",
    }

    for attempt in range(config["ollama"]["max_retries"]):
        try:
            options = {
                "temperature": config["ollama"]["temperature"],
                "num_predict": config["ollama"]["max_tokens"],
            }
            resp = ollama.generate(
                model=config["ollama"]["model"], prompt=prompt, options=options
            )["response"]
            parsed = json.loads(resp)

            # Vérification contenu approprié (narrative + choices)
            narrative = parsed.get("narrative", "")
            choices_text = " ".join(parsed.get("choices", []))

            if not is_safe_content(narrative) or not is_safe_content(choices_text):
                # RÉGÉNÉRATION au lieu de message d'erreur !
                print(
                    f"[SAFETY] Contenu inapproprié, régénération (tentative {attempt + 1})"
                )
                if attempt < config["ollama"]["max_retries"] - 1:
                    await asyncio.sleep(1)  # Petit délai
                    continue  # Retry avec prompt renforcé
                else:
                    # Dernier essai → fallback sûr
                    parsed = fallback

            # Validation et nettoyage
            parsed["choices"] = parsed.get("choices", fallback["choices"])[:3]

            # Mise à jour historique et état
            state.history.append(f"Joueur: {choice}")
            state.history.append(f"MJ: {parsed['narrative']}")
            if len(state.history) > 30:
                state.history = state.history[-20:]

            state.current_location = parsed.get("location", state.current_location)
            save_state(player_id, state)
            data["state"] = state

            # Enrichissement avec cache location
            loc_data = get_location_data(state.current_location)
            parsed.update(loc_data)

            data["last_activity"] = time.time()
            return parsed

        except json.JSONDecodeError as e:
            print(f"[JSON] Tentative {attempt + 1} échouée (JSON invalide): {e}")
            if attempt == config["ollama"]["max_retries"] - 1:
                state.history.append("MJ: Erreur technique, fallback activé.")
                save_state(player_id, state)
                data["state"] = state
                data["last_activity"] = time.time()
                return fallback
            await asyncio.sleep(2 ** attempt)  # Backoff exponentiel

        except Exception as e:
            print(f"[ERROR] Tentative {attempt + 1} échouée: {e}")
            if attempt == config["ollama"]["max_retries"] - 1:
                state.history.append("MJ: Erreur technique, fallback activé.")
                save_state(player_id, state)
                data["state"] = state
                data["last_activity"] = time.time()
                return fallback
            await asyncio.sleep(2 ** attempt)  # Backoff

    return fallback


# Update activity
def update_activity(player_id: str):
    if player_id in game_states:
        game_states[player_id]["last_activity"] = time.time()


# Cleanup task
async def cleanup_sessions():
    while True:
        await asyncio.sleep(60)
        now = time.time()
        to_delete = []
        for pid, data in game_states.items():
            if now - data["last_activity"] > config["server"]["session_ttl"]:
                to_delete.append(pid)
        for pid in to_delete:
            del game_states[pid]
        print(f"Nettoyé {len(to_delete)} sessions inactives.")


@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(cleanup_sessions())
    asyncio.create_task(pregenerate_cache())


@app.get("/")
async def read_root():
    return FileResponse("index.html")


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    if len(game_states) >= config["server"]["max_players"]:
        await websocket.close(code=503, reason="Serveur plein")
        return

    await websocket.accept()
    state = load_state(player_id)
    game_states[player_id] = {
        "state": state,
        "last_activity": time.time(),
        "ws": websocket,
    }
    update_activity(player_id)

    loc_data = get_location_data(state.current_location)
    welcome = {
        "narrative": "Bienvenue en Terre du Milieu, aventurier ! Que fais-tu dans la Comté ?",
        "choices": ["Explorer la forêt", "Rencontrer un hobbit", "Chercher un trésor"],
        **loc_data,
    }
    await websocket.send_json(welcome)

    try:
        while True:
            data = await websocket.receive_text()
            response = await generate_narrative(player_id, data)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        pass
    finally:
        if player_id in game_states:
            del game_states[player_id]


@app.post("/reset/{player_id}")
async def reset_game(player_id: str):
    state = GameState()
    save_state(player_id, state)
    if player_id in game_states:
        game_states[player_id]["state"] = state
        update_activity(player_id)
    return {"status": "Partie reset"}


@app.get("/health")
async def health():
    return {"status": "OK", "players": len(game_states)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
