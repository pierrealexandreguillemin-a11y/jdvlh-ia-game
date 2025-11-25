#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'extraction des traductions officielles PF2e FR

Source: https://github.com/pathfinder-fr/pf2-data-fr
Extrait les mappings EN→FR depuis les fichiers JSON officiels
et génère les fichiers de traduction pour le projet.

Auteur: jdvlh-ia-game
Date: 24 Novembre 2025
"""

import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
from pathlib import Path
from typing import Dict, List

# Chemins
PF2_DATA_FR_DIR = Path("C:/Dev/pf2-data-fr")
OUTPUT_DIR = Path("C:/Dev/jdvlh-ia-game/data/pf2e/translated/fr")


def normalize_id(name: str) -> str:
    """Normaliser nom en ID (lowercase, tirets)"""
    import re

    normalized = name.lower()
    normalized = re.sub(r"[^a-z0-9àâäéèêëïîôùûüç]+", "-", normalized)
    normalized = normalized.strip("-")
    return normalized


def extract_spells(source_file: Path) -> Dict[str, Dict]:
    """
    Extraire traductions sorts depuis spells-srd.json

    Returns:
        Dict {spell_id: {name_en, name_fr, description_fr, ...}}
    """
    print(f"\n📚 Extraction sorts depuis {source_file.name}...")

    with open(source_file, "r", encoding="utf-8") as f:
        spells_data = json.load(f)

    translations = {}
    count_translated = 0

    for spell in spells_data:
        name_en = spell.get("name", "")
        spell_id = normalize_id(name_en)

        # Extraire traduction FR
        translations_node = spell.get("translations", {})
        fr_data = translations_node.get("fr", {})

        if fr_data and "name" in fr_data:
            name_fr = fr_data["name"]
            description_fr = fr_data.get("description", "")

            # Nettoyer description HTML (basic)
            import re

            description_clean = re.sub(r"<[^>]+>", "", description_fr)[:500]

            translations[spell_id] = {
                "name_en": name_en,
                "name_fr": name_fr,
                "description_en": spell.get("description", "")[:500],
                "description_fr": description_clean,
                "traits_fr": spell.get("traits", []),
                "source": "pf2-data-fr",
                "verified": True,
                "level": spell.get("level", 0),
                "_id": spell.get("_id", ""),
            }
            count_translated += 1

    print(f"  ✅ {count_translated}/{len(spells_data)} sorts traduits")
    return translations


def extract_equipment(source_file: Path) -> Dict[str, Dict]:
    """Extraire traductions équipement depuis equipment-srd.json"""
    print(f"\n🗡️ Extraction équipement depuis {source_file.name}...")

    with open(source_file, "r", encoding="utf-8") as f:
        items_data = json.load(f)

    translations = {}
    count_translated = 0

    for item in items_data:
        name_en = item.get("name", "")
        item_id = normalize_id(name_en)

        translations_node = item.get("translations", {})
        fr_data = translations_node.get("fr", {})

        if fr_data and "name" in fr_data:
            name_fr = fr_data["name"]
            description_fr = fr_data.get("description", "")

            import re

            description_clean = re.sub(r"<[^>]+>", "", description_fr)[:500]

            translations[item_id] = {
                "name_en": name_en,
                "name_fr": name_fr,
                "description_en": item.get("description", "")[:500],
                "description_fr": description_clean,
                "traits_fr": item.get("traits", []),
                "source": "pf2-data-fr",
                "verified": True,
                "level": item.get("level", 0),
                "type": item.get("type", ""),
                "_id": item.get("_id", ""),
            }
            count_translated += 1

    print(f"  ✅ {count_translated}/{len(items_data)} items traduits")
    return translations


def extract_bestiary(source_files: List[Path]) -> Dict[str, Dict]:
    """Extraire traductions monstres depuis pathfinder-bestiary-*.json"""
    print(f"\n👹 Extraction monstres depuis {len(source_files)} bestiaires...")

    translations = {}
    total_creatures = 0
    count_translated = 0

    for source_file in source_files:
        print(f"  📖 Lecture {source_file.name}...")

        with open(source_file, "r", encoding="utf-8") as f:
            creatures_data = json.load(f)

        total_creatures += len(creatures_data)

        for creature in creatures_data:
            name_en = creature.get("name", "")
            creature_id = normalize_id(name_en)

            translations_node = creature.get("translations", {})
            fr_data = translations_node.get("fr", {})

            if fr_data and "name" in fr_data:
                name_fr = fr_data["name"]
                description_fr = fr_data.get("description", "")

                import re

                description_clean = re.sub(r"<[^>]+>", "", description_fr)[:500]

                translations[creature_id] = {
                    "name_en": name_en,
                    "name_fr": name_fr,
                    "description_en": creature.get("description", "")[:500],
                    "description_fr": description_clean,
                    "traits_fr": creature.get("traits", []),
                    "source": "pf2-data-fr",
                    "verified": True,
                    "level": creature.get("level", 0),
                    "_id": creature.get("_id", ""),
                }
                count_translated += 1

    print(f"  ✅ {count_translated}/{total_creatures} monstres traduits")
    return translations


def save_translations(translations: Dict, output_file: Path):
    """Sauvegarder traductions en JSON"""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)

    print(f"  💾 Sauvegardé {len(translations)} traductions → {output_file.name}")


def main():
    """Point d'entrée principal"""

    print(
        """
================================================================
  EXTRACTION TRADUCTIONS OFFICIELLES PF2e FR

  Source: https://github.com/pathfinder-fr/pf2-data-fr
  Licence: OGL (Open Gaming License)
================================================================
"""
    )

    # Vérifier présence du repository
    if not PF2_DATA_FR_DIR.exists():
        print(f"❌ Dossier pf2-data-fr introuvable: {PF2_DATA_FR_DIR}")
        print(
            "   Cloner d'abord: git clone https://github.com/pathfinder-fr/pf2-data-fr.git"
        )
        return

    # Extraire sorts
    spells_file = PF2_DATA_FR_DIR / "spells-srd.json"
    if spells_file.exists():
        spells_translations = extract_spells(spells_file)
        save_translations(spells_translations, OUTPUT_DIR / "spells.json")
    else:
        print(f"⚠️ Fichier introuvable: {spells_file}")

    # Extraire équipement
    equipment_file = PF2_DATA_FR_DIR / "equipment-srd.json"
    if equipment_file.exists():
        items_translations = extract_equipment(equipment_file)
        save_translations(items_translations, OUTPUT_DIR / "items.json")
    else:
        print(f"⚠️ Fichier introuvable: {equipment_file}")

    # Extraire monstres (bestiaires 1-3)
    bestiary_files = [
        PF2_DATA_FR_DIR / "pathfinder-bestiary.json",
        PF2_DATA_FR_DIR / "pathfinder-bestiary-2.json",
        PF2_DATA_FR_DIR / "pathfinder-bestiary-3.json",
    ]
    existing_bestiary = [f for f in bestiary_files if f.exists()]

    if existing_bestiary:
        monsters_translations = extract_bestiary(existing_bestiary)
        save_translations(monsters_translations, OUTPUT_DIR / "monsters.json")
    else:
        print("⚠️ Aucun fichier bestiary trouvé")

    # Copier les conditions (déjà existantes)
    existing_conditions = OUTPUT_DIR / "conditions.json"
    if existing_conditions.exists():
        print(f"\n✅ Conditions déjà traduites: {existing_conditions}")

    # Résumé final
    print("\n" + "=" * 60)
    print("✅ EXTRACTION TERMINÉE")
    print(f"   Output: {OUTPUT_DIR}")
    print("   Fichiers générés:")
    for json_file in OUTPUT_DIR.glob("*.json"):
        size_kb = json_file.stat().st_size / 1024
        print(f"     - {json_file.name} ({size_kb:.1f} KB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
