import asyncio
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

import ollama
import yaml

from .model_router import get_router
from .narrative_memory import NarrativeMemory, SmartHistoryManager
from .pf2e_content import get_pf2e_content
from .content_filter import get_content_filter

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
        self.content_filter = get_content_filter(target_age=16, strict_mode=True)

        # Intégration PF2e (optionnel)
        try:
            self.pf2e = get_pf2e_content(language="fr")
            print("[+] PF2e content intégré au NarrativeService")
        except Exception as e:
            print(f"[!] PF2e content non disponible: {e}")
            self.pf2e = None

        print("[+] ContentFilter PEGI 16 activé")

    async def generate(
        self, context: str, history: List[str], choice: str, blacklist_words: List[str]
    ) -> Dict[str, Any]:
        # FILTER INPUT: Check player choice for inappropriate content
        input_result = self.content_filter.filter_input(choice)
        if not input_result.is_safe:
            print(f"[!] Input filtré: {input_result.violations}")
            choice = input_result.filtered_text

        # AVANT génération
        self.memory.update_entities(choice)
        self.memory.advance_turn()
        smart_context = self.history_mgr.get_smart_context(self.memory)

        # Enrichissement PF2e si sort détecté
        spell_info = self._extract_spell_info(choice)

        smart_history = "\n".join(smart_context[-5:]) if smart_context else ""

        # Ajouter info sort au prompt si disponible
        spell_context = ""
        if spell_info:
            spell_desc = spell_info["description"][:100]
            spell_context = (
                f"\n\nSort utilisé: {spell_info['name']} "
                f"(niveau {spell_info['level']}) - {spell_desc}"
            )

        prompt = f"""Tu es un Maître du Jeu Pathfinder 2e expert pour adolescents (14-18 ans).
UNIVERS: Golarion - haute fantasy avec magie, dieux et aventures épiques.

STYLE:
- Descriptions immersives (4-6 phrases)
- Combats tactiques avec règles PF2e (3 actions/tour)
- Mentionne jets de dés (d20+mod) et DC appropriés

Mémoire: {self.memory.get_context_summary()[:150]}

Récemment: {smart_history}

Choix du joueur: {choice}{spell_context}

Si jet de dé requis: animation_trigger="DICE_ROLL:skill:DC" (ex: perception:15).

JSON STRICT:
{{
  "narrative": "description immersive 4-6 phrases",
  "choices": ["action1","action2","action3"],
  "location": "Absalom|Sandpoint|Magnimar|...",
  "animation_trigger": "none|DICE_ROLL:skill:DC",
  "sfx": "ambient|combat|magic|tavern"
}}"""

        fallback = {
            "narrative": "Les brumes de Golarion se dissipent, révélant un chemin...",
            "choices": ["Explorer", "Équipement", "Observer"],
            "location": "Absalom",
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

                # FILTER OUTPUT: Check AI response for inappropriate content
                output_result = self.content_filter.filter_output(
                    parsed.get("narrative", "")
                )
                if not output_result.is_safe:
                    print(f"[!] Output filtré: {output_result.violations}")
                    parsed["narrative"] = output_result.filtered_text
                    parsed["content_filtered"] = True

                # Legacy blacklist check (backward compatibility)
                if not self._is_safe(parsed.get("narrative", ""), blacklist_words):
                    parsed["narrative"] = "L'aventure continue paisiblement..."
                    parsed["content_filtered"] = True

                parsed["choices"] = parsed.get("choices", fallback["choices"])[:3]
                return parsed
            except Exception as e:
                print(f"Tentative {attempt + 1} échouée: {e}")
                if attempt == self.max_retries - 1:
                    return fallback
                await asyncio.sleep(2**attempt)

        return fallback

    def _extract_spell_info(self, choice: str) -> Optional[Dict]:
        """
        Extraire informations d'un sort si détecté dans le choix

        Args:
            choice: Le choix du joueur

        Returns:
            Dict avec info sort ou None
        """
        if not self.pf2e or "spell:" not in choice.lower():
            return None

        try:
            # Extraire nom sort après "spell:"
            parts = choice.lower().split("spell:")
            if len(parts) < 2:
                return None

            spell_name = parts[1].strip().split()[0]  # Premier mot après "spell:"

            # Chercher sort par nom
            spell = self.pf2e.get_spell_by_name(spell_name)
            if not spell:
                spell = self.pf2e.get_spell(spell_name)  # Essayer par ID

            if spell:
                return {
                    "name": spell.name,
                    "level": spell.level,
                    "description": spell.description,
                    "damage": spell.damage,
                }
        except Exception as e:
            print(f"[!] Erreur extraction sort: {e}")

        return None

    def _is_safe(self, text: str, blacklist_words: List[str]) -> bool:
        text_lower = text.lower()
        for word in blacklist_words:
            if word.lower() in text_lower:
                return False
        return True
