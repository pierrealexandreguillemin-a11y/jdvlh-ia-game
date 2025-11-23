"""
Quest Manager - Manages quests and objectives
Handles quest progression, rewards, and narrative integration
"""

from typing import Dict, Optional
from datetime import datetime
import ollama

from ..models.game_entities import Player, Quest, Objective, ObjectiveType, QuestStatus
from .model_router import get_router, TaskType
from .inventory_manager import InventoryManager, ITEM_DATABASE


class QuestManager:
    """Manages player quests and objectives"""

    def __init__(self):
        self.router = get_router()
        self.inventory_manager = InventoryManager()

    def start_quest(self, player: Player, quest: Quest) -> Dict[str, any]:
        """
        Start a new quest for the player

        Args:
            player: The player
            quest: The quest to start

        Returns:
            Dict with success status and message
        """

        # Check if quest already active
        if any(q.quest_id == quest.quest_id for q in player.active_quests):
            return {"success": False, "message": "Cette quête est déjà active"}

        # Check if quest already completed
        if quest.quest_id in player.completed_quests:
            return {"success": False, "message": "Cette quête a déjà été accomplie"}

        # Add quest to active quests
        player.active_quests.append(quest)

        return {
            "success": True,
            "message": f"Nouvelle quête: {quest.title}",
            "quest": quest.to_dict(),
        }

    def update_objective(
        self, player: Player, quest_id: str, objective_id: str, progress: int = 1
    ) -> Dict[str, any]:
        """
        Update progress on a quest objective

        Args:
            player: The player
            quest_id: ID of the quest
            objective_id: ID of the objective
            progress: Amount of progress to add

        Returns:
            Dict with success status and completion info
        """

        # Find quest
        quest = self._find_active_quest(player, quest_id)

        if not quest:
            return {"success": False, "message": "Quête non trouvée"}

        # Find objective
        objective = next(
            (obj for obj in quest.objectives if obj.objective_id == objective_id), None
        )

        if not objective:
            return {"success": False, "message": "Objectif non trouvé"}

        # Update progress
        was_completed = objective.completed
        objective.update_progress(progress)

        result = {
            "success": True,
            "objective_completed": objective.completed and not was_completed,
            "quest_completed": quest.is_completed(),
        }

        # Check if quest completed
        if quest.is_completed() and quest.status == QuestStatus.ACTIVE:
            complete_result = self.complete_quest(player, quest_id)
            result.update(complete_result)

        return result

    def complete_quest(self, player: Player, quest_id: str) -> Dict[str, any]:
        """
        Complete a quest and distribute rewards

        Args:
            player: The player
            quest_id: ID of the quest to complete

        Returns:
            Dict with success status and rewards
        """

        # Find quest
        quest = self._find_active_quest(player, quest_id)

        if not quest:
            return {"success": False, "message": "Quête non trouvée"}

        if not quest.is_completed():
            return {
                "success": False,
                "message": "Tous les objectifs ne sont pas accomplis",
            }

        # Mark as completed
        quest.complete()

        # Remove from active quests
        player.active_quests.remove(quest)
        player.completed_quests.append(quest_id)

        # Distribute rewards
        rewards = self._distribute_rewards(player, quest)

        return {
            "success": True,
            "message": f"Quête accomplie: {quest.title} !",
            "rewards": rewards,
        }

    def fail_quest(self, player: Player, quest_id: str) -> Dict[str, any]:
        """
        Fail a quest (e.g., time limit exceeded, wrong choice)

        Args:
            player: The player
            quest_id: ID of the quest to fail

        Returns:
            Dict with success status
        """

        quest = self._find_active_quest(player, quest_id)

        if not quest:
            return {"success": False, "message": "Quête non trouvée"}

        # Mark as failed
        quest.fail()

        # Remove from active quests
        player.active_quests.remove(quest)

        return {"success": True, "message": f"Quête échouée: {quest.title}"}

    def get_quest_progress(self, player: Player, quest_id: str) -> Dict[str, any]:
        """
        Get detailed progress for a quest

        Args:
            player: The player
            quest_id: ID of the quest

        Returns:
            Dict with quest progress details
        """

        quest = self._find_active_quest(player, quest_id)

        if not quest:
            return {"success": False, "message": "Quête non trouvée"}

        total_objectives = len(quest.objectives)
        completed_objectives = sum(1 for obj in quest.objectives if obj.completed)
        progress_percent = int((completed_objectives / total_objectives) * 100)

        return {
            "success": True,
            "quest": quest.to_dict(),
            "progress_percent": progress_percent,
            "completed_objectives": completed_objectives,
            "total_objectives": total_objectives,
        }

    async def generate_dynamic_quest(self, player: Player, location: str) -> Quest:
        """
        Generate a dynamic quest using AI based on player level and location

        Args:
            player: The player
            location: Current location

        Returns:
            Generated Quest
        """

        model, options = self.router.select_model(
            prompt=f"Générer une quête pour niveau {player.level} à {location}",
            context="",
            task_type=TaskType.CREATIVE_STORY,
        )

        prompt = (
            f"""Génère UNE quête courte pour un enfant de 10-14 ans.
Contexte: Joueur niveau {player.level}, classe {player.class_type.value}, "
            f"à {location}.

Réponds en JSON:
{{
  \"title\": \"Titre court\",
  \"description\": \"1-2 phrases\",
  \"objectives\": [
    {{\"type\": \"travel\", \"description\": \"Aller à X\", \"target\": \"lieu\"}},
    {{\"type\": \"collect\", \"description\": \"Trouver Y\", \"target\": \"item_id\"}}
  ],
  \"xp_reward\": {player.level * 50},
  \"gold_reward\": {player.level * 20}
}}"""
        )

        try:
            response = ollama.generate(model=model, prompt=prompt, options=options)
            import json

            quest_data = json.loads(response["response"])

            # Create quest from AI response
            objectives = [
                Objective(
                    objective_id=f"obj_{i}",
                    type=ObjectiveType(obj["type"]),
                    description=obj["description"],
                    target=obj["target"],
                )
                for i, obj in enumerate(quest_data["objectives"])
            ]

            quest = Quest(
                quest_id=f"dyn_quest_{player.player_id}_{int(datetime.now().timestamp())}",
                title=quest_data["title"],
                description=quest_data["description"],
                objectives=objectives,
                xp_reward=quest_data["xp_reward"],
                gold_reward=quest_data["gold_reward"],
            )

            return quest

        except Exception as e:
            print(f"Dynamic quest generation failed: {e}")

            # Fallback to template quest
            return QUEST_TEMPLATES["simple_delivery"]

    def _find_active_quest(self, player: Player, quest_id: str) -> Optional[Quest]:
        """Find an active quest by ID"""
        return next(
            (quest for quest in player.active_quests if quest.quest_id == quest_id),
            None,
        )

    def _distribute_rewards(self, player: Player, quest: Quest) -> Dict[str, any]:
        """Distribute quest rewards to player"""

        rewards = {"xp": 0, "gold": 0, "items": []}

        # XP
        if quest.xp_reward > 0:
            leveled_up = player.gain_xp(quest.xp_reward)
            rewards["xp"] = quest.xp_reward
            rewards["leveled_up"] = leveled_up

        # Gold
        if quest.gold_reward > 0:
            player.gold += quest.gold_reward
            rewards["gold"] = quest.gold_reward

        # Items
        for item_id in quest.item_rewards:
            if item_id in ITEM_DATABASE:
                item = ITEM_DATABASE[item_id]
                self.inventory_manager.add_item(player, item)
                rewards["items"].append(item.to_dict())

        return rewards


