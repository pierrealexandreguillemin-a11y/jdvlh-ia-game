"""
Game entities models for JDR narratif IA + Godot
Defines Player, Item, Spell, Enemy, Quest, and related classes
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class Race(str, Enum):
    """Character races"""
    HOBBIT = "hobbit"
    ELFE = "elfe"
    NAIN = "nain"
    HUMAIN = "humain"


class CharacterClass(str, Enum):
    """Character classes"""
    GUERRIER = "guerrier"
    MAGE = "mage"
    RANGER = "ranger"
    VOLEUR = "voleur"


class ItemType(str, Enum):
    """Item types"""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    QUEST_ITEM = "quest_item"
    CONSUMABLE = "consumable"
    MATERIAL = "material"


class ItemRarity(str, Enum):
    """Item rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class SpellElement(str, Enum):
    """Spell elements"""
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    HEALING = "healing"
    EARTH = "earth"
    WIND = "wind"


class EnemyType(str, Enum):
    """Enemy types"""
    ORC = "orc"
    GOBELIN = "gobelin"
    TROLL = "troll"
    LOUP_GAROU = "loup-garou"
    DRAGON = "dragon"
    ARAIGNEE = "araignée"
    SPECTRE = "spectre"


class AIStrategy(str, Enum):
    """AI combat strategies"""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    TACTICAL = "tactical"


