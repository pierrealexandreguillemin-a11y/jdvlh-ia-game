import asyncio
from typing import Any, Dict, List
from pathlib import Path

import yaml
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# from ..middleware.security import security_middleware  # Temporary comment
from ..services.cache import CacheService
from ..services.event_bus import EventBus
from ..services.narrative import NarrativeService
from ..services.state_manager import StateManager
from ..services.combat_engine import CombatEngine
from ..services.inventory_manager import InventoryManager
from ..services.quest_manager import QuestManager
from ..services.character_progression import CharacterProgression
from ..models.game_entities import (
    Player,
    Enemy,
    Item,
    Quest,
    Race,
    CharacterClass,
    EnemyType,
)

# Chemin absolu vers config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="JDVLH IA Game Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(security_middleware)  # Temporairement commenté pour syntaxe security.py


class NarrativeResponse(BaseModel):
    narrative: str
    choices: List[str]
    location: str
    animation_trigger: str = "none"
    sfx: str = "ambient"


def get_narrative_service() -> NarrativeService:
    return NarrativeService()


def get_cache_service() -> CacheService:
    return CacheService()


def get_state_manager() -> StateManager:
    return StateManager()


def get_event_bus() -> EventBus:
    return EventBus()


def get_combat_engine() -> CombatEngine:
    return CombatEngine()


def get_inventory_manager() -> InventoryManager:
    return InventoryManager()


def get_quest_manager() -> QuestManager:
    return QuestManager()


def get_character_progression() -> CharacterProgression:
    return CharacterProgression()


@app.on_event("startup")
async def startup_event():
    state_manager = get_state_manager()
    cache_service = get_cache_service()
    asyncio.create_task(cache_service.pregenerate())
    asyncio.create_task(state_manager.cleanup_inactive())
    if state_manager.get_active_count() >= config["server"]["max_players"]:
        print("Attention: limite max_players atteinte")


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    player_id: str,
    narrative_service: NarrativeService = Depends(get_narrative_service),
    cache_service: CacheService = Depends(get_cache_service),
    state_manager: StateManager = Depends(get_state_manager),
    event_bus: EventBus = Depends(get_event_bus),
):
    if state_manager.get_active_count() >= config["server"]["max_players"]:
        await websocket.close(code=503, reason="Serveur plein")
        return

    await websocket.accept()
    state = state_manager.load_state(player_id)

    loc_data = cache_service.get_location_data(state["current_location"])
    welcome = {
        "narrative": "Bienvenue en Terre du Milieu ! Que fais-tu dans la Comté ?",
        "choices": ["Explorer la forêt", "Rencontrer un hobbit", "Chercher un trésor"],
        **loc_data,
    }
    await websocket.send_json(welcome)

    try:
        while True:
            choice = await websocket.receive_text()
            blacklist = config.get("blacklist_words", [])
            response = await narrative_service.generate(
                state["context"], state["history"], choice, blacklist
            )
            state["history"].append(f"Joueur: {choice}")
            state["history"].append(f"MJ: {response['narrative']}")
            if len(state["history"]) > 30:
                state["history"] = state["history"][-20:]
            state["current_location"] = response["location"]
            state_manager.save_state(player_id, state)
            loc_data = cache_service.get_location_data(state["current_location"])
            full_response = {**response, **loc_data}
            await websocket.send_json(full_response)
            event_bus.emit("narrative_generated", full_response)
    except WebSocketDisconnect:
        print(f"Joueur {player_id} déconnecté")


@app.post("/reset/{player_id}")
async def reset_game(
    player_id: str, state_manager: StateManager = Depends(get_state_manager)
):
    state = {
        "context": config["prompts"]["system"],
        "history": [],
        "current_location": "la Comté",
    }
    state_manager.save_state(player_id, state)
    return {"status": "Partie réinitialisée"}


