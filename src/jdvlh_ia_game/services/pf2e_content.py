"""
Service d'accès contenu Pathfinder 2e

Features :
- Chargement SRD complet
- Traduction FR automatique avec fallback EN
- Feature flags (désactivation progressive)
- Cache en mémoire
"""

from typing import Optional, Dict, List
from pathlib import Path
import json
import yaml
from dataclasses import dataclass
from enum import Enum

from .translation.pf2e_translator import PF2eTranslator


class ContentType(Enum):
    """Types de contenu PF2e"""

    SPELL = "spells"
    ITEM = "items"
    MONSTER = "bestiary"
    FEAT = "feats"
    CONDITION = "conditions"
    CLASS = "classes"
    ANCESTRY = "ancestries"


@dataclass
class PF2eSpell:
    """Modèle spell PF2e"""

    id: str
    name: str
    description: str
    level: int
    traditions: List[str]
    actions: int  # 1, 2, ou 3
    traits: List[str]

    # Combat
    damage: Optional[str] = None  # Ex: "6d6"
    healing: Optional[str] = None
    range: Optional[int] = None
    area: Optional[Dict] = None

    # Metadata
    source: str = "Core Rulebook"
    rarity: str = "common"  # common, uncommon, rare

    @property
    def is_available_mvp(self) -> bool:
        """Disponible en MVP (level <= 3)"""
        return self.level <= 3


@dataclass
class PF2eItem:
    """Modèle item PF2e"""

    id: str
    name: str
    description: str
    type: str  # weapon, armor, consumable, etc.
    level: int
    price: Dict[str, int]  # {"gp": 10}

    # Combat stats (si applicable)
    damage: Optional[str] = None
    armor_class: Optional[int] = None

    traits: List[str] = None
    rarity: str = "common"


@dataclass
class PF2eMonster:
    """Modèle monstre PF2e"""

    id: str
    name: str
    description: str
    level: int

    # Combat stats
    hp: int
    ac: int
    attacks: List[Dict]

    # Abilities
    abilities: Dict[str, int]  # str, dex, con, int, wis, cha

    traits: List[str] = None
    rarity: str = "common"


