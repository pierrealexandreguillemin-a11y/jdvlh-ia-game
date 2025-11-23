"""
Character Progression - Manages player leveling, skills, and stats
Handles XP, level-ups, skill trees, and stat allocation
"""

from typing import Dict, List
from ..models.game_entities import Player, CharacterClass


# ============================================================================
# SKILL TREES
# ============================================================================

SKILL_TREES = {
    CharacterClass.GUERRIER: {
        "charge": {
            "name": "Charge",
            "description": "Foncez vers l'ennemi et infligez +50% dégâts",
            "level_required": 2,
            "cost": 1,
            "prerequisites": [],
        },
        "tourbillon": {
            "name": "Tourbillon d'acier",
            "description": "Attaque tous les ennemis autour de vous",
            "level_required": 5,
            "cost": 2,
            "prerequisites": ["charge"],
        },
        "rage": {
            "name": "Rage du guerrier",
            "description": "+100% dégâts pendant 3 tours",
            "level_required": 10,
            "cost": 3,
            "prerequisites": [],
        },
        "bouclier_iron": {
            "name": "Bouclier de fer",
            "description": "+50% armure pendant 2 tours",
            "level_required": 7,
            "cost": 2,
            "prerequisites": [],
        },
    },
    CharacterClass.MAGE: {
        "boule_de_feu": {
            "name": "Boule de feu",
            "description": "Lance une boule de feu (Intelligence x 2 dégâts)",
            "level_required": 2,
            "cost": 1,
            "prerequisites": [],
        },
        "eclair": {
            "name": "Éclair",
            "description": "Frappe l'ennemi avec la foudre (Intelligence x 3 dégâts)",
            "level_required": 5,
            "cost": 2,
            "prerequisites": [],
        },
        "meteore": {
            "name": "Pluie de météores",
            "description": "Attaque tous les ennemis (Intelligence x 2.5 dégâts)",
            "level_required": 10,
            "cost": 3,
            "prerequisites": ["boule_de_feu"],
        },
        "soin": {
            "name": "Soin",
            "description": "Restaure 50 HP",
            "level_required": 3,
            "cost": 1,
            "prerequisites": [],
        },
        "bouclier_magique": {
            "name": "Bouclier magique",
            "description": "Absorbe 100 dégâts",
            "level_required": 6,
            "cost": 2,
            "prerequisites": [],
        },
    },
    CharacterClass.RANGER: {
        "tir_precis": {
            "name": "Tir précis",
            "description": "Tir à l'arc garanti coup critique",
            "level_required": 2,
            "cost": 1,
            "prerequisites": [],
        },
        "pieges": {
            "name": "Pièges",
            "description": "Pose un piège qui inflige 50 dégâts",
            "level_required": 4,
            "cost": 1,
            "prerequisites": [],
        },
        "multi_fleches": {
            "name": "Pluie de flèches",
            "description": "Tire 5 flèches sur des cibles aléatoires",
            "level_required": 8,
            "cost": 3,
            "prerequisites": ["tir_precis"],
        },
        "camouflage": {
            "name": "Camouflage",
            "description": "Évite la prochaine attaque ennemie",
            "level_required": 5,
            "cost": 2,
            "prerequisites": [],
        },
    },
    CharacterClass.VOLEUR: {
        "coup_sournois": {
            "name": "Coup sournois",
            "description": "Attaque qui ignore 50% de l'armure",
            "level_required": 2,
            "cost": 1,
            "prerequisites": [],
        },
        "poison": {
            "name": "Poison",
            "description": "Empoisonne l'ennemi (20 dégâts par tour pendant 3 tours)",
            "level_required": 5,
            "cost": 2,
            "prerequisites": ["coup_sournois"],
        },
        "fuite": {
            "name": "Fuite rapide",
            "description": "Évite le combat immédiatement",
            "level_required": 3,
            "cost": 1,
            "prerequisites": [],
        },
        "vol_pickpocket": {
            "name": "Pickpocket",
            "description": "Chance de voler de l'or aux ennemis",
            "level_required": 6,
            "cost": 2,
            "prerequisites": [],
        },
    },
}


# ============================================================================
# CHARACTER PROGRESSION MANAGER
# ============================================================================