# ===== COMBAT WEBSOCKET =====
@app.websocket("/ws/combat/{player_id}")
async def combat_websocket(
    websocket: WebSocket,
    player_id: str,
    combat_engine: CombatEngine = Depends(get_combat_engine),
    state_manager: StateManager = Depends(get_state_manager),
):
    """
    WebSocket pour gérer les combats en temps réel

    Messages REÇUS:
    - start_combat: {"action": "start_combat", "enemies": ["orc_01"]}
    - attack: {"action": "attack", "target_index": 0}
    - cast_spell: {"action": "cast_spell", "spell_id": "fireball", "target_index": 0}
    - use_item: {"action": "use_item", "item_id": "health_potion"}
    - defend: {"action": "defend"}

    Messages ENVOYÉS:
    - combat_start: {type, combat_id, intro, enemies, player}
    - combat_result: {type, narrative, damages, animations, states}
    - combat_end: {type, victory, narrative, loot, rewards}
    """
    await websocket.accept()
    active_combat = None

    # Load or create player
    player = _load_or_create_player(player_id, state_manager)

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")

            if action == "start_combat":
                # Create enemies
                enemy_types = message.get("enemies", ["orc_01"])
                enemies = _create_enemies_from_ids(enemy_types)

                # Start combat
                combat_state = await combat_engine.start_combat(
                    player, enemies, player.current_location
                )
                active_combat = combat_state

                await websocket.send_json(
                    {
                        "type": "combat_start",
                        "combat_id": combat_state.combat_id,
                        "intro": combat_state.intro_text,
                        "enemies": [_enemy_to_dict(e) for e in enemies],
                        "player": {
                            "hp": player.hp,
                            "max_hp": player.max_hp,
                            "mana": player.mana,
                            "max_mana": player.max_mana,
                        },
                    }
                )

            elif action in ["attack", "cast_spell", "use_item", "defend"]:
                if not active_combat:
                    await websocket.send_json(
                        {"type": "error", "message": "Aucun combat actif"}
                    )
                    continue

                # Execute combat turn
                from ..models.game_entities import CombatAction

                combat_action = CombatAction(
                    action_type=action,
                    target_index=message.get("target_index", 0),
                    spell_id=message.get("spell_id"),
                    item_id=message.get("item_id"),
                )

                result = await combat_engine.execute_turn(active_combat, combat_action)

                # Send result
                response = {
                    "type": "combat_result",
                    "narrative": result.narrative,
                    "player_damage": result.player_damage,
                    "enemy_damages": result.enemy_damages,
                    "animations": result.animations,
                    "player": {
                        "hp": active_combat.player.hp,
                        "max_hp": active_combat.player.max_hp,
                        "mana": active_combat.player.mana,
                        "max_mana": active_combat.player.max_mana,
                    },
                    "enemies": [
                        {"hp": e.hp, "max_hp": e.max_hp, "alive": e.is_alive()}
                        for e in active_combat.enemies
                    ],
                }

                if result.is_victory or result.is_defeat:
                    response["type"] = "combat_end"
                    response["victory"] = result.is_victory
                    response["loot"] = [_item_to_dict(item) for item in result.loot]
                    response["gold_gained"] = result.gold_gained
                    response["xp_gained"] = result.xp_gained
                    active_combat = None

                    # Save player state
                    _save_player(player, state_manager)

                await websocket.send_json(response)

    except WebSocketDisconnect:
        print(f"Combat WebSocket disconnected: {player_id}")


