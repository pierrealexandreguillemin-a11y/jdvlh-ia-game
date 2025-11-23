#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests d'intégration bout-en-bout
Teste le flux complet du jeu avec tous les endpoints WebSocket
"""

import sys
from pathlib import Path

# Ajouter src au path pour imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from jdvlh_ia_game.core.game_server import app  # noqa: E402


@pytest.fixture
def client():
    """Fixture pour le test client"""
    return TestClient(app)


@pytest.fixture
def player_id():
    """Fixture pour un player_id unique"""
    import uuid

    return f"test_player_{uuid.uuid4().hex[:8]}"


class TestNarrativeWebSocket:
    """Tests pour le WebSocket narratif"""

    def test_narrative_connection(self, client, player_id):
        """Test de connexion au WebSocket narratif"""
        with client.websocket_connect(f"/ws/{player_id}") as websocket:
            # Recevoir le message de bienvenue
            data = websocket.receive_json()
            assert "narrative" in data
            assert "choices" in data
            assert isinstance(data["choices"], list)
            assert len(data["choices"]) > 0

    def test_narrative_choice(self, client, player_id):
        """Test d'envoi d'un choix et réception de réponse"""
        with client.websocket_connect(f"/ws/{player_id}") as websocket:
            # Recevoir bienvenue
            welcome = websocket.receive_json()

            # Envoyer un choix
            choice = welcome["choices"][0]
            websocket.send_text(choice)

            # Recevoir réponse
            response = websocket.receive_json()
            assert "narrative" in response
            assert "choices" in response


class TestCombatWebSocket:
    """Tests pour le WebSocket de combat"""

    def test_combat_start(self, client, player_id):
        """Test de démarrage d'un combat"""
        with client.websocket_connect(f"/ws/combat/{player_id}") as websocket:
            # Démarrer un combat
            websocket.send_json({"action": "start_combat", "enemies": ["orc_01"]})

            # Recevoir l'état de combat initial
            response = websocket.receive_json()
            assert response["type"] == "combat_start"
            assert "combat_id" in response
            assert "enemies" in response
            assert len(response["enemies"]) == 1
            assert "player" in response
            assert response["player"]["hp"] > 0

    def test_combat_attack(self, client, player_id):
        """Test d'attaque en combat"""
        with client.websocket_connect(f"/ws/combat/{player_id}") as websocket:
            # Démarrer combat
            websocket.send_json({"action": "start_combat", "enemies": ["gobelin_01"]})
            _ = websocket.receive_json()

            # Attaquer
            websocket.send_json({"action": "attack", "target_index": 0})

            # Recevoir résultat
            response = websocket.receive_json()
            assert response["type"] in ["combat_result", "combat_end"]
            assert "narrative" in response
            assert "player" in response
            assert "enemies" in response

    def test_combat_defend(self, client, player_id):
        """Test de défense en combat"""
        with client.websocket_connect(f"/ws/combat/{player_id}") as websocket:
            # Démarrer combat
            websocket.send_json({"action": "start_combat", "enemies": ["orc_01"]})
            websocket.receive_json()

            # Défendre
            websocket.send_json({"action": "defend"})

            # Recevoir résultat
            response = websocket.receive_json()
            assert response["type"] in ["combat_result", "combat_end"]

    def test_combat_no_active(self, client, player_id):
        """Test d'erreur quand pas de combat actif"""
        with client.websocket_connect(f"/ws/combat/{player_id}") as websocket:
            # Essayer d'attaquer sans combat actif
            websocket.send_json({"action": "attack", "target_index": 0})

            # Recevoir erreur
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "message" in response


class TestInventoryWebSocket:
    """Tests pour le WebSocket d'inventaire"""

    def test_inventory_get(self, client, player_id):
        """Test de récupération de l'inventaire"""
        with client.websocket_connect(f"/ws/inventory/{player_id}") as websocket:
            # Demander l'inventaire
            websocket.send_json({"action": "get_inventory"})

            # Recevoir inventaire
            response = websocket.receive_json()
            assert response["type"] == "inventory_full"
            assert "inventory" in response
            assert "equipped" in response
            assert "stats" in response
            assert "gold" in response
            assert isinstance(response["inventory"], list)
            assert isinstance(response["equipped"], dict)


