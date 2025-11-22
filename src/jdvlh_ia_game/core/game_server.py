import asyncio
import time
from typing import Any, Dict, List
from pathlib import Path

import yaml
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# from ..middleware.security import security_middleware  # Temporairement commenté pour corriger syntaxe security.py
from ..services.cache import CacheService
from ..services.event_bus import EventBus
from ..services.narrative import NarrativeService
from ..services.state_manager import StateManager

# Chemin absolu vers config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="JDVLH IA Game Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(security_middleware)  # Temporairement commenté pour syntaxe security.py


class NarrativeResponse(BaseModel):
    narrative: str
    choices: List[str]
    location: str
    animation_trigger: str = "none"
    sfx: str = "ambient"


def get_narrative_service() -> NarrativeService:
    return NarrativeService()


def get_cache_service() -> CacheService:
    return CacheService()


def get_state_manager() -> StateManager:
    return StateManager()


def get_event_bus() -> EventBus:
    return EventBus()


@app.on_event("startup")
async def startup_event():
    state_manager = get_state_manager()
    cache_service = get_cache_service()
    asyncio.create_task(cache_service.pregenerate())
    asyncio.create_task(state_manager.cleanup_inactive())
    if state_manager.get_active_count() >= config["server"]["max_players"]:
        print("Attention: limite max_players atteinte")


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    player_id: str,
    narrative_service: NarrativeService = Depends(get_narrative_service),
    cache_service: CacheService = Depends(get_cache_service),
    state_manager: StateManager = Depends(get_state_manager),
    event_bus: EventBus = Depends(get_event_bus),
):
    if state_manager.get_active_count() >= config["server"]["max_players"]:
        await websocket.close(code=503, reason="Serveur plein")
        return

    await websocket.accept()
    state = state_manager.load_state(player_id)

    loc_data = cache_service.get_location_data(state["current_location"])
    welcome = {
        "narrative": "Bienvenue en Terre du Milieu ! Que fais-tu dans la Comté ?",
        "choices": ["Explorer la forêt", "Rencontrer un hobbit", "Chercher un trésor"],
        **loc_data,
    }
    await websocket.send_json(welcome)

    try:
        while True:
            choice = await websocket.receive_text()
            blacklist = config.get("blacklist_words", [])
            response = await narrative_service.generate(
                state["context"], state["history"], choice, blacklist
            )
            state["history"].append(f"Joueur: {choice}")
            state["history"].append(f"MJ: {response['narrative']}")
            if len(state["history"]) > 30:
                state["history"] = state["history"][-20:]
            state["current_location"] = response["location"]
            state_manager.save_state(player_id, state)
            loc_data = cache_service.get_location_data(state["current_location"])
            full_response = {**response, **loc_data}
            await websocket.send_json(full_response)
            event_bus.emit("narrative_generated", full_response)
    except WebSocketDisconnect:
        print(f"Joueur {player_id} déconnecté")


@app.post("/reset/{player_id}")
async def reset_game(
    player_id: str, state_manager: StateManager = Depends(get_state_manager)
):
    state = {
        "context": config["prompts"]["system"],
        "history": [],
        "current_location": "la Comté",
    }
    state_manager.save_state(player_id, state)
    return {"status": "Partie réinitialisée"}