# ===== INVENTORY WEBSOCKET =====
@app.websocket("/ws/inventory/{player_id}")
async def inventory_websocket(
    websocket: WebSocket,
    player_id: str,
    inventory_manager: InventoryManager = Depends(get_inventory_manager),
    state_manager: StateManager = Depends(get_state_manager),
):
    """
    WebSocket pour gérer l'inventaire et l'équipement

    Messages REÇUS:
    - get_inventory: {"action": "get_inventory"}
    - equip: {"action": "equip", "item_id": "sword_01", "slot": "weapon_main"}
    - unequip: {"action": "unequip", "slot": "weapon_main"}
    - use_item: {"action": "use_item", "item_id": "health_potion"}
    - drop: {"action": "drop", "item_id": "rusty_sword"}
    """
    await websocket.accept()
    player = _load_or_create_player(player_id, state_manager)

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")

            if action == "get_inventory":
                await websocket.send_json(
                    {
                        "type": "inventory_full",
                        "inventory": [_item_to_dict(item) for item in player.inventory],
                        "equipped": {
                            slot: _item_to_dict(item)
                            for slot, item in player.equipped.items()
                        },
                        "stats": inventory_manager.get_total_stats(player),
                        "gold": player.gold,
                    }
                )

            elif action == "equip":
                result = inventory_manager.equip_item(
                    player, message["item_id"], message["slot"]
                )
                await websocket.send_json(
                    {
                        "type": "item_action_result",
                        **result,
                        "inventory": [_item_to_dict(item) for item in player.inventory],
                        "equipped": {
                            slot: _item_to_dict(item)
                            for slot, item in player.equipped.items()
                        },
                    }
                )
                _save_player(player, state_manager)

            elif action == "unequip":
                result = inventory_manager.unequip_item(player, message["slot"])
                await websocket.send_json(
                    {
                        "type": "item_action_result",
                        **result,
                        "inventory": [_item_to_dict(item) for item in player.inventory],
                        "equipped": {
                            slot: _item_to_dict(item)
                            for slot, item in player.equipped.items()
                        },
                    }
                )
                _save_player(player, state_manager)

            elif action == "use_item":
                result = inventory_manager.use_consumable(player, message["item_id"])
                await websocket.send_json(
                    {
                        "type": "item_action_result",
                        **result,
                        "inventory": [_item_to_dict(item) for item in player.inventory],
                        "player": {
                            "hp": player.hp,
                            "max_hp": player.max_hp,
                            "mana": player.mana,
                            "max_mana": player.max_mana,
                        },
                    }
                )
                _save_player(player, state_manager)

            elif action == "drop":
                result = inventory_manager.remove_item(player, message["item_id"])
                await websocket.send_json(
                    {
                        "type": "item_action_result",
                        **result,
                        "inventory": [_item_to_dict(item) for item in player.inventory],
                    }
                )
                _save_player(player, state_manager)

    except WebSocketDisconnect:
        print(f"Inventory WebSocket disconnected: {player_id}")


# ===== QUESTS WEBSOCKET =====
@app.websocket("/ws/quests/{player_id}")
async def quests_websocket(
    websocket: WebSocket,
    player_id: str,
    quest_manager: QuestManager = Depends(get_quest_manager),
    state_manager: StateManager = Depends(get_state_manager),
):
    """
    WebSocket pour gérer les quêtes

    Messages REÇUS:
    - get_quests: {"action": "get_quests"}
    - accept_quest: {"action": "accept_quest", "quest_id": "q1"}
    - abandon_quest: {"action": "abandon_quest", "quest_id": "q1"}
    - generate_quest: {"action": "generate_quest"}
    """
    await websocket.accept()
    player = _load_or_create_player(player_id, state_manager)

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")

            if action == "get_quests":
                active_quests = [
                    q for q in player.active_quests if q.status.value == "active"
                ]
                completed_quests = [
                    q for q in player.active_quests if q.status.value == "completed"
                ]

                await websocket.send_json(
                    {
                        "type": "quests_list",
                        "active": [_quest_to_dict(q) for q in active_quests],
                        "completed": [_quest_to_dict(q) for q in completed_quests],
                    }
                )

            elif action == "accept_quest":
                # For now, just acknowledge
                await websocket.send_json(
                    {"type": "quest_accepted", "quest_id": message["quest_id"]}
                )

            elif action == "abandon_quest":
                quest_id = message["quest_id"]
                player.active_quests = [
                    q for q in player.active_quests if q.quest_id != quest_id
                ]
                _save_player(player, state_manager)

                await websocket.send_json(
                    {"type": "quest_abandoned", "quest_id": quest_id}
                )

            elif action == "generate_quest":
                # Generate a dynamic quest
                quest = await quest_manager.generate_dynamic_quest(
                    player, player.current_location
                )
                player.active_quests.append(quest)
                _save_player(player, state_manager)

                await websocket.send_json(
                    {"type": "quest_generated", "quest": _quest_to_dict(quest)}
                )

    except WebSocketDisconnect:
        print(f"Quests WebSocket disconnected: {player_id}")


