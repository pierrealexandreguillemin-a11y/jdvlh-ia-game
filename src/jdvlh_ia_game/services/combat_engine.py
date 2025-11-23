"""
Combat Engine - Tactical combat system for JDR narratif
Handles turn-based combat with AI enemies, damage calculation, and loot distribution
"""

import random
from typing import List, Dict, Any, Tuple
import ollama

from ..models.game_entities import (
    Player,
    Enemy,
    CombatState,
    CombatAction,
    CombatResult,
    Item,
    AIStrategy,
    ItemType,
    ItemRarity,
)
from .model_router import get_router, TaskType


class CombatEngine:
    """Manages tactical turn-based combat"""

    def __init__(self):
        self.router = get_router()
        self.active_combats: Dict[str, CombatState] = {}

    async def start_combat(
        self, player: Player, enemies: List[Enemy], location: str
    ) -> CombatState:
        """
        Initialize a new combat encounter

        Args:
            player: The player character
            enemies: List of enemies to fight
            location: Where the combat takes place

        Returns:
            CombatState: The initialized combat state
        """

        # Generate combat ID
        combat_id = f"combat_{player.player_id}_{random.randint(1000, 9999)}"

        # Generate epic intro narrative
        enemy_names = ", ".join([e.name for e in enemies])
        model, options = self.router.select_model(
            prompt=f"Un combat épique commence à {location}",
            context="",
            task_type=TaskType.EPIC_ACTION,
        )

        intro_prompt = f"""Décris en 2-3 phrases le début d'un combat épique à {location}.
Le joueur {player.name} (niveau {player.level}) fait face à : {enemy_names}.
Adapté pour enfants 10-14 ans, ton excitant mais pas violent."""

        intro_narrative = await self._generate_narrative(
            model=model, prompt=intro_prompt, options=options
        )

        # Create combat state
        combat_state = CombatState(
            combat_id=combat_id,
            player=player,
            enemies=enemies,
            intro_text=intro_narrative,
        )

        self.active_combats[combat_id] = combat_state

        return combat_state

    async def execute_turn(
        self, combat_state: CombatState, action: CombatAction
    ) -> CombatResult:
        """
        Execute a combat turn (player action + enemy responses)

        Args:
            combat_state: Current combat state
            action: Player's action

        Returns:
            CombatResult: Result of the turn
        """

        result = CombatResult()

        # Validate action
        if not combat_state.player_turn:
            result.narrative = "Ce n'est pas votre tour !"
            return result

        if combat_state.is_over():
            result.narrative = "Le combat est terminé !"
            return result

        # Execute player action
        if action.action_type == "attack":
            damage, narrative = await self._execute_attack(
                combat_state, action.target_index
            )
            result.player_damage = damage
            result.narrative = narrative
            result.animations.append("attack")

        elif action.action_type == "cast_spell":
            damage, narrative = await self._execute_spell(
                combat_state, action.spell_id, action.target_index
            )
            result.player_damage = damage
            result.narrative = narrative
            result.animations.append(f"cast_{action.spell_id}")

        elif action.action_type == "use_item":
            narrative = await self._execute_item_use(combat_state, action.item_id)
            result.narrative = narrative
            result.animations.append("use_item")

        elif action.action_type == "defend":
            result.narrative = (
                f"{combat_state.player.name} se met en position défensive !"
            )
            # Bonus armor for this turn (implement in future)

        # Check if enemy defeated
        target_enemy = combat_state.enemies[action.target_index]
        if not target_enemy.is_alive():
            result.narrative += f"\n\n💀 {target_enemy.name} est vaincu !"

        # Check for victory
        if combat_state.is_victory():
            result.is_victory = True
            loot, gold, xp = self._distribute_loot(combat_state.enemies)
            result.loot = loot
            result.gold_gained = gold
            result.xp_gained = xp

            combat_state.player.gold += gold
            combat_state.player.gain_xp(xp)

            result.narrative += (
                f"\n\n🏆 Victoire ! Vous gagnez {xp} XP et {gold} pièces d'or !"
            )

            # Remove from active combats
            if combat_state.combat_id in self.active_combats:
                del self.active_combats[combat_state.combat_id]

            return result

        # Enemy turn (if combat not over)
        combat_state.next_turn()
        enemy_damages = await self._enemy_turn(combat_state)
        result.enemy_damages = enemy_damages

        # Check for defeat
        if combat_state.is_defeat():
            result.is_defeat = True
            result.narrative += "\n\n💀 Vous êtes vaincu... L'aventure s'arrête ici."

            # Remove from active combats
            if combat_state.combat_id in self.active_combats:
                del self.active_combats[combat_state.combat_id]

        combat_state.next_turn()  # Back to player turn

        return result

    async def _execute_attack(
        self, combat_state: CombatState, target_index: int
    ) -> Tuple[int, str]:
        """Execute basic attack"""

        player = combat_state.player
        enemy = combat_state.enemies[target_index]

        # Calculate damage
        damage = self._calculate_damage(
            attacker_strength=player.strength,
            weapon_damage=self._get_equipped_weapon_damage(player),
            defender_armor=enemy.armor,
        )

        # Apply damage
        enemy.take_damage(damage)

        # Generate narrative
        model, options = self.router.select_model(
            prompt="action combat rapide", context="", task_type=TaskType.QUICK_RESPONSE
        )

        narrative_prompt = (
            f"""En 1 phrase courte: {player.name} attaque {enemy.name} et "
            f"inflige {damage} dégâts.\nTon excitant adapté enfants. "
            f"HP restant ennemi: {enemy.hp}/{enemy.max_hp}."""
        )

        narrative = await self._generate_narrative(model, narrative_prompt, options)

        return damage, narrative

    async def _execute_spell(
        self, combat_state: CombatState, spell_id: str, target_index: int
    ) -> Tuple[int, str]:
        """Execute spell cast"""

        # TODO: Implement full spell system
        # For now, basic fireball
        player = combat_state.player
        enemy = combat_state.enemies[target_index]

        mana_cost = 20
        base_damage = player.intelligence * 2

        if player.mana < mana_cost:
            return 0, "Pas assez de mana !"

        player.mana -= mana_cost

        # Calculate spell damage
        damage = int(base_damage * random.uniform(0.8, 1.2))
        enemy.take_damage(damage)

        # Generate narrative
        model, options = self.router.select_model(
            prompt="sort magique épique", context="", task_type=TaskType.EPIC_ACTION
        )

        narrative_prompt = (
            f"""En 2 phrases: {player.name} lance un sort de feu puissant """
            f"""sur {enemy.name} !\n{damage} dégâts infligés. Ton épique """
            f"""adapté enfants."""
        )

        narrative = await self._generate_narrative(
            model, narrative_prompt, options
        )

        return damage, narrative

    async def _execute_item_use(self, combat_state: CombatState, item_id: str) -> str:
        """Execute item use (potion, etc.)"""

        player = combat_state.player

        # Find item in inventory
        item = next((i for i in player.inventory if i.item_id == item_id), None)
        if not item:
            return "Vous n'avez pas cet objet !"

        # Use item (basic potion logic)
        if item.type == ItemType.POTION:
            heal_amount = 50
            player.heal(heal_amount)

            # Remove item
            player.inventory.remove(item)

            return f"Vous buvez une {item.name} et récupérez {heal_amount} HP !"

        return "Cet objet ne peut pas être utilisé en combat."

    async def _enemy_turn(self, combat_state: CombatState) -> List[int]:
        """Execute all enemies' turns"""

        damages = []

        for enemy in combat_state.enemies:
            if not enemy.is_alive():
                damages.append(0)
                continue

            # AI decision
            action = self._decide_enemy_action(enemy, combat_state)

            if action == "attack":
                damage = self._calculate_damage(
                    attacker_strength=enemy.strength,
                    weapon_damage=enemy.damage,
                    defender_armor=self._get_player_total_armor(combat_state.player),
                )

                combat_state.player.take_damage(damage)
                damages.append(damage)

        return damages

    def _decide_enemy_action(self, enemy: Enemy, combat_state: CombatState) -> str:
        """AI decision making for enemy"""

        if enemy.ai_strategy == AIStrategy.AGGRESSIVE:
            return "attack"  # Always attack

        elif enemy.ai_strategy == AIStrategy.DEFENSIVE:
            # Attack if HP > 50%, defend otherwise
            hp_percent = enemy.hp / enemy.max_hp
            return "attack" if hp_percent > 0.5 else "defend"

        else:  # BALANCED or TACTICAL
            return "attack"

    def _calculate_damage(
        self, attacker_strength: int, weapon_damage: int, defender_armor: int
    ) -> int:
        """Calculate damage with armor reduction and critical hits"""

        # Base damage
        base_damage = attacker_strength + weapon_damage

        # Armor reduction (diminishing returns)
        damage_multiplier = 100 / (100 + defender_armor)
        damage = int(base_damage * damage_multiplier)

        # Critical hit (10% chance)
        if random.random() < 0.1:
            damage = int(damage * 2)

        # Random variance (±10%)
        damage = int(damage * random.uniform(0.9, 1.1))

        return max(1, damage)  # Minimum 1 damage

    def _get_equipped_weapon_damage(self, player: Player) -> int:
        """Get damage from equipped weapon"""

        weapon = player.equipped.get("weapon_main")
        if weapon and weapon.type == ItemType.WEAPON:
            return weapon.damage

        return 5  # Base fist damage

    def _get_player_total_armor(self, player: Player) -> int:
        """Calculate total armor from equipped items"""

        total_armor = 0

        for slot, item in player.equipped.items():
            if item and item.type == ItemType.ARMOR:
                total_armor += item.armor

        return total_armor

    def _distribute_loot(self, enemies: List[Enemy]) -> Tuple[List[Item], int, int]:
        """Distribute loot from defeated enemies"""

        items = []
        total_gold = 0
        total_xp = 0

        for enemy in enemies:
            # Gold
            gold = random.randint(enemy.gold_drop_min, enemy.gold_drop_max)
            total_gold += gold

            # XP
            total_xp += enemy.xp_reward

            # Items (basic loot system)
            for item_id, drop_chance in enemy.loot_table.items():
                if random.random() < drop_chance:
                    # Create item (simplified - would use item database)
                    item = Item(
                        item_id=item_id,
                        name=item_id.replace("_", " ").title(),
                        type=ItemType.MATERIAL,
                        rarity=ItemRarity.COMMON,
                    )
                    items.append(item)

        return items, total_gold, total_xp

    async def _generate_narrative(
        self, model: str, prompt: str, options: Dict[str, Any]
    ) -> str:
        """Generate narrative text using Ollama"""

        try:
            response = ollama.generate(model=model, prompt=prompt, options=options)
            return response["response"].strip()

        except Exception as e:
            print(f"Narrative generation failed: {e}")
            return "Le combat continue de manière intense..."


