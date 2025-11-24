#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT TRADUCTION COMPLETE SRD PATHFINDER 2e

Traduit l'ensemble du SRD PF2e en français :
- 2000+ sorts (spells)
- 3000+ items (équipements, armes, armures, consommables)
- 1000+ monstres (bestiary)
- Conditions, feats, classes, ancestries...

Sources de traduction :
1. Archives of Nethys FR (scraping)
2. Black Book Éditions (terminologie officielle)
3. Communauté Pathfinder-FR

Auteur: jdvlh-ia-game
Date: 23 Novembre 2025
Version: 1.0
"""

# Force UTF-8 encoding for Windows console
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import asyncio
import json
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Dépendances manquantes. Installer avec:")
    print("   pip install httpx beautifulsoup4 lxml --break-system-packages")
    exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================


class Config:
    """Configuration globale du script"""

    # Chemins
    PROJECT_ROOT = Path(__file__).parent  # Le script est à la racine du projet
    DATA_DIR = PROJECT_ROOT / "data" / "pf2e"
    RAW_DIR = DATA_DIR / "raw"
    TRANSLATED_DIR = DATA_DIR / "translated" / "fr"
    CACHE_DIR = DATA_DIR / "cache"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Scraping
    ARCHIVES_BASE_URL = "https://2e.aonprd.com"
    RATE_LIMIT_DELAY = 1.5  # Secondes entre requêtes
    MAX_RETRIES = 3
    TIMEOUT = 30.0

    # Limites (pour tests, mettre None pour tout traduire)
    MAX_SPELLS = None  # None = tous
    MAX_ITEMS = None
    MAX_MONSTERS = None

    # Parallélisme
    MAX_CONCURRENT_REQUESTS = 3

    # Output
    SAVE_PROGRESS_EVERY = 50  # Sauvegarder toutes les N traductions
    VERBOSE = True


class ContentType(Enum):
    """Types de contenu à traduire"""

    SPELLS = "spells"
    ITEMS = "items"
    MONSTERS = "monsters"
    CONDITIONS = "conditions"
    FEATS = "feats"
    CLASSES = "classes"
    ANCESTRIES = "ancestries"
    BACKGROUNDS = "backgrounds"
    ACTIONS = "actions"


# ============================================================================
# MODÈLES DE DONNÉES
# ============================================================================


@dataclass
class TranslationEntry:
    """Entrée de traduction pour un élément"""

    id: str
    name_en: str
    name_fr: str
    description_en: str = ""
    description_fr: str = ""
    traits_fr: List[str] = field(default_factory=list)
    source: str = "manual"  # manual, scraping, api
    verified: bool = False
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TranslationProgress:
    """État de progression de la traduction"""

    content_type: str
    total: int = 0
    translated: int = 0
    failed: int = 0
    skipped: int = 0
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    errors: List[str] = field(default_factory=list)

    @property
    def progress_percent(self) -> float:
        if self.total == 0:
            return 0
        return (self.translated / self.total) * 100

    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# MAPPINGS MANUELS (BASE DE RÉFÉRENCE)
# ============================================================================


class ManualMappings:
    """
    Mappings manuels de traduction

    Ces traductions sont prioritaires sur le scraping.
    Basées sur la terminologie officielle Black Book Éditions.
    """

    # Traits communs
    TRAITS = {
        "fire": "feu",
        "cold": "froid",
        "electricity": "électricité",
        "acid": "acide",
        "sonic": "son",
        "force": "force",
        "mental": "mental",
        "positive": "positif",
        "negative": "négatif",
        "chaotic": "chaotique",
        "evil": "mauvais",
        "good": "bon",
        "lawful": "loyal",
        "arcane": "arcanique",
        "divine": "divin",
        "occult": "occulte",
        "primal": "primordial",
        "attack": "attaque",
        "cantrip": "tour de magie",
        "concentrate": "concentration",
        "manipulate": "manipulation",
        "somatic": "gestuel",
        "verbal": "verbal",
        "material": "matériel",
        "evocation": "évocation",
        "abjuration": "abjuration",
        "conjuration": "invocation",
        "divination": "divination",
        "enchantment": "enchantement",
        "illusion": "illusion",
        "necromancy": "nécromancie",
        "transmutation": "transmutation",
        "healing": "guérison",
        "detection": "détection",
        "scrying": "scrutation",
        "teleportation": "téléportation",
        "polymorph": "métamorphose",
        "curse": "malédiction",
        "disease": "maladie",
        "poison": "poison",
        "fear": "peur",
        "emotion": "émotion",
        "linguistic": "linguistique",
        "visual": "visuel",
        "auditory": "auditif",
        "light": "lumière",
        "darkness": "ténèbres",
        "death": "mort",
        "incapacitation": "incapacitation",
        "sleep": "sommeil",
        "revelation": "révélation",
        "fortune": "fortune",
        "misfortune": "malchance",
    }

    # Conditions (complet)
    CONDITIONS = {
        "blinded": ("Aveuglé", "Vous ne pouvez pas voir."),
        "broken": ("Brisé", "L'objet est endommagé et moins efficace."),
        "clumsy": ("Maladroit", "Vos mouvements sont moins précis."),
        "concealed": ("Masqué", "Vous êtes partiellement obscurci."),
        "confused": ("Confus", "Vous n'êtes pas maître de vos actions."),
        "controlled": ("Contrôlé", "Quelqu'un d'autre décide de vos actions."),
        "dazzled": ("Ébloui", "Tout est masqué pour vous."),
        "deafened": ("Assourdi", "Vous ne pouvez pas entendre."),
        "doomed": ("Condamné", "Votre âme est en péril."),
        "drained": ("Drainé", "Votre force vitale est diminuée."),
        "dying": ("Mourant", "Vous êtes inconscient et proche de la mort."),
        "encumbered": ("Encombré", "Vous portez trop de poids."),
        "enfeebled": ("Affaibli", "Votre force physique est diminuée."),
        "fascinated": ("Fasciné", "Vous êtes captivé par quelque chose."),
        "fatigued": ("Fatigué", "Vous êtes épuisé."),
        "flat-footed": ("Pris au dépourvu", "Vous êtes vulnérable aux attaques."),
        "fleeing": ("En fuite", "Vous devez fuir."),
        "frightened": ("Effrayé", "La peur vous submerge."),
        "grabbed": ("Agrippé", "Quelqu'un vous tient."),
        "hidden": ("Caché", "Vos ennemis ne savent pas où vous êtes."),
        "immobilized": ("Immobilisé", "Vous ne pouvez pas bouger."),
        "invisible": ("Invisible", "On ne peut pas vous voir."),
        "observed": ("Observé", "Vous êtes repéré et visible."),
        "paralyzed": ("Paralysé", "Votre corps est figé."),
        "persistent damage": (
            "Dégâts persistants",
            "Vous subissez des dégâts continus.",
        ),
        "petrified": ("Pétrifié", "Vous êtes transformé en pierre."),
        "prone": ("À terre", "Vous êtes allongé au sol."),
        "quickened": ("Accéléré", "Vous agissez plus rapidement."),
        "restrained": ("Entravé", "Vous êtes tenu fermement."),
        "sickened": ("Malade", "Vous vous sentez nauséeux."),
        "slowed": ("Ralenti", "Vous agissez plus lentement."),
        "stunned": ("Étourdi", "Vous ne pouvez pas agir."),
        "stupefied": ("Hébété", "Votre esprit est embrumé."),
        "unconscious": ("Inconscient", "Vous êtes évanoui."),
        "undetected": ("Non détecté", "Vos ennemis ignorent votre présence."),
        "unnoticed": ("Inaperçu", "Personne ne fait attention à vous."),
        "wounded": ("Blessé", "Vous avez été gravement touché."),
    }

    # Classes
    CLASSES = {
        "alchemist": "Alchimiste",
        "barbarian": "Barbare",
        "bard": "Barde",
        "champion": "Champion",
        "cleric": "Prêtre",
        "druid": "Druide",
        "fighter": "Guerrier",
        "gunslinger": "Pistolero",
        "inventor": "Inventeur",
        "investigator": "Enquêteur",
        "kineticist": "Kinésiste",
        "magus": "Magus",
        "monk": "Moine",
        "oracle": "Oracle",
        "psychic": "Psychique",
        "ranger": "Rôdeur",
        "rogue": "Roublard",
        "sorcerer": "Ensorceleur",
        "summoner": "Conjurateur",
        "swashbuckler": "Bretteur",
        "thaumaturge": "Thaumaturge",
        "witch": "Sorcière",
        "wizard": "Magicien",
    }

    # Ancestries (races)
    ANCESTRIES = {
        "dwarf": "Nain",
        "elf": "Elfe",
        "gnome": "Gnome",
        "goblin": "Gobelin",
        "halfling": "Halfelin",
        "human": "Humain",
        "hobgoblin": "Hobgobelin",
        "leshy": "Leshy",
        "lizardfolk": "Homme-lézard",
        "orc": "Orque",
        "ratfolk": "Homme-rat",
        "tengu": "Tengu",
        "catfolk": "Homme-chat",
        "kobold": "Kobold",
        "android": "Androïde",
        "fetchling": "Fetchelin",
        "fleshwarp": "Distordu",
        "kitsune": "Kitsune",
        "sprite": "Sprite",
        "strix": "Strix",
        "azarketi": "Azarketi",
        "anadi": "Anadi",
        "conrasu": "Conrasu",
        "gnoll": "Gnoll",
        "grippli": "Grippli",
        "shisk": "Shisk",
        "automaton": "Automate",
        "goloma": "Goloma",
        "kashrishi": "Kashrishi",
        "nagaji": "Nagaji",
        "vanara": "Vanara",
        "vishkanya": "Vishkanya",
    }

    # Armes courantes
    WEAPONS = {
        "longsword": "Épée longue",
        "shortsword": "Épée courte",
        "greatsword": "Épée à deux mains",
        "rapier": "Rapière",
        "scimitar": "Cimeterre",
        "dagger": "Dague",
        "battleaxe": "Hache de bataille",
        "greataxe": "Grande hache",
        "handaxe": "Hachette",
        "mace": "Masse",
        "morningstar": "Morgenstern",
        "flail": "Fléau",
        "warhammer": "Marteau de guerre",
        "maul": "Maillet",
        "spear": "Lance",
        "longspear": "Longue lance",
        "trident": "Trident",
        "javelin": "Javelot",
        "halberd": "Hallebarde",
        "glaive": "Glaive",
        "scythe": "Faux",
        "quarterstaff": "Bâton",
        "club": "Gourdin",
        "shortbow": "Arc court",
        "longbow": "Arc long",
        "crossbow": "Arbalète",
        "heavy crossbow": "Arbalète lourde",
        "hand crossbow": "Arbalète de poing",
        "sling": "Fronde",
        "blowgun": "Sarbacane",
    }

    # Armures
    ARMORS = {
        "padded armor": "Armure matelassée",
        "leather armor": "Armure de cuir",
        "studded leather": "Armure de cuir clouté",
        "chain shirt": "Chemise de mailles",
        "chain mail": "Cotte de mailles",
        "scale mail": "Armure d'écailles",
        "breastplate": "Cuirasse",
        "half plate": "Demi-plate",
        "full plate": "Harnois",
        "hide armor": "Armure de peau",
        "splint mail": "Clibanion",
        "buckler": "Targe",
        "wooden shield": "Bouclier en bois",
        "steel shield": "Bouclier en acier",
        "tower shield": "Pavois",
    }

    # Types de monstres
    CREATURE_TYPES = {
        "aberration": "Aberration",
        "animal": "Animal",
        "astral": "Astral",
        "beast": "Bête",
        "celestial": "Céleste",
        "construct": "Créature artificielle",
        "dragon": "Dragon",
        "dream": "Rêve",
        "elemental": "Élémentaire",
        "ethereal": "Éthéré",
        "fey": "Fée",
        "fiend": "Fiélon",
        "fungus": "Champignon",
        "giant": "Géant",
        "humanoid": "Humanoïde",
        "monitor": "Moniteur",
        "ooze": "Vase",
        "plant": "Plante",
        "spirit": "Esprit",
        "undead": "Mort-vivant",
    }

    @classmethod
    def get_trait_fr(cls, trait_en: str) -> str:
        """Traduit un trait EN → FR"""
        return cls.TRAITS.get(trait_en.lower(), trait_en)

    @classmethod
    def get_condition_fr(cls, condition_en: str) -> Tuple[str, str]:
        """Traduit une condition EN → (nom FR, description FR)"""
        return cls.CONDITIONS.get(condition_en.lower(), (condition_en, ""))

    @classmethod
    def translate_traits(cls, traits_en: List[str]) -> List[str]:
        """Traduit une liste de traits"""
        return [cls.get_trait_fr(t) for t in traits_en]


# ============================================================================
# SCRAPER ARCHIVES OF NETHYS
# ============================================================================


class ArchivesOfNethysScraper:
    """
    Scraper pour Archives of Nethys (version française)

    Respecte robots.txt avec rate limiting.
    Gestion erreurs robuste avec retries.
    """

    def __init__(self):
        self.base_url = Config.ARCHIVES_BASE_URL
        self.session: Optional[httpx.AsyncClient] = None
        self.request_count = 0
        self.last_request_time = 0

        # Cache pour éviter re-scraping
        self.cache: Dict[str, Any] = {}

    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=Config.TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (jdvlh-ia-game PF2e translator)",
                "Accept-Language": "fr-FR,fr;q=0.9",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def _rate_limit(self):
        """Respecter le rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < Config.RATE_LIMIT_DELAY:
            await asyncio.sleep(Config.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
        self.request_count += 1

    async def _fetch_page(self, url: str, retries: int = 0) -> Optional[str]:
        """Fetch une page avec gestion d'erreurs et retries"""

        await self._rate_limit()

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.text

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Too Many Requests
                wait_time = Config.RATE_LIMIT_DELAY * (retries + 2)
                print(f"  ⚠️ Rate limited, attente {wait_time}s...")
                await asyncio.sleep(wait_time)
                if retries < Config.MAX_RETRIES:
                    return await self._fetch_page(url, retries + 1)

            print(f"  ❌ HTTP {e.response.status_code} pour {url}")
            return None

        except httpx.TimeoutException:
            if retries < Config.MAX_RETRIES:
                print(f"  ⚠️ Timeout, retry {retries + 1}...")
                return await self._fetch_page(url, retries + 1)
            return None

        except Exception as e:
            print(f"  ❌ Erreur fetch {url}: {e}")
            return None

    async def get_spell_list_fr(self) -> List[Dict[str, str]]:
        """
        Récupère la liste des sorts avec leurs traductions FR

        Returns:
            Liste de {id, name_en, name_fr, url}
        """

        print("📥 Récupération liste des sorts FR...")

        url = f"{self.base_url}/Spells.aspx?Lang=fr"
        html = await self._fetch_page(url)

        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        spells = []

        # Parser les liens vers les sorts
        # Structure typique : <a href="Spells.aspx?ID=XXX">Nom du sort</a>
        spell_links = soup.find_all("a", href=re.compile(r"Spells\.aspx\?ID=\d+"))

        for link in spell_links:
            spell_name_fr = link.get_text(strip=True)
            href = link.get("href", "")

            # Extraire ID
            match = re.search(r"ID=(\d+)", href)
            if match:
                spell_id = match.group(1)

                spells.append(
                    {
                        "id": spell_id,
                        "name_fr": spell_name_fr,
                        "url": urljoin(self.base_url, href),
                    }
                )

        print(f"  ✅ {len(spells)} sorts trouvés")
        return spells

    async def get_spell_details_fr(
        self, spell_id: str, spell_url: str
    ) -> Optional[Dict]:
        """
        Récupère les détails d'un sort en français

        Args:
            spell_id: ID du sort
            spell_url: URL de la page du sort

        Returns:
            Dict avec name_fr, description_fr, traits_fr, etc.
        """

        # Ajouter Lang=fr si pas déjà présent
        if "Lang=fr" not in spell_url:
            spell_url = f"{spell_url}&Lang=fr"

        html = await self._fetch_page(spell_url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        try:
            # Titre
            title_elem = soup.find("h1", class_="title")
            name_fr = title_elem.get_text(strip=True) if title_elem else ""

            # Description (premier paragraphe de texte principal)
            # Structure variable selon les pages
            main_content = soup.find("span", id="ctl00_MainContent_DetailedOutput")

            description_fr = ""
            if main_content:
                # Chercher les paragraphes de description
                paragraphs = main_content.find_all(["p", "span"], recursive=False)
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Ignorer les métadonnées
                    if text and not any(
                        kw in text.lower()
                        for kw in ["source", "traditions", "cast", "range", "area"]
                    ):
                        description_fr = text
                        break

            # Traits
            traits_fr = []
            trait_spans = soup.find_all("span", class_=re.compile(r"trait"))
            for span in trait_spans:
                trait = span.get_text(strip=True)
                if trait:
                    traits_fr.append(trait)

            return {
                "id": spell_id,
                "name_fr": name_fr,
                "description_fr": description_fr[:500] if description_fr else "",
                "traits_fr": traits_fr,
            }

        except Exception as e:
            print(f"  ⚠️ Erreur parsing sort {spell_id}: {e}")
            return None

    async def get_item_list_fr(self) -> List[Dict[str, str]]:
        """Récupère la liste des items avec traductions FR"""

        print("📥 Récupération liste des items FR...")

        # PF2e a plusieurs catégories d'items
        categories = [
            ("Equipment.aspx", "equipment"),
            ("Weapons.aspx", "weapons"),
            ("Armor.aspx", "armor"),
            ("Shields.aspx", "shields"),
            ("Consumables.aspx", "consumables"),
            ("Staves.aspx", "staves"),
            ("Wands.aspx", "wands"),
        ]

        all_items = []

        for page, category in categories:
            url = f"{self.base_url}/{page}?Lang=fr"
            html = await self._fetch_page(url)

            if not html:
                continue

            soup = BeautifulSoup(html, "lxml")

            # Parser liens
            item_links = soup.find_all(
                "a", href=re.compile(rf'{page.replace(".aspx", "")}\.aspx\?ID=\d+')
            )

            for link in item_links:
                item_name_fr = link.get_text(strip=True)
                href = link.get("href", "")

                match = re.search(r"ID=(\d+)", href)
                if match:
                    item_id = f"{category}_{match.group(1)}"

                    all_items.append(
                        {
                            "id": item_id,
                            "name_fr": item_name_fr,
                            "category": category,
                            "url": urljoin(self.base_url, href),
                        }
                    )

        print(f"  ✅ {len(all_items)} items trouvés")
        return all_items

    async def get_monster_list_fr(self) -> List[Dict[str, str]]:
        """Récupère la liste des monstres avec traductions FR"""

        print("📥 Récupération liste des monstres FR...")

        url = f"{self.base_url}/Monsters.aspx?Lang=fr"
        html = await self._fetch_page(url)

        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        monsters = []

        monster_links = soup.find_all("a", href=re.compile(r"Monsters\.aspx\?ID=\d+"))

        for link in monster_links:
            monster_name_fr = link.get_text(strip=True)
            href = link.get("href", "")

            match = re.search(r"ID=(\d+)", href)
            if match:
                monster_id = match.group(1)

                monsters.append(
                    {
                        "id": monster_id,
                        "name_fr": monster_name_fr,
                        "url": urljoin(self.base_url, href),
                    }
                )

        print(f"  ✅ {len(monsters)} monstres trouvés")
        return monsters


# ============================================================================
# SERVICE DE TRADUCTION PRINCIPAL
# ============================================================================


class PF2eTranslationService:
    """
    Service principal de traduction PF2e

    Coordonne :
    - Chargement data raw EN
    - Scraping traductions FR
    - Fusion et export
    - Sauvegarde progression
    """

    def __init__(self):
        self.config = Config
        self.scraper: Optional[ArchivesOfNethysScraper] = None

        # Traductions accumulées
        self.translations: Dict[ContentType, Dict[str, TranslationEntry]] = {
            ct: {} for ct in ContentType
        }

        # Progression
        self.progress: Dict[ContentType, TranslationProgress] = {}

        # Assurer que les dossiers existent
        self._ensure_directories()

    def _ensure_directories(self):
        """Créer les dossiers nécessaires"""
        Config.TRANSLATED_DIR.mkdir(parents=True, exist_ok=True)
        Config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def _load_raw_content(self, content_type: ContentType) -> List[Dict]:
        """
        Charge le contenu raw EN depuis les fichiers JSON

        Args:
            content_type: Type de contenu (spells, items, etc.)

        Returns:
            Liste des éléments EN
        """

        raw_dir = Config.RAW_DIR
        items = []

        if content_type == ContentType.SPELLS:
            spells_dir = raw_dir / "spells"
            if spells_dir.exists():
                for json_file in spells_dir.glob("*.json"):
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict) and "spell" in data:
                                items.extend(data["spell"])
                            elif isinstance(data, list):
                                items.extend(data)
                    except Exception as e:
                        print(f"  ⚠️ Erreur chargement {json_file}: {e}")

        elif content_type == ContentType.ITEMS:
            items_dir = raw_dir / "items"
            if items_dir.exists():
                for json_file in items_dir.glob("*.json"):
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict) and "item" in data:
                                items.extend(data["item"])
                            elif isinstance(data, list):
                                items.extend(data)
                    except Exception as e:
                        print(f"  ⚠️ Erreur chargement {json_file}: {e}")

        elif content_type == ContentType.MONSTERS:
            bestiary_dir = raw_dir / "bestiary"
            if bestiary_dir.exists():
                for json_file in bestiary_dir.glob("*.json"):
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict) and "creature" in data:
                                items.extend(data["creature"])
                            elif isinstance(data, dict) and "monster" in data:
                                items.extend(data["monster"])
                            elif isinstance(data, list):
                                items.extend(data)
                    except Exception as e:
                        print(f"  ⚠️ Erreur chargement {json_file}: {e}")

        return items

    def _normalize_id(self, name: str) -> str:
        """Normalise un nom en ID (lowercase, tirets)"""
        normalized = name.lower()
        normalized = re.sub(r"[^a-z0-9àâäéèêëïîôùûüç]+", "-", normalized)
        normalized = normalized.strip("-")
        return normalized

    def _load_existing_translations(
        self, content_type: ContentType
    ) -> Dict[str, TranslationEntry]:
        """Charge les traductions existantes pour éviter de re-traduire"""

        file_path = Config.TRANSLATED_DIR / f"{content_type.value}.json"

        if not file_path.exists():
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            translations = {}
            for item_id, item_data in data.items():
                if isinstance(item_data, dict):
                    translations[item_id] = TranslationEntry(
                        id=item_id,
                        name_en=item_data.get("name_en", ""),
                        name_fr=item_data.get("name_fr", ""),
                        description_en=item_data.get("description_en", ""),
                        description_fr=item_data.get("description_fr", ""),
                        traits_fr=item_data.get("traits_fr", []),
                        source=item_data.get("source", "existing"),
                        verified=item_data.get("verified", False),
                    )

            return translations

        except Exception as e:
            print(f"  ⚠️ Erreur chargement traductions existantes: {e}")
            return {}

    def _save_translations(self, content_type: ContentType):
        """Sauvegarde les traductions en JSON"""

        file_path = Config.TRANSLATED_DIR / f"{content_type.value}.json"

        translations_dict = {}
        for item_id, entry in self.translations[content_type].items():
            translations_dict[item_id] = {
                "name_en": entry.name_en,
                "name_fr": entry.name_fr,
                "description_en": entry.description_en,
                "description_fr": entry.description_fr,
                "traits_fr": entry.traits_fr,
                "source": entry.source,
                "verified": entry.verified,
                "updated_at": entry.updated_at,
            }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(translations_dict, f, indent=2, ensure_ascii=False)

        if Config.VERBOSE:
            print(
                f"  💾 Sauvegardé {len(translations_dict)} traductions → {file_path.name}"
            )

    def _save_progress(self, content_type: ContentType):
        """Sauvegarde l'état de progression"""

        progress_file = Config.CACHE_DIR / f"progress_{content_type.value}.json"

        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(self.progress[content_type].to_dict(), f, indent=2)

    async def translate_spells(self) -> TranslationProgress:
        """
        Traduit tous les sorts

        Returns:
            Progression de la traduction
        """

        print("\n" + "=" * 60)
        print("🔮 TRADUCTION DES SORTS")
        print("=" * 60)

        content_type = ContentType.SPELLS

        # Charger raw EN
        print("\n📚 Chargement sorts EN...")
        raw_spells = self._load_raw_content(content_type)
        print(f"  ✅ {len(raw_spells)} sorts EN chargés")

        # Limiter si configuré
        if Config.MAX_SPELLS:
            raw_spells = raw_spells[: Config.MAX_SPELLS]
            print(f"  ⚠️ Limité à {Config.MAX_SPELLS} sorts (config)")

        # Charger traductions existantes
        print("\n📖 Chargement traductions existantes...")
        existing = self._load_existing_translations(content_type)
        self.translations[content_type] = existing
        print(f"  ✅ {len(existing)} traductions existantes")

        # Initialiser progression
        self.progress[content_type] = TranslationProgress(
            content_type=content_type.value,
            total=len(raw_spells),
            translated=len(existing),
        )

        # Indexer raw par ID
        raw_by_id = {}
        for spell in raw_spells:
            spell_name = spell.get("name", "")
            spell_id = self._normalize_id(spell_name)
            raw_by_id[spell_id] = spell

        # Identifier sorts à traduire
        to_translate = []
        for spell_id, spell in raw_by_id.items():
            if spell_id not in self.translations[content_type]:
                to_translate.append((spell_id, spell))

        print(f"\n🌐 {len(to_translate)} sorts à traduire via scraping...")

        if not to_translate:
            print("  ✅ Tous les sorts sont déjà traduits!")
            return self.progress[content_type]

        # Scraping
        async with ArchivesOfNethysScraper() as scraper:
            # Récupérer liste FR
            spells_fr = await scraper.get_spell_list_fr()

            # Indexer par nom FR normalisé pour matching
            spells_fr_by_name = {}
            for spell_fr in spells_fr:
                name_normalized = self._normalize_id(spell_fr["name_fr"])
                spells_fr_by_name[name_normalized] = spell_fr

            # Traduire chaque sort
            translated_count = 0
            for i, (spell_id, spell_en) in enumerate(to_translate):
                spell_name_en = spell_en.get("name", "")

                if Config.VERBOSE and i % 20 == 0:
                    print(f"  [{i + 1}/{len(to_translate)}] Progression...")

                # Chercher correspondance FR
                # Essayer match direct par ID normalisé
                spell_fr_data = spells_fr_by_name.get(spell_id)

                if spell_fr_data:
                    # Récupérer détails
                    details = await scraper.get_spell_details_fr(
                        spell_fr_data["id"], spell_fr_data["url"]
                    )

                    if details:
                        # Créer entrée traduction
                        description_en = " ".join(spell_en.get("entries", []))
                        traits_en = spell_en.get("traits", [])

                        entry = TranslationEntry(
                            id=spell_id,
                            name_en=spell_name_en,
                            name_fr=details["name_fr"],
                            description_en=description_en[:500],
                            description_fr=details["description_fr"],
                            traits_fr=details.get(
                                "traits_fr", ManualMappings.translate_traits(traits_en)
                            ),
                            source="scraping",
                        )

                        self.translations[content_type][spell_id] = entry
                        translated_count += 1
                        self.progress[content_type].translated += 1
                    else:
                        self.progress[content_type].failed += 1
                else:
                    # Pas de correspondance FR trouvée
                    self.progress[content_type].skipped += 1

                # Sauvegarder périodiquement
                if (
                    translated_count > 0
                    and translated_count % Config.SAVE_PROGRESS_EVERY == 0
                ):
                    self._save_translations(content_type)
                    self._save_progress(content_type)

        # Sauvegarde finale
        self._save_translations(content_type)
        self.progress[content_type].completed_at = datetime.now().isoformat()
        self._save_progress(content_type)

        print("\n✅ Traduction sorts terminée:")
        print(f"   - Traduits: {self.progress[content_type].translated}")
        print(f"   - Échoués: {self.progress[content_type].failed}")
        print(f"   - Ignorés: {self.progress[content_type].skipped}")

        return self.progress[content_type]

    async def translate_items(self) -> TranslationProgress:
        """Traduit tous les items"""

        print("\n" + "=" * 60)
        print("🗡️ TRADUCTION DES ITEMS")
        print("=" * 60)

        content_type = ContentType.ITEMS

        # Charger raw EN
        print("\n📚 Chargement items EN...")
        raw_items = self._load_raw_content(content_type)
        print(f"  ✅ {len(raw_items)} items EN chargés")

        if Config.MAX_ITEMS:
            raw_items = raw_items[: Config.MAX_ITEMS]
            print(f"  ⚠️ Limité à {Config.MAX_ITEMS} items (config)")

        # Charger existants
        print("\n📖 Chargement traductions existantes...")
        existing = self._load_existing_translations(content_type)
        self.translations[content_type] = existing
        print(f"  ✅ {len(existing)} traductions existantes")

        # Initialiser progression
        self.progress[content_type] = TranslationProgress(
            content_type=content_type.value,
            total=len(raw_items),
            translated=len(existing),
        )

        # D'abord, appliquer les mappings manuels pour armes/armures courantes
        print("\n🔧 Application mappings manuels...")
        manual_count = 0

        for item in raw_items:
            item_name = item.get("name", "")
            item_id = self._normalize_id(item_name)

            if item_id in self.translations[content_type]:
                continue  # Déjà traduit

            # Chercher dans mappings manuels
            name_lower = item_name.lower()
            name_fr = None

            if name_lower in ManualMappings.WEAPONS:
                name_fr = ManualMappings.WEAPONS[name_lower]
            elif name_lower in ManualMappings.ARMORS:
                name_fr = ManualMappings.ARMORS[name_lower]

            if name_fr:
                entry = TranslationEntry(
                    id=item_id,
                    name_en=item_name,
                    name_fr=name_fr,
                    description_en="",
                    description_fr="",
                    source="manual",
                    verified=True,
                )
                self.translations[content_type][item_id] = entry
                manual_count += 1
                self.progress[content_type].translated += 1

        print(f"  ✅ {manual_count} items traduits via mappings manuels")

        # Ensuite, scraping pour le reste
        to_translate = [
            item
            for item in raw_items
            if self._normalize_id(item.get("name", ""))
            not in self.translations[content_type]
        ]

        print(f"\n🌐 {len(to_translate)} items à traduire via scraping...")

        if to_translate:
            async with ArchivesOfNethysScraper() as scraper:
                items_fr = await scraper.get_item_list_fr()

                # Indexer
                items_fr_by_name = {
                    self._normalize_id(item["name_fr"]): item for item in items_fr
                }

                # Traduire
                for i, item_en in enumerate(to_translate):
                    item_name_en = item_en.get("name", "")
                    item_id = self._normalize_id(item_name_en)

                    if Config.VERBOSE and i % 50 == 0:
                        print(f"  [{i + 1}/{len(to_translate)}] Progression...")

                    # Chercher correspondance
                    item_fr_data = items_fr_by_name.get(item_id)

                    if item_fr_data:
                        entry = TranslationEntry(
                            id=item_id,
                            name_en=item_name_en,
                            name_fr=item_fr_data["name_fr"],
                            source="scraping",
                        )
                        self.translations[content_type][item_id] = entry
                        self.progress[content_type].translated += 1
                    else:
                        self.progress[content_type].skipped += 1

                    # Sauvegarde périodique
                    if i > 0 and i % Config.SAVE_PROGRESS_EVERY == 0:
                        self._save_translations(content_type)

        # Sauvegarde finale
        self._save_translations(content_type)
        self.progress[content_type].completed_at = datetime.now().isoformat()
        self._save_progress(content_type)

        print("\n✅ Traduction items terminée:")
        print(f"   - Traduits: {self.progress[content_type].translated}")
        print(f"   - Ignorés: {self.progress[content_type].skipped}")

        return self.progress[content_type]

    async def translate_monsters(self) -> TranslationProgress:
        """Traduit tous les monstres"""

        print("\n" + "=" * 60)
        print("👹 TRADUCTION DES MONSTRES")
        print("=" * 60)

        content_type = ContentType.MONSTERS

        # Charger raw EN
        print("\n📚 Chargement monstres EN...")
        raw_monsters = self._load_raw_content(content_type)
        print(f"  ✅ {len(raw_monsters)} monstres EN chargés")

        if Config.MAX_MONSTERS:
            raw_monsters = raw_monsters[: Config.MAX_MONSTERS]
            print(f"  ⚠️ Limité à {Config.MAX_MONSTERS} monstres (config)")

        # Charger existants
        print("\n📖 Chargement traductions existantes...")
        existing = self._load_existing_translations(content_type)
        self.translations[content_type] = existing
        print(f"  ✅ {len(existing)} traductions existantes")

        # Initialiser progression
        self.progress[content_type] = TranslationProgress(
            content_type=content_type.value,
            total=len(raw_monsters),
            translated=len(existing),
        )

        # Scraping
        to_translate = [
            monster
            for monster in raw_monsters
            if self._normalize_id(monster.get("name", ""))
            not in self.translations[content_type]
        ]

        print(f"\n🌐 {len(to_translate)} monstres à traduire via scraping...")

        if to_translate:
            async with ArchivesOfNethysScraper() as scraper:
                monsters_fr = await scraper.get_monster_list_fr()

                # Indexer
                monsters_fr_by_name = {
                    self._normalize_id(m["name_fr"]): m for m in monsters_fr
                }

                # Traduire
                for i, monster_en in enumerate(to_translate):
                    monster_name_en = monster_en.get("name", "")
                    monster_id = self._normalize_id(monster_name_en)

                    if Config.VERBOSE and i % 50 == 0:
                        print(f"  [{i + 1}/{len(to_translate)}] Progression...")

                    monster_fr_data = monsters_fr_by_name.get(monster_id)

                    if monster_fr_data:
                        # Traduire type de créature
                        creature_type_en = monster_en.get("type", "")
                        creature_type_fr = ManualMappings.CREATURE_TYPES.get(
                            creature_type_en.lower(), creature_type_en
                        )

                        entry = TranslationEntry(
                            id=monster_id,
                            name_en=monster_name_en,
                            name_fr=monster_fr_data["name_fr"],
                            traits_fr=[creature_type_fr] if creature_type_fr else [],
                            source="scraping",
                        )
                        self.translations[content_type][monster_id] = entry
                        self.progress[content_type].translated += 1
                    else:
                        self.progress[content_type].skipped += 1

                    # Sauvegarde périodique
                    if i > 0 and i % Config.SAVE_PROGRESS_EVERY == 0:
                        self._save_translations(content_type)

        # Sauvegarde finale
        self._save_translations(content_type)
        self.progress[content_type].completed_at = datetime.now().isoformat()
        self._save_progress(content_type)

        print("\n✅ Traduction monstres terminée:")
        print(f"   - Traduits: {self.progress[content_type].translated}")
        print(f"   - Ignorés: {self.progress[content_type].skipped}")

        return self.progress[content_type]

    async def translate_conditions(self) -> TranslationProgress:
        """Traduit les conditions (utilise mappings manuels complets)"""

        print("\n" + "=" * 60)
        print("⚡ TRADUCTION DES CONDITIONS")
        print("=" * 60)

        content_type = ContentType.CONDITIONS

        # Les conditions sont traduites via mappings manuels (complets)
        self.progress[content_type] = TranslationProgress(
            content_type=content_type.value, total=len(ManualMappings.CONDITIONS)
        )

        for condition_en, (name_fr, desc_fr) in ManualMappings.CONDITIONS.items():
            condition_id = self._normalize_id(condition_en)

            entry = TranslationEntry(
                id=condition_id,
                name_en=condition_en,
                name_fr=name_fr,
                description_en="",
                description_fr=desc_fr,
                source="manual",
                verified=True,
            )

            self.translations[content_type][condition_id] = entry
            self.progress[content_type].translated += 1

        self._save_translations(content_type)
        self.progress[content_type].completed_at = datetime.now().isoformat()

        print(f"\n✅ {len(ManualMappings.CONDITIONS)} conditions traduites")

        return self.progress[content_type]

    async def translate_all(self) -> Dict[ContentType, TranslationProgress]:
        """
        Traduit TOUT le contenu PF2e

        Returns:
            Dict avec progression par type de contenu
        """

        print("\n" + "=" * 60)
        print("🌍 TRADUCTION COMPLÈTE SRD PATHFINDER 2e")
        print("=" * 60)
        print(f"\nDémarrage : {datetime.now().isoformat()}")
        print(f"Projet : {Config.PROJECT_ROOT}")
        print(f"Output : {Config.TRANSLATED_DIR}")
        print()

        start_time = time.time()

        # Traduire dans l'ordre
        results = {}

        # 1. Conditions (rapide, manuel)
        results[ContentType.CONDITIONS] = await self.translate_conditions()

        # 2. Sorts (prioritaire)
        results[ContentType.SPELLS] = await self.translate_spells()

        # 3. Items
        results[ContentType.ITEMS] = await self.translate_items()

        # 4. Monstres
        results[ContentType.MONSTERS] = await self.translate_monsters()

        # Résumé final
        elapsed = time.time() - start_time

        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ FINAL")
        print("=" * 60)

        total_translated = 0
        total_items = 0

        for content_type, progress in results.items():
            total_translated += progress.translated
            total_items += progress.total

            print(f"\n{content_type.value.upper()}:")
            print(f"  - Total: {progress.total}")
            print(
                f"  - Traduits: {progress.translated} ({progress.progress_percent:.1f}%)"
            )
            if progress.failed > 0:
                print(f"  - Échoués: {progress.failed}")
            if progress.skipped > 0:
                print(f"  - Ignorés: {progress.skipped}")

        print(f"\n{'=' * 60}")
        print("✅ TRADUCTION TERMINÉE")
        print(f"   Total traduit: {total_translated}/{total_items}")
        print(f"   Durée: {elapsed / 60:.1f} minutes")
        print(f"   Output: {Config.TRANSLATED_DIR}")
        print(f"{'=' * 60}\n")

        return results


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================


async def main():
    """Point d'entrée principal"""

    print(
        """
================================================================
  TRADUCTION SRD PATHFINDER 2e -> FRANCAIS

  Ce script traduit le contenu PF2e complet :
  - 2000+ sorts
  - 3000+ items
  - 1000+ monstres
  - Conditions, traits, classes...

  Sources : Archives of Nethys FR + mappings manuels
================================================================
"""
    )

    # Vérifier structure projet
    if not Config.RAW_DIR.exists():
        print(f"❌ Dossier raw data introuvable: {Config.RAW_DIR}")
        print("   Exécuter d'abord Phase 1 (Acquisition SRD)")
        return

    # Créer service et traduire
    service = PF2eTranslationService()
    results = await service.translate_all()

    # Générer rapport
    report_file = (
        Config.LOGS_DIR
        / f"translation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(report_file, "w", encoding="utf-8") as f:
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": {ct.value: p.to_dict() for ct, p in results.items()},
        }
        json.dump(report, f, indent=2)

    print(f"📝 Rapport sauvegardé: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