# ===== CHARACTER WEBSOCKET =====
@app.websocket("/ws/character/{player_id}")
async def character_websocket(
    websocket: WebSocket,
    player_id: str,
    character_progression: CharacterProgression = Depends(get_character_progression),
    state_manager: StateManager = Depends(get_state_manager),
):
    """
    WebSocket pour gérer la progression du personnage

    Messages REÇUS:
    - get_character: {"action": "get_character"}
    - allocate_stat: {"action": "allocate_stat", "stat": "strength"}
    - learn_skill: {"action": "learn_skill", "skill_id": "charge"}
    - reset_skills: {"action": "reset_skills"}
    """
    await websocket.accept()
    player = _load_or_create_player(player_id, state_manager)

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")

            if action == "get_character":
                available_skills = character_progression.get_available_skills(player)

                await websocket.send_json(
                    {
                        "type": "character_info",
                        "player": _player_to_dict(player),
                        "available_skills": [
                            _skill_to_dict(s) for s in available_skills
                        ],
                        "learned_skills": [
                            {"skill_id": s, "name": s} for s in player.learned_skills
                        ],
                    }
                )

            elif action == "allocate_stat":
                stat = message["stat"]
                if player.skill_points > 0:
                    # Allocate stat point
                    if hasattr(player, stat):
                        current_value = getattr(player, stat)
                        setattr(player, stat, current_value + 1)
                        player.skill_points -= 1
                        _save_player(player, state_manager)

                        await websocket.send_json(
                            {
                                "type": "stat_allocated",
                                "stat": stat,
                                "new_value": getattr(player, stat),
                                "skill_points_remaining": player.skill_points,
                            }
                        )
                    else:
                        await websocket.send_json(
                            {"type": "error", "message": f"Stat invalide: {stat}"}
                        )
                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Pas assez de points de compétence",
                        }
                    )

            elif action == "learn_skill":
                skill_id = message["skill_id"]
                result = character_progression.learn_skill(player, skill_id)

                if result["success"]:
                    _save_player(player, state_manager)
                    await websocket.send_json(
                        {
                            "type": "skill_learned",
                            "skill": _skill_to_dict(result["skill"]),
                        }
                    )
                else:
                    await websocket.send_json(
                        {"type": "error", "message": result["message"]}
                    )

            elif action == "reset_skills":
                cost = character_progression.calculate_reset_cost(player)
                if player.gold >= cost:
                    player.gold -= cost
                    player.learned_skills = []
                    player.skill_points = player.level  # Restore skill points
                    _save_player(player, state_manager)

                    await websocket.send_json(
                        {
                            "type": "skills_reset",
                            "cost": cost,
                            "skill_points": player.skill_points,
                        }
                    )
                else:
                    await websocket.send_json(
                        {"type": "error", "message": f"Pas assez d'or (coût: {cost})"}
                    )

    except WebSocketDisconnect:
        print(f"Character WebSocket disconnected: {player_id}")


# ===== HELPER FUNCTIONS =====
def _load_or_create_player(player_id: str, state_manager: StateManager) -> Player:
    """Load player from state or create a new one"""
    state = state_manager.load_state(player_id)

    if "player" in state:
        # Load existing player (simplified - would need proper deserialization)
        return Player(
            player_id=player_id,
            name=state["player"].get("name", "Aventurier"),
            race=Race.HUMAIN,
            class_type=CharacterClass.GUERRIER,
            current_location="la Comté",
        )
    else:
        # Create new player
        player = Player(
            player_id=player_id,
            name="Aventurier",
            race=Race.HUMAIN,
            class_type=CharacterClass.GUERRIER,
            current_location="la Comté",
        )
        state["player"] = _player_to_dict(player)
        state_manager.save_state(player_id, state)
        return player


def _save_player(player: Player, state_manager: StateManager):
    """Save player to state"""
    state = state_manager.load_state(player.player_id)
    state["player"] = _player_to_dict(player)
    state_manager.save_state(player.player_id, state)