class CharacterProgression:
    """Manages player leveling and skill progression"""

    def __init__(self):
        pass

    def gain_xp(self, player: Player, amount: int) -> Dict[str, any]:
        """
        Give XP to player and check for level up

        Args:
            player: The player
            amount: XP amount to give

        Returns:
            Dict with level up info
        """

        old_level = player.level
        leveled_up = player.gain_xp(amount)

        result = {
            "xp_gained": amount,
            "current_xp": player.xp,
            "leveled_up": leveled_up,
        }

        if leveled_up:
            result.update(
                {
                    "new_level": player.level,
                    "skill_points_gained": player.level - old_level,  # 1 per level
                    "stat_increases": self._get_level_up_bonuses(player),
                }
            )

        return result

    def allocate_stat_point(self, player: Player, stat_name: str) -> Dict[str, any]:
        """
        Allocate a skill point to a stat

        Args:
            player: The player
            stat_name: Name of the stat to increase

        Returns:
            Dict with success status
        """

        if player.skill_points <= 0:
            return {
                "success": False,
                "message": "Pas de points de compétence disponibles",
            }

        # Validate stat name
        valid_stats = [
            "strength",
            "intelligence",
            "agility",
            "wisdom",
            "constitution",
            "charisma",
        ]

        if stat_name not in valid_stats:
            return {"success": False, "message": f"Stat invalide: {stat_name}"}

        # Increase stat
        current_value = getattr(player, stat_name)
        setattr(player, stat_name, current_value + 1)

        # Deduct skill point
        player.skill_points -= 1

        # Update derived stats if needed
        if stat_name == "constitution":
            player.max_hp += 5
            player.hp += 5

        if stat_name == "intelligence":
            player.max_mana += 3
            player.mana += 3

        return {
            "success": True,
            "message": f"{stat_name.capitalize()} augmenté à {current_value + 1}",
            "stat": stat_name,
            "new_value": current_value + 1,
            "skill_points_remaining": player.skill_points,
        }

    def learn_skill(self, player: Player, skill_id: str) -> Dict[str, any]:
        """
        Learn a new skill from skill tree

        Args:
            player: The player
            skill_id: ID of the skill to learn

        Returns:
            Dict with success status
        """

        # Get skill tree for player class
        skill_tree = SKILL_TREES.get(player.class_type)

        if not skill_tree:
            return {"success": False, "message": "Classe inconnue"}

        # Get skill data
        skill = skill_tree.get(skill_id)

        if not skill:
            return {"success": False, "message": "Compétence inconnue"}

        # Check if already learned
        if skill_id in player.learned_skills:
            return {
                "success": False,
                "message": "Vous connaissez déjà cette compétence",
            }

        # Check level requirement
        if player.level < skill["level_required"]:
            return {
                "success": False,
                "message": f"Niveau {skill['level_required']} requis",
            }

        # Check skill points
        if player.skill_points < skill["cost"]:
            return {
                "success": False,
                "message": f"Pas assez de points de compétence (besoin: {skill['cost']})",
            }

        # Check prerequisites
        for prereq in skill["prerequisites"]:
            if prereq not in player.learned_skills:
                prereq_name = skill_tree[prereq]["name"]
                return {
                    "success": False,
                    "message": f"Prérequis manquant: {prereq_name}",
                }

        # Learn skill
        player.learned_skills.append(skill_id)
        player.skill_points -= skill["cost"]

        return {
            "success": True,
            "message": f"Nouvelle compétence apprise: {skill['name']} !",
            "skill": {
                "id": skill_id,
                "name": skill["name"],
                "description": skill["description"],
            },
            "skill_points_remaining": player.skill_points,
        }

    def get_available_skills(self, player: Player) -> List[Dict]:
        """
        Get list of skills player can learn

        Args:
            player: The player

        Returns:
            List of available skills with their info
        """

        skill_tree = SKILL_TREES.get(player.class_type, {})
        available_skills = []

        for skill_id, skill_data in skill_tree.items():
            # Skip if already learned
            if skill_id in player.learned_skills:
                continue

            # Check level requirement
            if player.level < skill_data["level_required"]:
                continue

            # Check prerequisites
            prereqs_met = all(
                prereq in player.learned_skills
                for prereq in skill_data["prerequisites"]
            )

            if not prereqs_met:
                continue

            # Skill is available
            available_skills.append(
                {
                    "id": skill_id,
                    "name": skill_data["name"],
                    "description": skill_data["description"],
                    "cost": skill_data["cost"],
                    "can_afford": player.skill_points >= skill_data["cost"],
                }
            )

        return available_skills

    def get_stat_recommendations(self, player: Player) -> Dict[str, str]:
        """
        Get stat allocation recommendations based on class

        Args:
            player: The player

        Returns:
            Dict with recommended stats
        """

        recommendations = {
            CharacterClass.GUERRIER: {
                "primary": "strength",
                "secondary": "constitution",
                "description": "Force pour dégâts, Constitution pour survie",
            },
            CharacterClass.MAGE: {
                "primary": "intelligence",
                "secondary": "wisdom",
                "description": "Intelligence pour sorts puissants, Sagesse pour mana",
            },
            CharacterClass.RANGER: {
                "primary": "agility",
                "secondary": "wisdom",
                "description": "Agilité pour précision, Sagesse pour compétences spéciales",
            },
            CharacterClass.VOLEUR: {
                "primary": "agility",
                "secondary": "charisma",
                "description": "Agilité pour furtivité, Charisme pour interactions",
            },
        }

        return recommendations.get(player.class_type, {})

    def reset_skills(self, player: Player, cost: int = 100) -> Dict[str, any]:
        """
        Reset all learned skills and refund skill points (costs gold)

        Args:
            player: The player
            cost: Gold cost to reset

        Returns:
            Dict with success status
        """

        if not player.can_afford(cost):
            return {
                "success": False,
                "message": f"Pas assez d'or (besoin: {cost}, vous avez: {player.gold})",
            }

        # Calculate total skill points spent
        skill_tree = SKILL_TREES.get(player.class_type, {})
        total_points_spent = sum(
            skill_tree[skill_id]["cost"]
            for skill_id in player.learned_skills
            if skill_id in skill_tree
        )

        # Reset
        player.learned_skills.clear()
        player.skill_points += total_points_spent
        player.gold -= cost

        return {
            "success": True,
            "message": f"Compétences réinitialisées ! {total_points_spent} points récupérés",
            "skill_points_refunded": total_points_spent,
            "gold_paid": cost,
        }

    def _get_level_up_bonuses(self, player: Player) -> Dict[str, int]:
        """Get stat bonuses from leveling up"""

        # Already applied in player.level_up()
        return {"max_hp": 10, "max_mana": 5, "max_stamina": 5, "skill_points": 1}


