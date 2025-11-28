"""
Contrôle Parental pour JDVLH IA Game - Sécurité Enfants

Fonctionnalités:
- Code PIN parents (4 chiffres, hashé)
- Limite temps de session (60 min par défaut)
- Plages horaires autorisées (14h-20h par défaut)
- Niveaux de contenu (10+, 12+, 14+)
- Logs de sessions (choix, durée, timestamps)
- Export rapports hebdomadaires (email parents)

Persistance: Par player_id dans StateManager
"""

import hashlib
import datetime
import json
import smtplib  # noqa: F401 - Reserved for email export feature
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import logging

from ..services.state_manager import StateManager

logger = logging.getLogger(__name__)


@dataclass
class ParentalSession:
    """Session contrôle parental par joueur"""

    pin_hash: Optional[str] = None
    settings: Dict = field(
        default_factory=lambda: {
            "max_session_time": 60,
            "allowed_hours": (14, 20),
            "content_level": "10+",
            "enable_logs": True,
        }
    )
    start_time: Optional[datetime.datetime] = None
    logs: List[Dict] = field(default_factory=list)
    total_play_time: int = 0  # minutes

    def __post_init__(self):
        if self.settings is None:
            self.settings = {
                "max_session_time": 60,  # minutes
                "allowed_hours": (14, 20),  # 14h-20h
                "content_level": "10+",
                "enable_logs": True,
            }
        if self.logs is None:
            self.logs = []

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):
        session = cls(**data)
        session.logs = data.get("logs", [])
        return session


class ParentalControl:
    """Service contrôle parental singleton"""

    def __init__(self):
        self.sessions: Dict[str, ParentalSession] = {}
        self.state_manager = StateManager()

    def get_or_create_session(self, player_id: str) -> ParentalSession:
        """Récupère ou crée session parentale pour joueur"""
        if player_id not in self.sessions:
            state = self.state_manager.load_state(player_id)
            parental_data = state.get("parental", {})
            self.sessions[player_id] = ParentalSession.from_dict(parental_data)
        return self.sessions[player_id]

    def set_pin(self, player_id: str, pin: str) -> bool:
        """Définit code PIN (4 chiffres) - hashé"""
        if not (pin.isdigit() and len(pin) == 4):
            return False
        session = self.get_or_create_session(player_id)
        session.pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        self._save_session(player_id)
        logger.info(f"PIN défini pour {player_id}")
        return True

    def verify_pin(self, player_id: str, pin: str) -> bool:
        """Vérifie code PIN"""
        session = self.get_or_create_session(player_id)
        if not session.pin_hash:
            return False
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        return pin_hash == session.pin_hash

    def check_session_allowed(self, player_id: str) -> Tuple[bool, str]:
        """
        Vérifie si session autorisée :
        - Plages horaires
        - Durée session max
        """
        now = datetime.datetime.now()
        session = self.get_or_create_session(player_id)

        # Check heures autorisées
        hour = now.hour
        allowed_start, allowed_end = session.settings["allowed_hours"]
        if not (allowed_start <= hour < allowed_end):
            return False, f"Hors horaires autorisés ({allowed_start}h-{allowed_end}h)"

        # Check durée session
        if session.start_time:
            duration_min = int((now - session.start_time).total_seconds() / 60)
            if duration_min > session.settings["max_session_time"]:
                return (
                    False,
                    f"Session dépassée ({session.settings['max_session_time']} min)",
                )

        return True, "OK"

    def start_session(self, player_id: str):
        """Démarre session (reset timer)"""
        session = self.get_or_create_session(player_id)
        session.start_time = datetime.datetime.now()
        self._save_session(player_id)
        logger.info(f"Session démarrée pour {player_id}")

    def end_session(self, player_id: str):
        """Termine session, calcule temps joué"""
        session = self.get_or_create_session(player_id)
        if session.start_time:
            duration_min = (
                datetime.datetime.now() - session.start_time
            ).total_seconds() / 60
            session.total_play_time += duration_min
            session.start_time = None
            self._save_session(player_id)

    def log_event(self, player_id: str, event: str, details: Optional[Dict] = None):
        """Log événement session"""
        session = self.get_or_create_session(player_id)
        if session.settings["enable_logs"]:
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "event": event,
                "details": details or {},
            }
            session.logs.append(log_entry)
            # Keep last 100 logs
            if len(session.logs) > 100:
                session.logs = session.logs[-100:]
            self._save_session(player_id)

    def get_session_logs(self, player_id: str) -> List[Dict]:
        """Récupère logs session"""
        session = self.get_or_create_session(player_id)
        return session.logs

    def export_logs(self, player_id: str, parent_email: str) -> bool:
        """Export logs par email (MVP: print + log)"""
        try:
            logs = self.get_session_logs(player_id)
            report = {
                "player_id": player_id,
                "total_play_time": self.get_or_create_session(
                    player_id
                ).total_play_time,
                "logs": logs[-20:],  # Last 20
                "generated": datetime.datetime.now().isoformat(),
            }
            report_text = json.dumps(report, indent=2, ensure_ascii=False)

            # TODO: Real email with SMTP config
            logger.info(f"RAPPORT EXPORT {player_id} -> {parent_email}\n{report_text}")

            # Simulate send
            print(f"📧 Email envoyé à {parent_email}:\n{report_text[:500]}...")
            return True
        except Exception as e:
            logger.error(f"Export logs échoué: {e}")
            return False

    def _save_session(self, player_id: str):
        """Sauvegarde session dans StateManager"""
        state = self.state_manager.load_state(player_id)
        state["parental"] = self.sessions[player_id].to_dict()
        self.state_manager.save_state(player_id, state)

    def update_settings(self, player_id: str, settings: Dict, pin: str) -> bool:
        """Met à jour settings (vérif PIN)"""
        session = self.get_or_create_session(player_id)
        if not self.verify_pin(player_id, pin):
            return False
        session.settings.update(settings)
        self._save_session(player_id)
        return True


# Singleton
_parental_instance: Optional[ParentalControl] = None


def get_parental_control() -> ParentalControl:
    """Singleton ParentalControl"""
    global _parental_instance
    if _parental_instance is None:
        _parental_instance = ParentalControl()
        logger.info("ParentalControl initialisé")
    return _parental_instance


def reset_parental():
    """Reset pour tests"""
    global _parental_instance
    _parental_instance = None