def _player_to_dict(player: Player) -> Dict[str, Any]:
    """Convert Player to dict"""
    return {
        "player_id": player.player_id,
        "name": player.name,
        "race": (
            player.race.value if hasattr(player.race, "value") else str(player.race)
        ),
        "class_type": (
            player.class_type.value
            if hasattr(player.class_type, "value")
            else str(player.class_type)
        ),
        "level": player.level,
        "xp": player.xp,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "mana": player.mana,
        "max_mana": player.max_mana,
        "gold": player.gold,
        "current_location": player.current_location,
        "skill_points": getattr(player, "skill_points", 0),
        "strength": getattr(player, "strength", 10),
        "intelligence": getattr(player, "intelligence", 10),
        "agility": getattr(player, "agility", 10),
    }


def _enemy_to_dict(enemy: Enemy) -> Dict[str, Any]:
    """Convert Enemy to dict"""
    return {
        "enemy_id": enemy.enemy_id,
        "name": enemy.name,
        "type": (
            enemy.type.value
            if hasattr(enemy.type, "value")
            else str(enemy.type)
        ),
        "level": enemy.level,
        "hp": enemy.hp,
        "max_hp": enemy.max_hp,
        "damage": enemy.damage,
        "armor": enemy.armor,
    }


def _item_to_dict(item: Item) -> Dict[str, Any]:
    """Convert Item to dict"""
    return {
        "item_id": item.item_id,
        "name": item.name,
        "item_type": (
            item.item_type.value
            if hasattr(item.item_type, "value")
            else str(item.item_type)
        ),
        "rarity": (
            item.rarity.value if hasattr(item.rarity, "value") else str(item.rarity)
        ),
        "value": item.value,
        "stackable": item.stackable,
        "quantity": item.quantity,
        "description": item.description,
    }


def _quest_to_dict(quest: Quest) -> Dict[str, Any]:
    """Convert Quest to dict"""
    return {
        "quest_id": quest.quest_id,
        "title": quest.title,
        "description": quest.description,
        "level": quest.level,
        "is_main_quest": quest.is_main_quest,
        "status": (
            quest.status.value if hasattr(quest.status, "value") else str(quest.status)
        ),
        "xp_reward": quest.xp_reward,
        "gold_reward": quest.gold_reward,
        "objectives": [
            {
                "objective_id": obj.objective_id,
                "description": obj.description,
                "current": obj.current_count,
                "target": obj.target_count,
                "completed": obj.is_complete(),
            }
            for obj in quest.objectives
        ],
    }


def _skill_to_dict(skill: Dict[str, Any]) -> Dict[str, Any]:
    """Convert skill to dict (already a dict, just ensure format)"""
    return {
        "skill_id": skill.get("skill_id", ""),
        "name": skill.get("name", ""),
        "description": skill.get("description", ""),
        "level_required": skill.get("level_required", 1),
        "cost": skill.get("cost", 1),
    }


def _create_enemies_from_ids(enemy_ids: List[str]) -> List[Enemy]:
    """Create Enemy instances from IDs"""
    enemies = []
    for enemy_id in enemy_ids:
        # Simple enemy creation based on ID
        if "orc" in enemy_id.lower():
            enemy = Enemy(
                enemy_id=enemy_id,
                name="Orc des plaines",
                type=EnemyType.ORC,
                level=1,
                hp=80,
                max_hp=80,
                damage=15,
                armor=5,
                loot_table={},
            )
        elif "gobelin" in enemy_id.lower():
            enemy = Enemy(
                enemy_id=enemy_id,
                name="Gobelin voleur",
                type=EnemyType.GOBELIN,
                level=1,
                hp=50,
                max_hp=50,
                damage=10,
                armor=3,
                loot_table={},
            )
        else:
            # Default enemy
            enemy = Enemy(
                enemy_id=enemy_id,
                name="Ennemi mystérieux",
                type=EnemyType.GOBELIN,
                level=1,
                hp=60,
                max_hp=60,
                damage=12,
                armor=4,
                loot_table={},
            )
        enemies.append(enemy)
    return enemies
