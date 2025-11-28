"""
SessionManager pour multi-device sync temps réel

Gère:
- Sessions actives par player_id (max 10 joueurs)
- Multiple sockets par player (multi-portables)
- Broadcast sync state (narrative, combat, character)
- Gestion déconnexions/reconnexions
- Limite simultané par player (e.g. 3 devices)
"""

from fastapi import WebSocket
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..models.game_entities import Player
from dataclasses import dataclass, field
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class ServerFullError(Exception):
    pass


@dataclass
class GameSession:
    player_id: str
    device: Dict
    started_at: datetime
    state: Dict = field(default_factory=dict)
    current_narrative: str = ""
    location: str = ""
    player: Optional[Player] = None


class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, GameSession] = {}
        self.player_sockets: Dict[str, List[WebSocket]] = (
            {}
        )  # player_id -> list sockets
        self.max_sessions = 10
        self.max_devices_per_player = 3
        self.state_manager = StateManager()

    async def create_session(self, player_id: str, device_info: Dict) -> GameSession:
        """Crée session pour nouveau player/device"""
        if len(self.active_sessions) >= self.max_sessions:
            raise ServerFullError("Serveur plein (max 10 joueurs)")

        # Load or create game state
        state = self.state_manager.load_state(player_id)
        session = GameSession(
            player_id=player_id,
            device=device_info,
            started_at=datetime.now(),
            state=state,
        )
        self.active_sessions[player_id] = session
        logger.info(
            f"Session créée pour {player_id} "
            f"(devices: {len(self.player_sockets.get(player_id, [])) + 1})"
        )
        return session

    async def add_socket(self, player_id: str, socket):
        """Ajoute socket pour player (multi-device)"""
        if player_id not in self.player_sockets:
            self.player_sockets[player_id] = []
        sockets = self.player_sockets[player_id]
        if len(sockets) >= self.max_devices_per_player:
            await socket.close(code=503, reason="Trop de devices pour ce joueur")
            return False
        sockets.append(socket)
        logger.info(f"Socket ajouté pour {player_id} (total: {len(sockets)})")
        return True

    async def remove_socket(self, player_id: str, socket):
        """Retire socket"""
        if player_id in self.player_sockets:
            sockets = self.player_sockets[player_id]
            if socket in sockets:
                sockets.remove(socket)
                if not sockets:
                    del self.player_sockets[player_id]
                logger.info(f"Socket retiré pour {player_id} (restant: {len(sockets)})")
                return True
        return False

    async def broadcast(self, player_id: str, event: str, data: Dict):
        """Broadcast event à tous devices du player"""
        if player_id in self.player_sockets:
            sockets = self.player_sockets[player_id][:]
            disconnected = []
            for socket in sockets:
                try:
                    await socket.send_json({"event": event, "data": data})
                except Exception:
                    disconnected.append(socket)
            # Clean disconnected
            for socket in disconnected:
                await self.remove_socket(player_id, socket)

    async def sync_state(self, player_id: str) -> Dict:
        """Sync état session (narrative, character, etc.)"""
        if player_id not in self.active_sessions:
            raise ValueError("Session inexistante")
        session = self.active_sessions[player_id]
        return {
            "character": (
                session.player.to_dict() if hasattr(session.player, "to_dict") else {}
            ),
            "narrative": getattr(session, "current_narrative", ""),
            "location": getattr(session, "location", ""),
            "inventory": getattr(session, "inventory", []),
            "quests": getattr(session, "quests", []),
            "combat": getattr(session, "combat", None),
            "session_info": {
                "devices": len(self.player_sockets.get(player_id, [])),
                "started_at": (
                    session.started_at.isoformat() if session.started_at else None
                ),
            },
        }

    async def update_narrative(
        self, player_id: str, narrative: str, choices: List[str]
    ):
        """Update narrative et broadcast"""
        if player_id in self.active_sessions:
            self.active_sessions[player_id].current_narrative = narrative
            self.state_manager.save_state(
                player_id, self.active_sessions[player_id].state
            )
            await self.broadcast(
                player_id, "narrative", {"narrative": narrative, "choices": choices}
            )

    async def update_character(self, player_id: str, character: Dict):
        """Update character et broadcast"""
        await self.broadcast(player_id, "character", {"character": character})

    async def update_combat(self, player_id: str, combat: Dict):
        """Update combat et broadcast"""
        await self.broadcast(player_id, "combat", {"combat": combat})

    async def cleanup_inactive(self):
        """Nettoie sessions inactives"""
        now = datetime.now()
        to_remove = []
        for player_id, session in self.active_sessions.items():
            if (now - session.started_at).total_seconds() > 3600:  # 1h inactive
                to_remove.append(player_id)
        for player_id in to_remove:
            del self.active_sessions[player_id]
            await self.state_manager.cleanup_inactive()
            logger.info(f"Session nettoyée: {player_id}")


# Singleton
_manager_instance: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = SessionManager()
    return _manager_instance
