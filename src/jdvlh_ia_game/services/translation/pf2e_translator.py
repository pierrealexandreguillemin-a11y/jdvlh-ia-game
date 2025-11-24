"""
Service traduction PF2e EN→FR

Sources :
- Archives of Nethys FR (https://2e.aonprd.com/?Lang=fr)
- Pathfinder-FR.org
- Black Book Éditions
"""

import httpx
import json
import asyncio
from typing import Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import re


class PF2eTranslator:
    """
    Traducteur PF2e EN→FR

    Stratégie :
    1. Mapping manuel prioritaire (50-100 éléments MVP)
    2. Scraping Archives of Nethys FR (automatique)
    3. Fallback EN si traduction absente
    """

    # Base URLs
    ARCHIVES_FR = "https://2e.aonprd.com"

    # Rate limiting (respecter robots.txt)
    RATE_LIMIT_DELAY = 2.0  # 2 secondes entre requêtes

    def __init__(self):
        self.translations: Dict[str, Dict] = {
            "spells": {},
            "items": {},
            "monsters": {},
            "conditions": {},
            "feats": {},
        }

        # Charger mappings manuels
        self._load_manual_translations()

    def _load_manual_translations(self):
        """
        Mappings manuels prioritaires (MVP)

        À compléter avec 50-100 éléments essentiels
        """

        # Sorts prioritaires MVP (50+ sorts essentiels niveaux 0-3)
        self.translations["spells"] = {
            # === CANTRIPS (Niveau 0) ===
            "acid-splash": {
                "name": "Aspersion acide",
                "description": "Vous projetez de l'acide sur un ennemi.",
            },
            "detect-magic": {
                "name": "Détection de la magie",
                "description": "Vous détectez la présence de magie autour de vous.",
            },
            "light": {
                "name": "Lumière",
                "description": "Vous créez une source de lumière.",
            },
            "ray-of-frost": {
                "name": "Rayon de givre",
                "description": "Un rayon de froid gèle votre ennemi.",
            },
            "shield": {
                "name": "Bouclier",
                "description": "Vous créez un champ de force protecteur.",
            },
            "telekinetic-projectile": {
                "name": "Projectile télékinétique",
                "description": "Vous lancez un objet par télékinésie.",
            },
            "electric-arc": {
                "name": "Arc électrique",
                "description": "Un éclair frappe jusqu'à deux ennemis.",
            },
            "produce-flame": {
                "name": "Flamme",
                "description": "Vous créez une flamme dans votre main.",
            },
            "tanglefoot": {
                "name": "Enlacer",
                "description": "Vous créez une substance collante qui entrave.",
            },
            "daze": {
                "name": "Hébétement",
                "description": "Vous hébétez un ennemi avec de l'énergie mentale.",
            },
            "read-aura": {
                "name": "Lecture d'aura",
                "description": "Vous percevez l'aura magique d'un objet.",
            },
            "ghost-sound": {
                "name": "Son imaginaire",
                "description": "Vous créez des illusions sonores.",
            },
            "mage-hand": {
                "name": "Main du mage",
                "description": "Vous créez une main spectrale.",
            },
            "prestidigitation": {
                "name": "Prestidigitation",
                "description": "Vous créez de petits effets magiques.",
            },
            # === NIVEAU 1 ===
            "magic-missile": {
                "name": "Projectile magique",
                "description": "Vous lancez des projectiles qui ne ratent jamais.",
            },
            "heal": {
                "name": "Guérison",
                "description": "Vous canalisez de l'énergie positive pour soigner.",
            },
            "burning-hands": {
                "name": "Mains brûlantes",
                "description": "Des flammes jaillissent de vos mains en cône.",
            },
            "grease": {
                "name": "Graisse",
                "description": "Vous couvrez le sol d'une graisse glissante.",
            },
            "mage-armor": {
                "name": "Armure du mage",
                "description": "Une armure invisible vous protège.",
            },
            "true-strike": {
                "name": "Coup au but",
                "description": "Votre prochaine attaque a plus de chances de toucher.",
            },
            "fear": {
                "name": "Frayeur",
                "description": "Vous effrayez un ennemi.",
            },
            "sleep": {
                "name": "Sommeil",
                "description": "Vous endormez des créatures.",
            },
            "charm": {
                "name": "Charme",
                "description": "Vous rendez une créature amicale.",
            },
            "color-spray": {
                "name": "Couleurs dansantes",
                "description": "Des couleurs vives aveuglent vos ennemis.",
            },
            "command": {
                "name": "Injonction",
                "description": "Vous donnez un ordre d'un mot à une créature.",
            },
            "bane": {
                "name": "Malédiction",
                "description": "Vous maudissez vos ennemis.",
            },
            "bless": {
                "name": "Bénédiction",
                "description": "Vous bénissez vos alliés.",
            },
            "summon-animal": {
                "name": "Convocation d'animal",
                "description": "Vous invoquez un animal pour vous aider.",
            },
            "shocking-grasp": {
                "name": "Décharge électrique",
                "description": "Vous électrocutez un ennemi au toucher.",
            },
            "grim-tendrils": {
                "name": "Vrilles sinistres",
                "description": "Des tentacules d'énergie négative attaquent.",
            },
            # === NIVEAU 2 ===
            "invisibility": {
                "name": "Invisibilité",
                "description": "Vous devenez invisible.",
            },
            "mirror-image": {
                "name": "Image miroir",
                "description": "Vous créez des copies illusoires de vous-même.",
            },
            "blur": {
                "name": "Flou",
                "description": "Votre silhouette devient floue.",
            },
            "false-life": {
                "name": "Fausse vie",
                "description": "Vous gagnez des points de vie temporaires.",
            },
            "see-invisibility": {
                "name": "Détection de l'invisibilité",
                "description": "Vous voyez les créatures invisibles.",
            },
            "silence": {
                "name": "Silence",
                "description": "Vous créez une zone de silence total.",
            },
            "spiritual-weapon": {
                "name": "Arme spirituelle",
                "description": "Une arme magique flottante attaque vos ennemis.",
            },
            "flaming-sphere": {
                "name": "Sphère de feu",
                "description": "Une boule de feu roule et brûle vos ennemis.",
            },
            "darkness": {
                "name": "Ténèbres",
                "description": "Vous créez une zone de ténèbres magiques.",
            },
            "glitterdust": {
                "name": "Poussière scintillante",
                "description": "Une poudre scintillante révèle les créatures.",
            },
            "restoration": {
                "name": "Restauration",
                "description": "Vous soignez les afflictions et conditions.",
            },
            # === NIVEAU 3 ===
            "fireball": {
                "name": "Boule de feu",
                "description": "Vous créez une explosion de flammes dévastatrice.",
            },
            "haste": {
                "name": "Rapidité",
                "description": "Vous accélérez vos alliés.",
            },
            "slow": {
                "name": "Lenteur",
                "description": "Vous ralentissez vos ennemis.",
            },
            "lightning-bolt": {
                "name": "Éclair",
                "description": "Un éclair dévastateur frappe en ligne.",
            },
            "dispel-magic": {
                "name": "Dissipation de la magie",
                "description": "Vous dissipez les effets magiques.",
            },
            "fly": {
                "name": "Vol",
                "description": "Vous vous envolez dans les airs.",
            },
            "heroism": {
                "name": "Héroïsme",
                "description": "Vous insufflez du courage à un allié.",
            },
            "invisibility-sphere": {
                "name": "Sphère d'invisibilité",
                "description": "Vous et vos alliés devenez invisibles.",
            },
            "stinking-cloud": {
                "name": "Nuage nauséabond",
                "description": "Un nuage toxique rend vos ennemis malades.",
            },
            "wall-of-wind": {
                "name": "Mur de vent",
                "description": "Vous créez un mur de vents violents.",
            },
        }

        # Items prioritaires (à étendre)
        self.translations["items"] = {
            "longsword": {
                "name": "Épée longue",
                "description": "Une épée à une main polyvalente.",
            },
            "shortbow": {
                "name": "Arc court",
                "description": "Un arc compact pour le combat à distance.",
            },
            "leather-armor": {
                "name": "Armure de cuir",
                "description": "Armure légère en cuir tanné.",
            },
            "chain-mail": {
                "name": "Cotte de mailles",
                "description": "Armure moyenne en mailles métalliques.",
            },
            "healing-potion": {
                "name": "Potion de soins",
                "description": "Restaure des points de vie.",
            },
        }

        # Monstres prioritaires (à étendre)
        self.translations["monsters"] = {
            "goblin-warrior": {
                "name": "Guerrier gobelin",
                "description": "Un petit humanoïde malveillant.",
            },
            "orc-brute": {
                "name": "Brute orque",
                "description": "Un guerrier orque féroce et violent.",
            },
            "wolf": {"name": "Loup", "description": "Un prédateur canin sauvage."},
        }

        # Conditions (complet pour MVP)
        self.translations["conditions"] = {
            "blinded": "Aveuglé",
            "clumsy": "Maladroit",
            "confused": "Confus",
            "dazzled": "Ébloui",
            "deafened": "Assourdi",
            "doomed": "Condamné",
            "drained": "Drainé",
            "dying": "Mourant",
            "enfeebled": "Affaibli",
            "fatigued": "Fatigué",
            "fleeing": "En fuite",
            "frightened": "Effrayé",
            "grabbed": "Agrippé",
            "immobilized": "Immobilisé",
            "invisible": "Invisible",
            "paralyzed": "Paralysé",
            "persistent-damage": "Dégâts persistants",
            "petrified": "Pétrifié",
            "prone": "À terre",
            "quickened": "Accéléré",
            "restrained": "Entravé",
            "sickened": "Malade",
            "slowed": "Ralenti",
            "stunned": "Étourdi",
            "stupefied": "Hébété",
            "unconscious": "Inconscient",
            "wounded": "Blessé",
        }

    async def scrape_spell_translations(self, max_spells: int = 100) -> Dict[str, Dict]:
        """
        Scrape traductions sorts depuis Archives of Nethys FR

        Args:
            max_spells: Nombre maximum de sorts à scraper

        Returns:
            Dict avec traductions {spell_id: {name: str, description: str}}
        """

        print(f"[*] Scraping traductions sorts (max {max_spells})...")

        scraped = {}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Page liste sorts FR
                url = f"{self.ARCHIVES_FR}/Spells.aspx?Lang=fr"

                print(f"[+] Fetching {url}")
                response = await client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # Parser liens sorts (structure à adapter selon HTML réel)
                spell_links = soup.find_all(
                    "a", href=re.compile(r"Spells\.aspx\?ID=\d+")
                )

                print(f"[+] Trouvé {len(spell_links)} sorts")

                # Limiter au max_spells
                spell_links = spell_links[:max_spells]

                for i, link in enumerate(spell_links):
                    spell_name_fr = link.text.strip()
                    spell_url = f"{self.ARCHIVES_FR}/{link['href']}&Lang=fr"

                    # Rate limiting
                    if i > 0:
                        await asyncio.sleep(self.RATE_LIMIT_DELAY)

                    print(f"  [{i + 1}/{len(spell_links)}] {spell_name_fr}...")

                    # Fetch page sort
                    try:
                        spell_response = await client.get(spell_url)
                        spell_response.raise_for_status()

                        spell_soup = BeautifulSoup(spell_response.text, "html.parser")

                        # Parser description (structure à adapter)
                        desc_elem = spell_soup.find("span", class_="description")
                        description_fr = desc_elem.text.strip() if desc_elem else ""

                        # Générer ID (normaliser nom EN)
                        # NOTE : Nécessite matching EN→FR (complexe)
                        # Pour MVP, utiliser nom FR comme clé temporaire
                        spell_id = self._normalize_id(spell_name_fr)

                        scraped[spell_id] = {
                            "name": spell_name_fr,
                            "description": description_fr,
                        }

                    except Exception as e:
                        print(f"    [!] Erreur scraping {spell_name_fr}: {e}")
                        continue

            except Exception as e:
                print(f"[!] Erreur scraping liste sorts: {e}")
                return {}

        print(f"[+] Scraped {len(scraped)} sorts avec succès")

        return scraped

    def _normalize_id(self, name: str) -> str:
        """Normaliser nom pour ID (lowercase, tirets)"""
        normalized = name.lower()
        normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
        normalized = normalized.strip("-")
        return normalized

    async def scrape_item_translations(self, max_items: int = 100) -> Dict[str, Dict]:
        """
        Scrape traductions items depuis Archives of Nethys FR

        Similar à scrape_spell_translations
        """
        # TODO : Implémenter (structure similaire à spells)
        print("[!] Item scraping non implémenté encore")
        return {}

    def get_translation(
        self, content_type: str, content_id: str, field: str = "name"
    ) -> Optional[str]:
        """
        Récupérer traduction d'un élément

        Args:
            content_type: "spells", "items", "monsters", etc.
            content_id: ID de l'élément (ex: "fireball")
            field: "name" ou "description"

        Returns:
            Traduction FR ou None si absente
        """

        content_translations = self.translations.get(content_type, {})
        item_translation = content_translations.get(content_id, {})

        # Support both old format (field="name") and new format (field_fr="name_fr")
        # New JSON files from pf2-data-fr use "name_fr" and "description_fr"
        fr_field = f"{field}_fr"

        # Try new format first (name_fr, description_fr)
        result = item_translation.get(fr_field)
        if result:
            return result

        # Fallback to old format (name, description)
        return item_translation.get(field)

    def save_translations(self, output_dir: Path):
        """
        Sauvegarder traductions en JSON

        Args:
            output_dir: Dossier de sortie (ex: data/pf2e/translated/fr/)
        """

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for content_type, translations in self.translations.items():
            if not translations:
                continue

            output_file = output_dir / f"{content_type}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)

            print(
                f"[+] Sauvegardé {len(translations)} traductions {content_type} -> {output_file}"
            )

    def load_translations(self, input_dir: Path):
        """
        Charger traductions depuis JSON

        Args:
            input_dir: Dossier source (ex: data/pf2e/translated/fr/)
        """

        input_dir = Path(input_dir)

        if not input_dir.exists():
            print(f"[!] Dossier traductions introuvable: {input_dir}")
            return

        for content_type in ["spells", "items", "monsters", "conditions", "feats"]:
            json_file = input_dir / f"{content_type}.json"

            if json_file.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    self.translations[content_type] = json.load(f)

                print(
                    f"[+] Chargé {len(self.translations[content_type])} traductions {content_type}"
                )


# Script utilitaire pour générer traductions
async def generate_translations():
    """Script autonome pour générer traductions"""

    translator = PF2eTranslator()

    # Scraping sorts (limité à 50 pour test)
    print("\n[*] Démarrage scraping traductions...\n")

    scraped_spells = await translator.scrape_spell_translations(max_spells=50)

    # Merger avec manuels
    translator.translations["spells"].update(scraped_spells)

    # Sauvegarder
    output_dir = Path("data/pf2e/translated/fr")
    translator.save_translations(output_dir)

    print("\n[+] Traductions générées avec succès!")


if __name__ == "__main__":
    # Exécution autonome
    asyncio.run(generate_translations())