class QuestStatus(str, Enum):
    """Quest statuses"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class ObjectiveType(str, Enum):
    """Quest objective types"""
    TRAVEL = "travel"
    COMBAT = "combat"
    COLLECT = "collect"
    USE_ITEM = "use_item"
    TALK_TO_NPC = "talk_to_npc"


# ============================================================================
# PLAYER
# ============================================================================

@dataclass
class Player:
    """Main player character"""

    # Identity
    player_id: str
    name: str
    race: Race
    class_type: CharacterClass

    # Stats
    level: int = 1
    xp: int = 0
    hp: int = 100
    max_hp: int = 100
    mana: int = 50
    max_mana: int = 50
    stamina: int = 100
    max_stamina: int = 100

    # Attributes
    strength: int = 10
    intelligence: int = 10
    agility: int = 10
    wisdom: int = 10
    constitution: int = 10
    charisma: int = 10

    # Progression
    skill_points: int = 0
    learned_skills: List[str] = field(default_factory=list)

    # Inventory
    inventory: List['Item'] = field(default_factory=list)
    equipped: Dict[str, 'Item'] = field(default_factory=dict)
    gold: int = 100

    # Position
    current_location: str = "la Comté"

    # Quests
    active_quests: List['Quest'] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)

    # Relations
    npc_reputation: Dict[str, int] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_played: datetime = field(default_factory=datetime.now)

    def gain_xp(self, amount: int) -> bool:
        """Add XP and check for level up"""
        self.xp += amount
        required_xp = self.xp_for_next_level()

        if self.xp >= required_xp:
            self.level_up()
            return True
        return False

    def xp_for_next_level(self) -> int:
        """Calculate XP required for next level"""
        return int(100 * (1.5 ** (self.level - 1)))

    def level_up(self):
        """Level up the player"""
        self.level += 1
        self.xp = 0
        self.skill_points += 1

        # Increase stats
        self.max_hp += 10
        self.max_mana += 5
        self.max_stamina += 5

        # Heal to full
        self.hp = self.max_hp
        self.mana = self.max_mana
        self.stamina = self.max_stamina

    def take_damage(self, damage: int) -> bool:
        """Take damage, return True if dead"""
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0

    def heal(self, amount: int):
        """Heal HP"""
        self.hp = min(self.max_hp, self.hp + amount)

    def restore_mana(self, amount: int):
        """Restore mana"""
        self.mana = min(self.max_mana, self.mana + amount)

    def can_afford(self, cost: int) -> bool:
        """Check if player has enough gold"""
        return self.gold >= cost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "race": self.race.value,
            "class_type": self.class_type.value,
            "level": self.level,
            "xp": self.xp,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "strength": self.strength,
            "intelligence": self.intelligence,
            "agility": self.agility,
            "wisdom": self.wisdom,
            "constitution": self.constitution,
            "charisma": self.charisma,
            "skill_points": self.skill_points,
            "learned_skills": self.learned_skills,
            "gold": self.gold,
            "current_location": self.current_location,
        }


# ============================================================================
# ITEM
# ============================================================================

@dataclass
class Item:
    """Game item (weapon, armor, potion, etc.)"""

    item_id: str
    name: str
    type: ItemType
    rarity: ItemRarity

    # Stats (if equipment)
    damage: int = 0
    armor: int = 0
    magic_power: int = 0

    # Bonuses
    strength_bonus: int = 0
    intelligence_bonus: int = 0
    agility_bonus: int = 0
    hp_bonus: int = 0
    mana_bonus: int = 0

    # Properties
    stackable: bool = False
    quantity: int = 1
    value: int = 10  # Gold value

    # Description
    description: str = ""

    # Visual (for Godot)
    icon_path: str = ""
    model_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "type": self.type.value,
            "rarity": self.rarity.value,
            "damage": self.damage,
            "armor": self.armor,
            "magic_power": self.magic_power,
            "strength_bonus": self.strength_bonus,
            "intelligence_bonus": self.intelligence_bonus,
            "agility_bonus": self.agility_bonus,
            "hp_bonus": self.hp_bonus,
            "mana_bonus": self.mana_bonus,
            "stackable": self.stackable,
            "quantity": self.quantity,
            "value": self.value,
            "description": self.description,
        }


# ============================================================================
# SPELL
# ============================================================================

@dataclass
class Spell:
    """Magic spell"""

    spell_id: str
    name: str
    element: SpellElement
    mana_cost: int

    # Effects
    damage: int = 0
    healing: int = 0

    # Mechanics
    cooldown: int = 0  # Turns
    area_of_effect: bool = False

    # Description
    description: str = ""

    # Godot animations
    cast_animation: str = "cast_spell"
    effect_scene: str = ""

    def can_cast(self, player: Player) -> bool:
        """Check if player can cast this spell"""
        return player.mana >= self.mana_cost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "spell_id": self.spell_id,
            "name": self.name,
            "element": self.element.value,
            "mana_cost": self.mana_cost,
            "damage": self.damage,
            "healing": self.healing,
            "cooldown": self.cooldown,
            "area_of_effect": self.area_of_effect,
            "description": self.description,
        }


# ============================================================================
# ENEMY
# ============================================================================

@dataclass
class Enemy:
    """Enemy/monster"""

    enemy_id: str
    name: str
    type: EnemyType
    level: int

    # Stats
    hp: int
    max_hp: int
    damage: int
    armor: int

    # Attributes
    strength: int = 10
    agility: int = 10

    # AI Combat
    ai_strategy: AIStrategy = AIStrategy.BALANCED
    skills: List[str] = field(default_factory=list)

    # Loot
    loot_table: Dict[str, float] = field(default_factory=dict)  # item_id: drop_chance
    gold_drop_min: int = 0
    gold_drop_max: int = 10
    xp_reward: int = 50

    # Visual (for Godot)
    model_path: str = ""

    def take_damage(self, damage: int) -> bool:
        """Take damage, return True if dead"""
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0

    def is_alive(self) -> bool:
        """Check if enemy is alive"""
        return self.hp > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enemy_id": self.enemy_id,
            "name": self.name,
            "type": self.type.value,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "damage": self.damage,
            "armor": self.armor,
            "ai_strategy": self.ai_strategy.value,
        }


# ============================================================================
# QUEST
# ============================================================================

@dataclass
class Objective:
    """Quest objective"""

    objective_id: str
    type: ObjectiveType
    description: str
    target: str  # location, enemy_id, item_id, npc_id, etc.
    target_quantity: int = 1
    current_progress: int = 0
    completed: bool = False

    def update_progress(self, amount: int = 1) -> bool:
        """Update progress, return True if completed"""
        self.current_progress = min(self.target_quantity, self.current_progress + amount)
        self.completed = self.current_progress >= self.target_quantity
        return self.completed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "objective_id": self.objective_id,
            "type": self.type.value,
            "description": self.description,
            "target": self.target,
            "target_quantity": self.target_quantity,
            "current_progress": self.current_progress,
            "completed": self.completed,
        }


@dataclass
class Quest:
    """Quest/mission"""

    quest_id: str
    title: str
    description: str
    objectives: List[Objective]

    # Rewards
    xp_reward: int = 0
    gold_reward: int = 0
    item_rewards: List[str] = field(default_factory=list)  # item_ids

    # Status
    status: QuestStatus = QuestStatus.ACTIVE
    is_main_quest: bool = False

    # Metadata
    accepted_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def is_completed(self) -> bool:
        """Check if all objectives are completed"""
        return all(obj.completed for obj in self.objectives)

    def complete(self):
        """Mark quest as completed"""
        self.status = QuestStatus.COMPLETED
        self.completed_at = datetime.now()

    def fail(self):
        """Mark quest as failed"""
        self.status = QuestStatus.FAILED
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "xp_reward": self.xp_reward,
            "gold_reward": self.gold_reward,
            "item_rewards": self.item_rewards,
            "status": self.status.value,
            "is_main_quest": self.is_main_quest,
        }


# ============================================================================
# COMBAT STATE
# ============================================================================

@dataclass
class CombatAction:
    """Combat action"""

    action_type: str  # "attack", "cast_spell", "use_item", "defend"
    target_index: int = 0
    spell_id: Optional[str] = None
    item_id: Optional[str] = None


@dataclass
class CombatState:
    """State of an ongoing combat"""

    combat_id: str
    player: Player
    enemies: List[Enemy]
    turn: int = 1
    player_turn: bool = True
    intro_text: str = ""

    # Cooldowns
    spell_cooldowns: Dict[str, int] = field(default_factory=dict)

    def is_victory(self) -> bool:
        """Check if all enemies are defeated"""
        return all(not enemy.is_alive() for enemy in self.enemies)

    def is_defeat(self) -> bool:
        """Check if player is defeated"""
        return self.player.hp <= 0

    def is_over(self) -> bool:
        """Check if combat is over"""
        return self.is_victory() or self.is_defeat()

    def next_turn(self):
        """Advance to next turn"""
        self.turn += 1
        self.player_turn = not self.player_turn

        # Reduce cooldowns
        for spell_id in list(self.spell_cooldowns.keys()):
            self.spell_cooldowns[spell_id] -= 1
            if self.spell_cooldowns[spell_id] <= 0:
                del self.spell_cooldowns[spell_id]


@dataclass
class CombatResult:
    """Result of a combat turn"""

    player_damage: int = 0
    enemy_damages: List[int] = field(default_factory=list)
    narrative: str = ""
    is_victory: bool = False
    is_defeat: bool = False
    animations: List[str] = field(default_factory=list)
    loot: List[Item] = field(default_factory=list)
    gold_gained: int = 0
    xp_gained: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "player_damage": self.player_damage,
            "enemy_damages": self.enemy_damages,
            "narrative": self.narrative,
            "is_victory": self.is_victory,
            "is_defeat": self.is_defeat,
            "animations": self.animations,
            "loot": [item.to_dict() for item in self.loot],
            "gold_gained": self.gold_gained,
            "xp_gained": self.xp_gained,
        }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    'Race', 'CharacterClass', 'ItemType', 'ItemRarity',
    'SpellElement', 'EnemyType', 'AIStrategy',
    'QuestStatus', 'ObjectiveType',

    # Entities
    'Player', 'Item', 'Spell', 'Enemy',
    'Quest', 'Objective',

    # Combat
    'CombatAction', 'CombatState', 'CombatResult',
]
