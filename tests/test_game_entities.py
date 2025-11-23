import pytest
import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jdvlh_ia_game.models.game_entities import (  # noqa: E402
    Player,
    Item,
    Spell,
    Enemy,
    Quest,
    Objective,
    Race,
    CharacterClass,
    ItemType,
    ItemRarity,
    SpellElement,
    EnemyType,
    AIStrategy,
    QuestStatus,
    ObjectiveType,
)


@pytest.fixture
def sample_player():
    """Sample player fixture"""
    return Player(
        player_id="p1",
        name="Aragorn",
        race=Race.HUMAIN,
        class_type=CharacterClass.GUERRIER,
        level=1,
        xp=0,
        hp=100,
        max_hp=100,
        mana=50,
        max_mana=50,
        stamina=100,
        max_stamina=100,
        strength=10,
        intelligence=10,
        agility=10,
        wisdom=10,
        constitution=10,
        charisma=10,
        skill_points=0,
        learned_skills=[],
        inventory=[],
        equipped={},
        gold=100,
        current_location="la Comté",
        active_quests=[],
        completed_quests=[],
        npc_reputation={},
    )


@pytest.fixture
def sample_item():
    """Sample item fixture"""
    return Item(
        item_id="i1",
        name="Épée de Fer",
        type=ItemType.WEAPON,
        rarity=ItemRarity.COMMON,
        damage=15,
        armor=0,
        magic_power=0,
        strength_bonus=2,
        intelligence_bonus=0,
        agility_bonus=0,
        hp_bonus=0,
        mana_bonus=0,
        stackable=False,
        quantity=1,
        value=50,
        description="Une épée basique.",
    )


@pytest.fixture
def sample_enemy():
    """Sample enemy fixture"""
    return Enemy(
        enemy_id="e1",
        name="Orc",
        type=EnemyType.ORC,
        level=1,
        hp=80,
        max_hp=80,
        damage=12,
        armor=2,
        strength=12,
        agility=8,
        ai_strategy=AIStrategy.AGGRESSIVE,
        skills=[],
        loot_table={"i1": 0.3},
        gold_drop_min=10,
        gold_drop_max=20,
        xp_reward=50,
    )


@pytest.fixture
def sample_objective():
    """Sample objective fixture"""
    return Objective(
        objective_id="o1",
        type=ObjectiveType.COMBAT,
        description="Tuer 3 orcs",
        target="orc",
        target_quantity=3,
        current_progress=0,
        completed=False,
    )


@pytest.fixture
def sample_quest(sample_objective):
    """Sample quest fixture"""
    return Quest(
        quest_id="q1",
        title="Chasse aux Orques",
        description="Éliminez la menace orc.",
        objectives=[sample_objective],
        xp_reward=200,
        gold_reward=100,
        item_rewards=["i1"],
        status=QuestStatus.ACTIVE,
        is_main_quest=False,
    )


class TestPlayer:
    def test_init(self, sample_player):
        assert sample_player.player_id == "p1"
        assert sample_player.name == "Aragorn"
        assert sample_player.level == 1
        assert sample_player.hp == 100

    def test_gain_xp_level_up(self, sample_player):
        sample_player.xp = 90
        assert sample_player.gain_xp(20)
        assert sample_player.level == 2
        assert sample_player.xp == 0
        assert sample_player.skill_points == 1
        assert sample_player.max_hp == 110

    def test_take_damage(self, sample_player):
        assert not sample_player.take_damage(50)
        assert sample_player.hp == 50

    def test_to_dict(self, sample_player):
        d = sample_player.to_dict()
        assert d["player_id"] == "p1"


class TestItem:
    def test_init(self, sample_item):
        assert sample_item.item_id == "i1"
        assert sample_item.damage == 15

    def test_to_dict(self, sample_item):
        d = sample_item.to_dict()
        assert d["type"] == "weapon"


class TestEnemy:
    def test_take_damage(self, sample_enemy):
        assert not sample_enemy.take_damage(40)
        assert sample_enemy.hp == 40

    def test_is_alive(self, sample_enemy):
        assert sample_enemy.is_alive()
        sample_enemy.hp = 0
        assert not sample_enemy.is_alive()


class TestObjective:
    def test_update_progress(self, sample_objective):
        assert not sample_objective.update_progress(2)
        assert sample_objective.current_progress == 2
        assert not sample_objective.completed
        sample_objective.update_progress(1)
        assert sample_objective.completed


class TestQuest:
    def test_is_completed(self, sample_quest):
        sample_quest.objectives[0].completed = True
        assert sample_quest.is_completed()

    def test_complete(self, sample_quest):
        sample_quest.complete()
        assert sample_quest.status == QuestStatus.COMPLETED


@pytest.fixture
def sample_spell():
    return Spell(
        spell_id="s1",
        name="Boule de Feu",
        element=SpellElement.FIRE,
        mana_cost=20,
        damage=30,
    )


class TestSpell:
    def test_can_cast(self, sample_player, sample_spell):
        assert sample_spell.can_cast(sample_player)
        sample_player.mana = 10
        assert not sample_spell.can_cast(sample_player)


class TestEnums:
    def test_enums(self):
        assert Race.HUMAIN.value == "humain"
        assert ItemType.WEAPON.value == "weapon"
        assert QuestStatus.ACTIVE.value == "active"
