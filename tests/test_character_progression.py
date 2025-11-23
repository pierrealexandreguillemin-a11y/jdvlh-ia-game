import pytest
from datetime import datetime

from jdvlh_ia_game.services.character_progression import (
    CharacterProgression,
    SKILL_TREES,
    apply_racial_bonuses,
    apply_class_bonuses,
)
from jdvlh_ia_game.models.game_entities import Player, CharacterClass, Race


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
        created_at=datetime.now(),
        last_played=datetime.now(),
    )


@pytest.fixture
def progression():
    """Character progression fixture"""
    return CharacterProgression()


class TestCharacterProgression:
    """Tests for CharacterProgression"""

    def test_gain_xp_no_level_up(self, progression, sample_player):
        result = progression.gain_xp(sample_player, 50)
        assert result["leveled_up"] is False
        assert sample_player.xp == 50
        assert sample_player.level == 1

    def test_gain_xp_level_up(self, progression, sample_player):
        sample_player.xp = 90
        result = progression.gain_xp(sample_player, 20)
        assert result["leveled_up"] is True
        assert sample_player.level == 2
        assert sample_player.xp == 0
        assert "new_level" in result

    def test_allocate_stat_point_valid(self, progression, sample_player):
        sample_player.skill_points = 1
        result = progression.allocate_stat_point(sample_player, "strength")
        assert result["success"] is True
        assert sample_player.strength == 11
        assert sample_player.skill_points == 0

    def test_allocate_stat_point_no_points(self, progression, sample_player):
        result = progression.allocate_stat_point(sample_player, "strength")
        assert result["success"] is False

    def test_allocate_stat_point_invalid_stat(self, progression, sample_player):
        sample_player.skill_points = 1
        result = progression.allocate_stat_point(sample_player, "invalid")
        assert result["success"] is False

    def test_learn_skill_valid(self, progression, sample_player):
        sample_player.level = 2
        sample_player.skill_points = 1
        result = progression.learn_skill(sample_player, "charge")
        assert result["success"] is True
        assert "charge" in sample_player.learned_skills
        assert sample_player.skill_points == 0

    def test_learn_skill_level_too_low(self, progression, sample_player):
        sample_player.skill_points = 1
        result = progression.learn_skill(sample_player, "charge")
        assert result["success"] is False
        assert "Niveau 2 requis" in result["message"]

    def test_learn_skill_already_learned(self, progression, sample_player):
        sample_player.level = 2
        sample_player.skill_points = 1
        sample_player.learned_skills = ["charge"]
        result = progression.learn_skill(sample_player, "charge")
        assert result["success"] is False

    def test_learn_skill_prerequisite_missing(self, progression, sample_player):
        sample_player.level = 5
        sample_player.skill_points = 2
        result = progression.learn_skill(sample_player, "tourbillon")
        assert result["success"] is False
        assert "Prérequis manquant: Charge" in result["message"]

    def test_get_available_skills(self, progression, sample_player):
        sample_player.level = 5  # Niveau suffisant pour "tourbillon"
        sample_player.skill_points = 2
        sample_player.learned_skills = ["charge"]  # Prérequis de "tourbillon" satisfait
        available = progression.get_available_skills(sample_player)
        assert len(available) > 0
        # "tourbillon" devrait être disponible (level 5, prereq charge OK, cost 2)
        assert any(skill["id"] == "tourbillon" for skill in available)
        assert available[0]["can_afford"] is True

    def test_reset_skills(self, progression, sample_player):
        sample_player.skill_points = 0
        sample_player.learned_skills = ["charge"]
        sample_player.gold = 200
        result = progression.reset_skills(sample_player)
        assert result["success"] is True
        assert len(sample_player.learned_skills) == 0
        assert sample_player.skill_points == 1  # Refunded

    def test_racial_bonuses(self, sample_player):
        # Copy player to avoid modifying fixture
        import copy

        player_copy = copy.deepcopy(sample_player)
        player_copy.race = Race.NAIN
        apply_racial_bonuses(player_copy)
        assert player_copy.strength == 12  # +2
        assert player_copy.constitution == 12  # +2
        assert player_copy.max_hp == 120  # +20

    def test_class_bonuses(self, sample_player):
        import copy

        player_copy = copy.deepcopy(sample_player)
        player_copy.class_type = CharacterClass.MAGE
        apply_class_bonuses(player_copy)
        assert player_copy.max_mana == 80  # +30
        assert player_copy.intelligence == 14  # +4

    def test_skill_trees_structure(self):
        """Test skill trees structure"""
        guerrier_skills = SKILL_TREES[CharacterClass.GUERRIER]
        assert "charge" in guerrier_skills
        assert guerrier_skills["charge"]["level_required"] == 2