# ============================================================================
# COMBAT TEMPLATES & PRESETS
# ============================================================================

ENEMY_TEMPLATES = {
    "orc_faible": Enemy(
        enemy_id="orc_01",
        name="Orc des plaines",
        type="orc",
        level=1,
        hp=50,
        max_hp=50,
        damage=10,
        armor=5,
        strength=12,
        agility=8,
        ai_strategy=AIStrategy.AGGRESSIVE,
        gold_drop_min=5,
        gold_drop_max=15,
        xp_reward=50,
    ),
    "gobelin_sournois": Enemy(
        enemy_id="gobelin_01",
        name="Gobelin des cavernes",
        type="gobelin",
        level=1,
        hp=30,
        max_hp=30,
        damage=8,
        armor=3,
        strength=8,
        agility=14,
        ai_strategy=AIStrategy.TACTICAL,
        gold_drop_min=3,
        gold_drop_max=10,
        xp_reward=40,
    ),
    "troll_montagne": Enemy(
        enemy_id="troll_01",
        name="Troll des montagnes",
        type="troll",
        level=5,
        hp=200,
        max_hp=200,
        damage=25,
        armor=15,
        strength=20,
        agility=5,
        ai_strategy=AIStrategy.BALANCED,
        gold_drop_min=50,
        gold_drop_max=100,
        xp_reward=250,
    ),
}