# ============================================================================
# RACIAL BONUSES
# ============================================================================


def apply_racial_bonuses(player: Player):
    """Apply racial stat bonuses at character creation"""

    from ..models.game_entities import Race

    bonuses = {
        Race.HOBBIT: {
            "agility": 2,
            "wisdom": 1,
            "max_hp": -10,
        },
        Race.ELFE: {
            "intelligence": 2,
            "agility": 1,
            "charisma": 1,
        },
        Race.NAIN: {
            "strength": 2,
            "constitution": 2,
            "max_hp": 20,
        },
        Race.HUMAIN: {
            "strength": 1,
            "intelligence": 1,
            "agility": 1,
            "wisdom": 1,
        },
    }

    race_bonuses = bonuses.get(player.race, {})

    for stat, bonus in race_bonuses.items():
        if hasattr(player, stat):
            current_value = getattr(player, stat)
            setattr(player, stat, current_value + bonus)


# ============================================================================
# CLASS STARTING BONUSES
# ============================================================================


def apply_class_bonuses(player: Player):
    """Apply class starting bonuses"""

    bonuses = {
        CharacterClass.GUERRIER: {
            "max_hp": 20,
            "strength": 3,
            "constitution": 2,
        },
        CharacterClass.MAGE: {
            "max_mana": 30,
            "intelligence": 4,
            "wisdom": 2,
        },
        CharacterClass.RANGER: {
            "agility": 3,
            "wisdom": 2,
            "max_stamina": 20,
        },
        CharacterClass.VOLEUR: {
            "agility": 3,
            "charisma": 2,
            "max_stamina": 10,
        },
    }

    class_bonuses = bonuses.get(player.class_type, {})

    for stat, bonus in class_bonuses.items():
        if hasattr(player, stat):
            current_value = getattr(player, stat)
            setattr(player, stat, current_value + bonus)