# ============================================================================
# QUEST TEMPLATES
# ============================================================================

QUEST_TEMPLATES = {
    "destroy_ring": Quest(
        quest_id="main_quest_ring",
        title="Détruire l'Anneau Unique",
        description=(
            "Apportez l'Anneau Unique au Mont Destin et "
            "détruisez-le pour sauver la Terre du Milieu."
        ),
        objectives=[
            Objective(
                objective_id="obj_1",
                type=ObjectiveType.TRAVEL,
                description="Voyager jusqu'au Mont Destin",
                target="le Mont Destin",
            ),
            Objective(
                objective_id="obj_2",
                type=ObjectiveType.COMBAT,
                description="Vaincre Gollum",
                target="gollum",
            ),
            Objective(
                objective_id="obj_3",
                type=ObjectiveType.USE_ITEM,
                description="Détruire l'Anneau dans les flammes",
                target="ring_of_power",
            ),
        ],
        xp_reward=1000,
        gold_reward=0,
        is_main_quest=True,
    ),
    "help_gandalf": Quest(
        quest_id="quest_gandalf_1",
        title="Aider Gandalf",
        description="Gandalf a besoin de 3 herbes médicinales rares pour un sort important.",
        objectives=[
            Objective(
                objective_id="obj_herbs",
                type=ObjectiveType.COLLECT,
                description="Collecter 3 herbes médicinales",
                target="medical_herb",
                target_quantity=3,
            ),
            Objective(
                objective_id="obj_return",
                type=ObjectiveType.TALK_TO_NPC,
                description="Rapporter les herbes à Gandalf",
                target="gandalf",
            ),
        ],
        xp_reward=100,
        gold_reward=50,
        item_rewards=["health_potion", "health_potion"],
        is_main_quest=False,
    ),
    "defend_village": Quest(
        quest_id="quest_defend_shire",
        title="Défendre la Comté",
        description="Des orcs attaquent la Comté ! Protégez les hobbits.",
        objectives=[
            Objective(
                objective_id="obj_defeat_orcs",
                type=ObjectiveType.COMBAT,
                description="Vaincre 5 orcs",
                target="orc",
                target_quantity=5,
            ),
        ],
        xp_reward=200,
        gold_reward=100,
        item_rewards=["rusty_sword"],
        is_main_quest=False,
    ),
    "simple_delivery": Quest(
        quest_id="quest_delivery_1",
        title="Livraison urgente",
        description="Livrez un colis important à Fondcombe.",
        objectives=[
            Objective(
                objective_id="obj_travel_rivendell",
                type=ObjectiveType.TRAVEL,
                description="Voyager à Fondcombe",
                target="Fondcombe",
            ),
            Objective(
                objective_id="obj_deliver",
                type=ObjectiveType.TALK_TO_NPC,
                description="Livrer le colis à Elrond",
                target="elrond",
            ),
        ],
        xp_reward=75,
        gold_reward=30,
        is_main_quest=False,
    ),
}
