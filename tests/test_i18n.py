"""Tests unitaires pour le service i18n"""

from pathlib import Path
import sys

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jdvlh_ia_game.services.i18n import I18nService, get_i18n, Language  # noqa: E402


def test_i18n_initialization():
    """Test initialisation du service i18n"""
    i18n = I18nService(language="fr")
    assert i18n.language == Language.FR


def test_get_translation_french():
    """Test récupération traduction française"""
    i18n = I18nService(language="fr")

    assert i18n.get("combat.no_active") == "Aucun combat actif"
    assert i18n.get("game.reset") == "Partie réinitialisée"
    assert i18n.get("welcome.title") == "Bienvenue en Terre du Milieu !"


def test_get_translation_english():
    """Test récupération traduction anglaise"""
    i18n = I18nService(language="en")

    assert i18n.get("combat.no_active") == "No active combat"
    assert i18n.get("game.reset") == "Game reset"
    assert i18n.get("welcome.title") == "Welcome to Middle-earth!"


def test_get_translation_with_variables():
    """Test traduction avec variables de formatage"""
    i18n = I18nService(language="fr")

    result = i18n.get("character.level_up", level=5)
    assert result == "Niveau supérieur ! Vous êtes maintenant niveau 5"

    result = i18n.get("character.reset_cost", cost=100)
    assert result == "Coût de réinitialisation : 100 pièces d'or"


def test_fallback_to_english():
    """Test fallback vers anglais si traduction FR absente"""
    i18n = I18nService(language="fr")

    # Si une clé n'existe qu'en anglais, devrait fallback
    # (actuellement toutes les clés existent en FR, donc test avec clé invalide)
    result = i18n.get("nonexistent.key")
    assert result == "[MISSING: nonexistent.key]"


def test_set_language():
    """Test changement de langue"""
    i18n = I18nService(language="fr")
    assert i18n.get("combat.victory") == "Victoire ! Vous avez vaincu vos ennemis."

    i18n.set_language("en")
    assert i18n.get("combat.victory") == "Victory! You defeated your enemies."


def test_get_all_translations():
    """Test récupération de toutes les traductions"""
    i18n = I18nService(language="fr")

    # Récupérer toutes les traductions combat
    combat_translations = i18n.get_all_translations("combat")
    assert "combat.no_active" in combat_translations
    assert "combat.victory" in combat_translations
    assert "combat.defeat" in combat_translations

    # Vérifier les valeurs
    assert combat_translations["combat.no_active"] == "Aucun combat actif"


def test_get_all_translations_no_prefix():
    """Test récupération toutes traductions sans préfixe"""
    i18n = I18nService(language="fr")

    all_translations = i18n.get_all_translations()
    assert len(all_translations) > 50  # Devrait avoir plus de 50 clés
    assert "welcome.title" in all_translations
    assert "combat.no_active" in all_translations


def test_singleton():
    """Test que get_i18n retourne un singleton"""
    i18n1 = get_i18n("fr")
    i18n2 = get_i18n("fr")
    assert i18n1 is i18n2


def test_singleton_language_change():
    """Test que changer la langue crée une nouvelle instance"""
    i18n_fr = get_i18n("fr")
    i18n_en = get_i18n("en")

    # Devraient être des instances différentes
    # (car language a changé)
    assert i18n_fr.language != i18n_en.language


def test_stats_translations():
    """Test traductions des statistiques"""
    i18n = I18nService(language="fr")

    assert i18n.get("stat.strength") == "Force"
    assert i18n.get("stat.intelligence") == "Intelligence"
    assert i18n.get("stat.agility") == "Agilité"
    assert i18n.get("stat.wisdom") == "Sagesse"


def test_races_translations():
    """Test traductions des races"""
    i18n = I18nService(language="fr")

    assert i18n.get("race.human") == "Humain"
    assert i18n.get("race.elf") == "Elfe"
    assert i18n.get("race.dwarf") == "Nain"
    assert i18n.get("race.hobbit") == "Hobbit"


def test_classes_translations():
    """Test traductions des classes"""
    i18n = I18nService(language="fr")

    assert i18n.get("class.warrior") == "Guerrier"
    assert i18n.get("class.mage") == "Mage"
    assert i18n.get("class.ranger") == "Rôdeur"
    assert i18n.get("class.cleric") == "Clerc"


def test_locations_translations():
    """Test traductions des lieux"""
    i18n = I18nService(language="fr")

    assert i18n.get("location.shire") == "la Comté"
    assert i18n.get("location.rivendell") == "Fondcombe"
    assert i18n.get("location.moria") == "les Mines de la Moria"


def test_pf2e_integration_keys():
    """Test clés d'intégration PF2e"""
    i18n = I18nService(language="fr")

    # Tester les clés PF2e
    result = i18n.get("pf2e.spell_cast", spell_name="Boule de feu")
    assert result == "Vous lancez Boule de feu"

    result = i18n.get("pf2e.monster_appears", monster_name="Dragon")
    assert result == "Un Dragon apparaît !"

    result = i18n.get("pf2e.item_found", item_name="Épée longue")
    assert result == "Vous trouvez : Épée longue"


def test_tutorial_messages():
    """Test messages de tutoriel"""
    i18n = I18nService(language="fr")

    assert "Bienvenue, aventurier" in i18n.get("tutorial.welcome")
    assert "combat" in i18n.get("tutorial.combat").lower()
    assert "inventaire" in i18n.get("tutorial.inventory").lower()


def test_error_messages():
    """Test messages d'erreur"""
    i18n = I18nService(language="fr")

    assert i18n.get("error.invalid_action") == "Action invalide"
    assert i18n.get("error.not_found") == "Élément introuvable"
    assert i18n.get("error.connection_lost") == "Connexion perdue"