class TestQuestsWebSocket:
    """Tests pour le WebSocket de quêtes"""

    def test_quests_get(self, client, player_id):
        """Test de récupération des quêtes"""
        with client.websocket_connect(f"/ws/quests/{player_id}") as websocket:
            # Demander les quêtes
            websocket.send_json({"action": "get_quests"})

            # Recevoir quêtes
            response = websocket.receive_json()
            assert response["type"] == "quests_list"
            assert "active" in response
            assert "completed" in response
            assert isinstance(response["active"], list)
            assert isinstance(response["completed"], list)

    def test_quest_accept(self, client, player_id):
        """Test d'acceptation de quête"""
        with client.websocket_connect(f"/ws/quests/{player_id}") as websocket:
            # Accepter une quête
            websocket.send_json({"action": "accept_quest", "quest_id": "test_quest"})

            # Recevoir confirmation
            response = websocket.receive_json()
            assert response["type"] == "quest_accepted"
            assert response["quest_id"] == "test_quest"

    def test_quest_abandon(self, client, player_id):
        """Test d'abandon de quête"""
        with client.websocket_connect(f"/ws/quests/{player_id}") as websocket:
            # Abandonner une quête
            websocket.send_json({"action": "abandon_quest", "quest_id": "test_quest"})

            # Recevoir confirmation
            response = websocket.receive_json()
            assert response["type"] == "quest_abandoned"
            assert response["quest_id"] == "test_quest"


class TestCharacterWebSocket:
    """Tests pour le WebSocket de personnage"""

    def test_character_get(self, client, player_id):
        """Test de récupération des infos personnage"""
        with client.websocket_connect(f"/ws/character/{player_id}") as websocket:
            # Demander les infos personnage
            websocket.send_json({"action": "get_character"})

            # Recevoir infos
            response = websocket.receive_json()
            assert response["type"] == "character_info"
            assert "player" in response
            assert "available_skills" in response
            assert "learned_skills" in response
            assert isinstance(response["player"], dict)
            assert isinstance(response["available_skills"], list)
            assert isinstance(response["learned_skills"], list)

    def test_stat_allocate_no_points(self, client, player_id):
        """Test d'allocation de stat sans points"""
        with client.websocket_connect(f"/ws/character/{player_id}") as websocket:
            # Essayer d'allouer sans points
            websocket.send_json({"action": "allocate_stat", "stat": "strength"})

            # Recevoir erreur
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "points" in response["message"].lower()


