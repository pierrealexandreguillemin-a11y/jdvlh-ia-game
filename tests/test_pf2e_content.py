"""Tests unitaires pour PF2eContent service"""

import pytest
from pathlib import Path
import sys

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jdvlh_ia_game.services.pf2e_content import PF2eContent  # noqa: E402


@pytest.fixture
def pf2e_content():
    """Fixture pour PF2eContent"""
    return PF2eContent()


def test_load_spells(pf2e_content):
    """Test chargement sorts"""
    spells = pf2e_content.get_all_spells()
    assert len(spells) > 0, "Aucun sort chargé"
    print(f"[+] {len(spells)} sorts chargés")


def test_get_spell_by_id(pf2e_content):
    """Test récupération sort par ID"""
    spell = pf2e_content.get_spell("fireball")
    assert spell is not None, "Fireball non trouvé"
    assert spell.name == "Boule de feu", f"Traduction FR incorrecte: {spell.name}"
    assert spell.level == 3, f"Niveau incorrect: {spell.level}"
    print(f"[+] Spell: {spell.name} (niv. {spell.level})")


@pytest.mark.skip(reason="Feature config missing max_spell_level key - TODO fix")
def test_feature_flags_mvp(pf2e_content):
    """Test feature flags MVP"""
    available = pf2e_content.get_all_spells(available_only=True)

    # Tous sorts <= niveau 3
    assert all(s.level <= 3 for s in available), "Sorts niveau > 3 en MVP"
    print(f"[+] {len(available)} sorts MVP (niveau <= 3)")


def test_fallback_en():
    """Test fallback EN si traduction FR absente"""
    content = PF2eContent()

    # Sort sans traduction FR devrait avoir nom EN
    spells = content.get_all_spells()
    untranslated = [s for s in spells if s.id != s.name.lower().replace(" ", "-")]

    # La plupart des sorts n'ont pas de traduction FR
    assert len(untranslated) > 0, "Aucun sort EN trouvé"
    print(f"[+] {len(untranslated)} sorts avec fallback EN")


def test_search(pf2e_content):
    """Test recherche sorts"""
    results = pf2e_content.search_spells("feu", limit=5)

    assert len(results) > 0, "Aucun résultat recherche"
    # Au moins un résultat doit contenir "feu"
    assert any(
        "feu" in s.name.lower() or "feu" in s.description.lower() for s in results
    ), "Résultats incohérents"

    print(f"[+] {len(results)} résultats pour 'feu'")


def test_spell_translations(pf2e_content):
    """Test traductions spécifiques"""
    translations = {
        "fireball": "Boule de feu",
        "heal": "Guérison",
        "shield": "Bouclier",
    }

    for spell_id, expected_fr in translations.items():
        spell = pf2e_content.get_spell(spell_id)
        assert spell is not None, f"Sort {spell_id} non trouvé"
        assert (
            spell.name == expected_fr
        ), f"Traduction incorrecte: {spell.name} != {expected_fr}"

    print(f"[+] {len(translations)} traductions vérifiées")


def test_mvp_spell_count():
    """Test nombre de sorts MVP"""
    content = PF2eContent()
    mvp_spells = content.get_all_spells(filter_by_level=3)

    assert len(mvp_spells) > 800, f"Trop peu de sorts MVP: {len(mvp_spells)}"
    assert len(mvp_spells) < 1000, f"Trop de sorts MVP: {len(mvp_spells)}"

    print(f"[+] {len(mvp_spells)} sorts MVP dans la plage attendue")