class PF2eContent:
    """
    Service d'accès contenu PF2e

    Usage:
        content = PF2eContent(language="fr")
        spell = content.get_spell("fireball")
        print(spell.name)  # "Boule de feu"
    """

    def __init__(
        self,
        data_dir: Path = Path("data/pf2e"),
        language: str = "fr",
        config_path: Path = Path(__file__).parent.parent / "config" / "config.yaml",
    ):
        self.data_dir = Path(data_dir)
        self.language = language
        self.config_path = config_path

        # Translator
        self.translator = PF2eTranslator()

        # Cache en mémoire
        self._spells: Dict[str, PF2eSpell] = {}
        self._items: Dict[str, PF2eItem] = {}
        self._monsters: Dict[str, PF2eMonster] = {}

        # Feature flags
        self._feature_config = self._load_feature_config()

        # Charger contenu
        self._load_all_content()

    def _load_feature_config(self) -> Dict:
        """Charger config feature flags depuis config.yaml"""

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            pf2e_config = config.get("pf2e", {})
            active_level = pf2e_config.get("active_level", "mvp")

            levels_config = pf2e_config.get("levels", {})
            feature_config = levels_config.get(active_level, {})

            print(f"[*] Feature level: {active_level}")

            return feature_config
        except Exception as e:
            print(f"[!] Erreur chargement config: {e}, utilisation MVP par défaut")
            return {
                "max_spell_level": 3,
                "max_character_level": 5,
                "enabled_classes": ["fighter", "wizard", "ranger"],
                "complex_conditions": False,
            }

    def _load_all_content(self):
        """Charger tout le contenu au démarrage"""

        print(f"[*] Chargement contenu PF2e (langue: {self.language})...")

        # Charger traductions
        translation_dir = self.data_dir / "translated" / self.language
        if translation_dir.exists():
            self.translator.load_translations(translation_dir)
            print(f"  [+] Traductions {self.language} chargées")
        else:
            print(f"  [!] Pas de traductions {self.language}, fallback EN")

        # Charger sorts
        self._load_spells()

        # TODO : Charger items, monsters, etc.
        print("  [!] Items & monsters non chargés encore")

        print(f"[+] Contenu PF2e chargé : {len(self._spells)} sorts")

    def _load_spells(self):
        """Charger sorts depuis raw data"""

        spells_dir = self.data_dir / "raw" / "spells"

        if not spells_dir.exists():
            print(f"[!] Dossier sorts introuvable: {spells_dir}")
            return

        # Parser tous les fichiers JSON
        for json_file in spells_dir.glob("**/*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Parser selon structure pf2etools
                if isinstance(data, dict) and "spell" in data:
                    spells_list = data["spell"]
                elif isinstance(data, list):
                    spells_list = data
                else:
                    continue

                for spell_data in spells_list:
                    spell = self._parse_spell(spell_data)
                    if spell:
                        self._spells[spell.id] = spell

            except Exception as e:
                print(f"[!] Erreur parsing {json_file}: {e}")
                continue

    def _extract_text_from_entries(self, entries: List) -> str:
        """Extraire texte depuis entries (gère structures complexes)"""
        text_parts = []

        for entry in entries:
            if isinstance(entry, str):
                text_parts.append(entry)
            elif isinstance(entry, dict):
                # Extraire type ou texte si présent
                if "type" in entry:
                    # Structures complexes comme {type: "list", items: [...]}
                    continue  # Ignorer pour simplification MVP
                elif "entries" in entry:
                    # Récursion pour entries imbriqués
                    text_parts.append(self._extract_text_from_entries(entry["entries"]))
                else:
                    # Prendre première valeur string trouvée
                    for value in entry.values():
                        if isinstance(value, str):
                            text_parts.append(value)
                            break

        return " ".join(text_parts)

    def _parse_spell(self, data: Dict) -> Optional[PF2eSpell]:
        """Parser spell depuis JSON PF2e"""

        try:
            spell_id = data.get("name", "").lower().replace(" ", "-")

            # Nom : traduction FR si dispo, sinon EN
            name_en = data.get("name", "Unknown")
            name_fr = self.translator.get_translation("spells", spell_id, "name")
            name = name_fr if name_fr else name_en

            # Description : traduction FR si dispo, sinon EN
            desc_en = self._extract_text_from_entries(data.get("entries", []))
            desc_fr = self.translator.get_translation("spells", spell_id, "description")
            description = desc_fr if desc_fr else desc_en

            # Actions (1, 2, ou 3)
            actions_data = data.get("activity", {})
            if isinstance(actions_data, dict):
                actions = actions_data.get("number", 2)
            else:
                actions = 2  # Default

            spell = PF2eSpell(
                id=spell_id,
                name=name,
                description=description,
                level=data.get("level", 1),
                traditions=data.get("traditions", []),
                actions=actions,
                traits=data.get("traits", []),
                # Damage (si applicable)
                damage=self._extract_damage(data),
                # Metadata
                source=data.get("source", "Unknown"),
                rarity=data.get("rarity", "common"),
            )

            return spell

        except Exception as e:
            print(f"[!] Erreur parsing spell: {e}")
            return None

    def _extract_damage(self, spell_data: Dict) -> Optional[str]:
        """Extraire dégâts d'un sort"""

        # Structure variable selon sorts
        # Exemple : {"damage": {"6d6": ["fire"]}}

        damage_data = spell_data.get("damage")
        if not damage_data:
            return None

        # Simplifier pour MVP (juste les dés)
        if isinstance(damage_data, dict):
            # Prendre première clé
            damage_dice = list(damage_data.keys())[0] if damage_data else None
            return damage_dice

        return None

    def get_spell(self, spell_id: str) -> Optional[PF2eSpell]:
        """
        Récupérer un sort par ID

        Args:
            spell_id: ID du sort (ex: "fireball")

        Returns:
            PF2eSpell ou None si introuvable
        """
        return self._spells.get(spell_id)

    def get_all_spells(
        self, filter_by_level: Optional[int] = None, available_only: bool = False
    ) -> List[PF2eSpell]:
        """
        Liste tous les sorts

        Args:
            filter_by_level: Filtrer par niveau (ex: <= 3 pour MVP)
            available_only: Si True, respecter feature flags

        Returns:
            Liste de PF2eSpell
        """

        spells = list(self._spells.values())

        # Filtrer par niveau
        if filter_by_level is not None:
            spells = [s for s in spells if s.level <= filter_by_level]

        # Filtrer selon feature flags
        if available_only:
            max_level = self._feature_config["max_spell_level"]
            spells = [s for s in spells if s.level <= max_level]

        return spells

    def get_spell_by_name(self, name: str) -> Optional[PF2eSpell]:
        """Récupérer sort par nom (FR ou EN)"""

        name_lower = name.lower()

        for spell in self._spells.values():
            if spell.name.lower() == name_lower:
                return spell

        return None

    def search_spells(self, query: str, limit: int = 10) -> List[PF2eSpell]:
        """
        Recherche sorts par mot-clé

        Args:
            query: Mot-clé (nom ou description)
            limit: Nombre max résultats

        Returns:
            Liste de PF2eSpell
        """

        query_lower = query.lower()
        results = []

        for spell in self._spells.values():
            # Chercher dans nom ou description
            if (
                query_lower in spell.name.lower()
                or query_lower in spell.description.lower()
            ):
                results.append(spell)

                if len(results) >= limit:
                    break

        return results


# Singleton global (optionnel)
_pf2e_content_instance: Optional[PF2eContent] = None


def get_pf2e_content(language: str = "fr") -> PF2eContent:
    """Récupérer instance singleton PF2eContent"""

    global _pf2e_content_instance

    if _pf2e_content_instance is None:
        _pf2e_content_instance = PF2eContent(language=language)

    return _pf2e_content_instance