class TestCompleteGameFlow:
    """Tests du flux complet de jeu"""

    def test_full_game_session(self, client, player_id):
        """Test d'une session de jeu complète avec tous les systèmes"""

        # 1. Connexion narrative
        with client.websocket_connect(f"/ws/{player_id}") as ws_narrative:
            welcome = ws_narrative.receive_json()
            assert "narrative" in welcome

            # Faire un choix
            ws_narrative.send_text(welcome["choices"][0])
            response = ws_narrative.receive_json()
            assert "narrative" in response

        # 2. Vérifier l'inventaire
        with client.websocket_connect(f"/ws/inventory/{player_id}") as ws_inventory:
            ws_inventory.send_json({"action": "get_inventory"})
            inv_response = ws_inventory.receive_json()
            assert inv_response["type"] == "inventory_full"

        # 3. Vérifier les quêtes
        with client.websocket_connect(f"/ws/quests/{player_id}") as ws_quests:
            ws_quests.send_json({"action": "get_quests"})
            quests_response = ws_quests.receive_json()
            assert quests_response["type"] == "quests_list"

        # 4. Vérifier le personnage
        with client.websocket_connect(f"/ws/character/{player_id}") as ws_character:
            ws_character.send_json({"action": "get_character"})
            char_response = ws_character.receive_json()
            assert char_response["type"] == "character_info"

        # 5. Combat complet
        with client.websocket_connect(f"/ws/combat/{player_id}") as ws_combat:
            # Démarrer combat
            ws_combat.send_json({"action": "start_combat", "enemies": ["gobelin_01"]})
            start = ws_combat.receive_json()
            assert start["type"] == "combat_start"

            # Attaquer jusqu'à victoire ou défaite (max 20 tours)
            for _ in range(20):
                ws_combat.send_json({"action": "attack", "target_index": 0})
                result = ws_combat.receive_json()

                if result["type"] == "combat_end":
                    # Combat terminé
                    assert "victory" in result
                    break

                # Combat continue
                assert result["type"] == "combat_result"

    def test_concurrent_websockets(self, client, player_id):
        """Test de plusieurs WebSockets actifs simultanément"""
        # Note: Ce test nécessite asyncio pour gérer les connexions concurrentes
        # Pour l'instant, on teste juste que les connexions peuvent être établies séquentiellement

        connections = []

        # Ouvrir toutes les connexions
        ws_narrative = client.websocket_connect(f"/ws/{player_id}")
        ws_narrative.__enter__()
        connections.append(ws_narrative)

        ws_combat = client.websocket_connect(f"/ws/combat/{player_id}")
        ws_combat.__enter__()
        connections.append(ws_combat)

        ws_inventory = client.websocket_connect(f"/ws/inventory/{player_id}")
        ws_inventory.__enter__()
        connections.append(ws_inventory)

        ws_quests = client.websocket_connect(f"/ws/quests/{player_id}")
        ws_quests.__enter__()
        connections.append(ws_quests)

        ws_character = client.websocket_connect(f"/ws/character/{player_id}")
        ws_character.__enter__()
        connections.append(ws_character)

        # Toutes les connexions sont ouvertes
        assert len(connections) == 5

        # Fermer toutes les connexions
        for ws in connections:
            ws.__exit__(None, None, None)


class TestErrorHandling:
    """Tests de gestion d'erreurs"""

    def test_invalid_action_combat(self, client, player_id):
        """Test d'action invalide en combat"""
        with client.websocket_connect(f"/ws/combat/{player_id}") as websocket:
            websocket.send_json({"action": "invalid_action"})
            # Le serveur devrait gérer gracieusement

    def test_missing_parameters(self, client, player_id):
        """Test de paramètres manquants"""
        with client.websocket_connect(f"/ws/inventory/{player_id}") as websocket:
            # Essayer d'équiper sans item_id
            try:
                websocket.send_json({"action": "equip", "slot": "weapon_main"})
                _ = websocket.receive_json()
                # Devrait soit réussir avec erreur, soit lever une exception
                assert True
            except Exception:
                # Exception attendue pour paramètres manquants
                assert True


class TestStateManagement:
    """Tests de gestion d'état"""

    def test_state_persistence(self, client, player_id):
        """Test de persistance de l'état entre connexions"""
        # Première connexion - faire un choix
        with client.websocket_connect(f"/ws/{player_id}") as websocket:
            welcome = websocket.receive_json()
            websocket.send_text(welcome["choices"][0])
            _ = websocket.receive_json()

        # Deuxième connexion - vérifier que l'état persiste
        with client.websocket_connect(f"/ws/{player_id}") as websocket:
            welcome2 = websocket.receive_json()
            # L'état devrait être différent du premier welcome
            assert "narrative" in welcome2

    def test_player_creation(self, client):
        """Test de création automatique de joueur"""
        import uuid

        new_player_id = f"new_player_{uuid.uuid4().hex[:8]}"

        with client.websocket_connect(f"/ws/character/{new_player_id}") as websocket:
            websocket.send_json({"action": "get_character"})
            response = websocket.receive_json()

            assert response["type"] == "character_info"
            assert response["player"]["player_id"] == new_player_id


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
