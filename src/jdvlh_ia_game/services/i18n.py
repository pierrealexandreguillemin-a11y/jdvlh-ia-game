"""
Service d'internationalisation (i18n) pour jdvlh-ia-game

Gère toutes les traductions de l'interface utilisateur,
messages système, erreurs, et contenu statique.
"""

from typing import Dict, Optional
from enum import Enum


class Language(Enum):
    """Langues supportées"""

    FR = "fr"
    EN = "en"


class I18nService:
    """
    Service centralisé de traduction pour l'interface

    Usage:
        i18n = I18nService(language="fr")
        message = i18n.get("combat.no_active")
        # "Aucun combat actif"
    """

    def __init__(self, language: str = "fr"):
        self.language = Language(language)
        self._translations: Dict[str, Dict[str, str]] = {
            # ===== MESSAGES SYSTÈME =====
            "system": {
                "fr": "Système",
                "en": "System",
            },
            "error": {
                "fr": "Erreur",
                "en": "Error",
            },
            "success": {
                "fr": "Succès",
                "en": "Success",
            },
            # ===== BIENVENUE & INTRO =====
            "welcome.title": {
                "fr": "Bienvenue en Terre du Milieu !",
                "en": "Welcome to Middle-earth!",
            },
            "welcome.message": {
                "fr": "Que fais-tu dans la Comté ?",
                "en": "What are you doing in the Shire?",
            },
            "welcome.choice.explore": {
                "fr": "Explorer la forêt",
                "en": "Explore the forest",
            },
            "welcome.choice.meet": {
                "fr": "Rencontrer un hobbit",
                "en": "Meet a hobbit",
            },
            "welcome.choice.treasure": {
                "fr": "Chercher un trésor",
                "en": "Search for treasure",
            },
            # ===== COMBAT =====
            "combat.no_active": {
                "fr": "Aucun combat actif",
                "en": "No active combat",
            },
            "combat.start": {
                "fr": "Le combat commence !",
                "en": "Combat begins!",
            },
            "combat.victory": {
                "fr": "Victoire ! Vous avez vaincu vos ennemis.",
                "en": "Victory! You defeated your enemies.",
            },
            "combat.defeat": {
                "fr": "Défaite... Vous avez été vaincu.",
                "en": "Defeat... You have been vanquished.",
            },
            "combat.your_turn": {
                "fr": "À votre tour !",
                "en": "Your turn!",
            },
            "combat.enemy_turn": {
                "fr": "Tour de l'ennemi",
                "en": "Enemy turn",
            },
            # ===== INVENTAIRE =====
            "inventory.empty": {
                "fr": "Votre inventaire est vide",
                "en": "Your inventory is empty",
            },
            "inventory.full": {
                "fr": "Inventaire plein",
                "en": "Inventory full",
            },
            "inventory.item_equipped": {
                "fr": "Objet équipé",
                "en": "Item equipped",
            },
            "inventory.item_unequipped": {
                "fr": "Objet déséquipé",
                "en": "Item unequipped",
            },
            "inventory.item_used": {
                "fr": "Objet utilisé",
                "en": "Item used",
            },
            "inventory.item_dropped": {
                "fr": "Objet abandonné",
                "en": "Item dropped",
            },
            "inventory.not_enough_gold": {
                "fr": "Pas assez d'or",
                "en": "Not enough gold",
            },
            # ===== QUÊTES =====
            "quest.accepted": {
                "fr": "Quête acceptée",
                "en": "Quest accepted",
            },
            "quest.completed": {
                "fr": "Quête terminée !",
                "en": "Quest completed!",
            },
            "quest.failed": {
                "fr": "Quête échouée",
                "en": "Quest failed",
            },
            "quest.abandoned": {
                "fr": "Quête abandonnée",
                "en": "Quest abandoned",
            },
            "quest.no_active": {
                "fr": "Aucune quête active",
                "en": "No active quests",
            },
            "quest.objective_complete": {
                "fr": "Objectif accompli",
                "en": "Objective complete",
            },
            # ===== PERSONNAGE =====
            "character.level_up": {
                "fr": "Niveau supérieur ! Vous êtes maintenant niveau {level}",
                "en": "Level up! You are now level {level}",
            },
            "character.stat_increased": {
                "fr": "Statistique augmentée : {stat}",
                "en": "Stat increased: {stat}",
            },
            "character.skill_learned": {
                "fr": "Compétence apprise : {skill}",
                "en": "Skill learned: {skill}",
            },
            "character.not_enough_points": {
                "fr": "Pas assez de points de compétence",
                "en": "Not enough skill points",
            },
            "character.invalid_stat": {
                "fr": "Statistique invalide : {stat}",
                "en": "Invalid stat: {stat}",
            },
            "character.skills_reset": {
                "fr": "Compétences réinitialisées",
                "en": "Skills reset",
            },
            "character.reset_cost": {
                "fr": "Coût de réinitialisation : {cost} pièces d'or",
                "en": "Reset cost: {cost} gold",
            },
            # ===== GAME STATE =====
            "game.reset": {
                "fr": "Partie réinitialisée",
                "en": "Game reset",
            },
            "game.saved": {
                "fr": "Partie sauvegardée",
                "en": "Game saved",
            },
            "game.loaded": {
                "fr": "Partie chargée",
                "en": "Game loaded",
            },
            "game.server_full": {
                "fr": "Serveur plein. Réessayez plus tard.",
                "en": "Server full. Try again later.",
            },
            # ===== ERREURS COMMUNES =====
            "error.invalid_action": {
                "fr": "Action invalide",
                "en": "Invalid action",
            },
            "error.not_found": {
                "fr": "Élément introuvable",
                "en": "Item not found",
            },
            "error.already_equipped": {
                "fr": "Déjà équipé",
                "en": "Already equipped",
            },
            "error.requirements_not_met": {
                "fr": "Conditions non remplies",
                "en": "Requirements not met",
            },
            "error.connection_lost": {
                "fr": "Connexion perdue",
                "en": "Connection lost",
            },
            # ===== STATS =====
            "stat.strength": {
                "fr": "Force",
                "en": "Strength",
            },
            "stat.intelligence": {
                "fr": "Intelligence",
                "en": "Intelligence",
            },
            "stat.agility": {
                "fr": "Agilité",
                "en": "Agility",
            },
            "stat.constitution": {
                "fr": "Constitution",
                "en": "Constitution",
            },
            "stat.wisdom": {
                "fr": "Sagesse",
                "en": "Wisdom",
            },
            "stat.charisma": {
                "fr": "Charisme",
                "en": "Charisma",
            },
            # ===== RACES =====
            "race.human": {
                "fr": "Humain",
                "en": "Human",
            },
            "race.elf": {
                "fr": "Elfe",
                "en": "Elf",
            },
            "race.dwarf": {
                "fr": "Nain",
                "en": "Dwarf",
            },
            "race.hobbit": {
                "fr": "Hobbit",
                "en": "Hobbit",
            },
            # ===== CLASSES =====
            "class.warrior": {
                "fr": "Guerrier",
                "en": "Warrior",
            },
            "class.mage": {
                "fr": "Mage",
                "en": "Mage",
            },
            "class.ranger": {
                "fr": "Rôdeur",
                "en": "Ranger",
            },
            "class.cleric": {
                "fr": "Clerc",
                "en": "Cleric",
            },
            # ===== LIEUX =====
            "location.shire": {
                "fr": "la Comté",
                "en": "the Shire",
            },
            "location.rivendell": {
                "fr": "Fondcombe",
                "en": "Rivendell",
            },
            "location.moria": {
                "fr": "les Mines de la Moria",
                "en": "the Mines of Moria",
            },
            "location.gondor": {
                "fr": "le Gondor",
                "en": "Gondor",
            },
            "location.mordor": {
                "fr": "le Mordor",
                "en": "Mordor",
            },
            # ===== TUTORIELS =====
            "tutorial.welcome": {
                "fr": "Bienvenue, aventurier ! Laissez-moi vous guider dans votre périple.",
                "en": "Welcome, adventurer! Let me guide you on your journey.",
            },
            "tutorial.movement": {
                "fr": "Utilisez les choix pour naviguer dans le monde.",
                "en": "Use the choices to navigate the world.",
            },
            "tutorial.combat": {
                "fr": "En combat, choisissez attaquer, lancer un sort, ou vous défendre.",
                "en": "In combat, choose to attack, cast a spell, or defend.",
            },
            "tutorial.inventory": {
                "fr": "Gérez votre équipement dans l'inventaire.",
                "en": "Manage your equipment in the inventory.",
            },
            "tutorial.quests": {
                "fr": "Acceptez des quêtes pour gagner de l'expérience et des récompenses.",
                "en": "Accept quests to earn experience and rewards.",
            },
            # ===== PF2E INTÉGRATION =====
            "pf2e.spell_cast": {
                "fr": "Vous lancez {spell_name}",
                "en": "You cast {spell_name}",
            },
            "pf2e.monster_appears": {
                "fr": "Un {monster_name} apparaît !",
                "en": "A {monster_name} appears!",
            },
            "pf2e.item_found": {
                "fr": "Vous trouvez : {item_name}",
                "en": "You found: {item_name}",
            },
        }

    def get(self, key: str, **kwargs) -> str:
        """
        Récupérer une traduction par clé

        Args:
            key: Clé de traduction (ex: "combat.no_active")
            **kwargs: Variables pour formatage (ex: level=5)

        Returns:
            Texte traduit dans la langue actuelle

        Example:
            >>> i18n = I18nService("fr")
            >>> i18n.get("character.level_up", level=5)
            "Niveau supérieur ! Vous êtes maintenant niveau 5"
        """
        translations = self._translations.get(key, {})
        text = translations.get(self.language.value)

        if text is None:
            # Fallback EN si traduction FR absente
            text = translations.get("en", f"[MISSING: {key}]")

        # Formatage des variables
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"[i18n] Missing variable in '{key}': {e}")

        return text

    def set_language(self, language: str):
        """Changer la langue de l'interface"""
        self.language = Language(language)

    def get_all_translations(self, prefix: Optional[str] = None) -> Dict[str, str]:
        """
        Récupérer toutes les traductions avec un préfixe donné

        Args:
            prefix: Préfixe optionnel (ex: "combat" pour toutes les clés combat.*)

        Returns:
            Dict {key: translated_text}

        Example:
            >>> i18n.get_all_translations("combat")
            {'combat.no_active': 'Aucun combat actif', ...}
        """
        result = {}

        for key, translations in self._translations.items():
            if prefix is None or key.startswith(f"{prefix}."):
                result[key] = translations.get(
                    self.language.value, translations.get("en")
                )

        return result


# Singleton global
_i18n_instance: Optional[I18nService] = None


def get_i18n(language: str = "fr") -> I18nService:
    """Récupérer instance singleton I18nService"""
    global _i18n_instance

    if _i18n_instance is None or _i18n_instance.language.value != language:
        _i18n_instance = I18nService(language=language)

    return _i18n_instance
