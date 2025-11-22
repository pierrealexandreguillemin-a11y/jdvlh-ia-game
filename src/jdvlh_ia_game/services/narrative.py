import asyncio
import json
from typing import Any, Dict, List
from pathlib import Path

import ollama
import yaml

from .model_router import get_router
from .narrative_memory import NarrativeMemory, SmartHistoryManager

# Chemin absolu vers config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class NarrativeService:
    def __init__(self):
        self.model = config["ollama"]["model"]
        self.max_retries = config["ollama"]["max_retries"]
        self.temperature = config["ollama"]["temperature"]
        self.max_tokens = config["ollama"]["max_tokens"]
        self.router = get_router()
        self.memory = NarrativeMemory()
        self.history_mgr = SmartHistoryManager()

    async def generate(
        self, context: str, history: List[str], choice: str, blacklist_words: List[str]
    ) -> Dict[str, Any]:
        # AVANT génération
        self.memory.update_entities(choice)
        self.memory.advance_turn()
        smart_context = self.history_mgr.get_smart_context(self.memory)

        smart_history = "\n".join(smart_context[-5:]) if smart_context else ""
        prompt = f"""Tu es MJ Tolkien enfants 10 ans. Ton positif.

Mémoire: {self.memory.get_context_summary()[:100]}

Récemment: {smart_history}

Choix: {choice}

JSON SEULEMENT:
{{
  "narrative": "1-2 phrases courtes",
  "choices": ["Continuer","Explorer","Autre"],
  "location": "la Comté|Fondcombe|Moria|...",
  "animation_trigger": "none",
  "sfx": "ambient"
}}"""


        fallback = {
            "narrative": "L'aventure continue de manière mystérieuse...",
            "choices": ["Continuer", "Explorer", "Retourner"],
            "location": "la Comté",
            "animation_trigger": "none",
            "sfx": "ambient",
        }

        for attempt in range(self.max_retries):
            try:
                model, options = self.router.select_model(
                    prompt=choice, context=context
                )
                resp = ollama.generate(model=model, prompt=prompt, options=options)[
                    "response"
                ]
                parsed = json.loads(resp)

                # APRÈS génération
                self.memory.update_entities(parsed["narrative"])
                self.history_mgr.add_interaction(choice, parsed["narrative"])

                event = self.memory.detect_important_events(parsed["narrative"])
                if event and event.importance >= 4:
                    self.memory.add_event(
                        description=event.description,
                        location=parsed.get("location", ""),
                        entities=event.entities_involved,
                        importance=event.importance,
                    )

                # Mettre à jour lieu
                if parsed.get("location"):
                    self.memory.update_location(parsed["location"])

                if not self._is_safe(parsed.get("narrative", ""), blacklist_words):
                    parsed["narrative"] = (
                        "Choix non adapté aux enfants, essaie autre chose !"
                    )
                parsed["choices"] = parsed.get("choices", fallback["choices"])[:3]
                return parsed
            except Exception as e:
                print(f"Tentative {attempt+1} échouée: {e}")
                if attempt == self.max_retries - 1:
                    return fallback
                await asyncio.sleep(2**attempt)

        return fallback

    def _is_safe(self, text: str, blacklist_words: List[str]) -> bool:
        text_lower = text.lower()
        for word in blacklist_words:
            if word.lower() in text_lower:
                return False
        return True
