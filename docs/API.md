# API Reference

## WebSocket Endpoints

Tous les endpoints WebSocket utilisent JSON pour les messages.

### Narrative Principal

**Endpoint:** `ws://localhost:8000/ws/{player_id}`

Connexion principale pour le jeu narratif.

#### Messages reçus (client → serveur)

```
"Le joueur fait son choix en texte libre"
```

#### Messages envoyés (serveur → client)

```json
{
  "narrative": "Description narrative de la scène...",
  "choices": ["Choix 1", "Choix 2", "Choix 3"],
  "location": "la Comté",
  "animation_trigger": "none",
  "sfx": "ambient"
}
```

---

### Combat

**Endpoint:** `ws://localhost:8000/ws/combat/{player_id}`

Gestion des combats en temps réel.

#### Actions disponibles

**Démarrer combat:**

```json
{
  "action": "start_combat",
  "enemies": ["orc_01", "gobelin_01"]
}
```

**Attaquer:**

```json
{
  "action": "attack",
  "target_index": 0
}
```

**Lancer un sort:**

```json
{
  "action": "cast_spell",
  "spell_id": "fireball",
  "target_index": 0
}
```

**Utiliser objet:**

```json
{
  "action": "use_item",
  "item_id": "health_potion"
}
```

**Défendre:**

```json
{
  "action": "defend"
}
```

#### Réponses

**Début combat:**

```json
{
  "type": "combat_start",
  "combat_id": "uuid",
  "intro": "Un orc surgit des buissons!",
  "enemies": [
    {
      "enemy_id": "orc_01",
      "name": "Orc des plaines",
      "hp": 80,
      "max_hp": 80
    }
  ],
  "player": {
    "hp": 100,
    "max_hp": 100,
    "mana": 50,
    "max_mana": 50
  }
}
```

**Résultat tour:**

```json
{
  "type": "combat_result",
  "narrative": "Vous frappez l'orc!",
  "player_damage": 0,
  "enemy_damages": [15],
  "animations": ["slash"],
  "player": { "hp": 100, "max_hp": 100 },
  "enemies": [{ "hp": 65, "max_hp": 80, "alive": true }]
}
```

**Fin combat:**

```json
{
  "type": "combat_end",
  "victory": true,
  "narrative": "L'orc s'effondre!",
  "loot": [{ "item_id": "gold_pouch", "name": "Bourse d'or" }],
  "gold_gained": 25,
  "xp_gained": 100
}
```

---

### Inventaire

**Endpoint:** `ws://localhost:8000/ws/inventory/{player_id}`

Gestion de l'inventaire et équipement.

#### Actions

**Récupérer inventaire:**

```json
{ "action": "get_inventory" }
```

**Équiper objet:**

```json
{
  "action": "equip",
  "item_id": "sword_01",
  "slot": "weapon_main"
}
```

**Déséquiper:**

```json
{
  "action": "unequip",
  "slot": "weapon_main"
}
```

**Utiliser consommable:**

```json
{
  "action": "use_item",
  "item_id": "health_potion"
}
```

**Jeter objet:**

```json
{
  "action": "drop",
  "item_id": "rusty_sword"
}
```

#### Réponses

**Inventaire complet:**

```json
{
  "type": "inventory_full",
  "inventory": [
    {
      "item_id": "sword_01",
      "name": "Épée longue",
      "item_type": "weapon",
      "rarity": "common",
      "value": 50
    }
  ],
  "equipped": {
    "weapon_main": { "item_id": "dagger_01", "name": "Dague" }
  },
  "stats": { "attack": 15, "defense": 10 },
  "gold": 100
}
```

---

### Quêtes

**Endpoint:** `ws://localhost:8000/ws/quests/{player_id}`

Gestion des quêtes.

#### Actions

**Liste quêtes:**

```json
{ "action": "get_quests" }
```

**Accepter quête:**

```json
{
  "action": "accept_quest",
  "quest_id": "q1"
}
```

**Abandonner quête:**

```json
{
  "action": "abandon_quest",
  "quest_id": "q1"
}
```

**Générer quête dynamique:**

```json
{ "action": "generate_quest" }
```

#### Réponses

**Liste:**

```json
{
  "type": "quests_list",
  "active": [
    {
      "quest_id": "q1",
      "title": "Le trésor perdu",
      "description": "Retrouvez le coffre caché...",
      "level": 3,
      "xp_reward": 200,
      "gold_reward": 50,
      "objectives": [
        {
          "description": "Trouver la carte",
          "current": 0,
          "target": 1,
          "completed": false
        }
      ]
    }
  ],
  "completed": []
}
```

---

### Personnage

**Endpoint:** `ws://localhost:8000/ws/character/{player_id}`

Progression du personnage.

#### Actions

**Info personnage:**

```json
{ "action": "get_character" }
```

**Allouer point stat:**

```json
{
  "action": "allocate_stat",
  "stat": "strength"
}
```

**Apprendre compétence:**

```json
{
  "action": "learn_skill",
  "skill_id": "charge"
}
```

**Reset compétences:**

```json
{ "action": "reset_skills" }
```

#### Réponses

**Info:**

```json
{
  "type": "character_info",
  "player": {
    "name": "Aventurier",
    "race": "humain",
    "class_type": "guerrier",
    "level": 5,
    "xp": 1250,
    "hp": 120,
    "max_hp": 120,
    "strength": 14,
    "intelligence": 10,
    "agility": 12,
    "skill_points": 2
  },
  "available_skills": [
    {
      "skill_id": "charge",
      "name": "Charge",
      "description": "Foncez sur l'ennemi",
      "level_required": 5,
      "cost": 1
    }
  ],
  "learned_skills": []
}
```

---

## REST Endpoints

### Reset Game

**POST** `/reset/{player_id}`

Réinitialise la partie d'un joueur.

**Réponse:**

```json
{ "status": "Partie réinitialisée" }
```

---

## Codes d'erreur WebSocket

| Code | Raison                              |
| ---- | ----------------------------------- |
| 503  | Serveur plein (max_players atteint) |
| 1000 | Déconnexion normale                 |
| 1001 | Client parti                        |

## Types d'erreur JSON

```json
{
  "type": "error",
  "message": "Description de l'erreur"
}
```

Messages courants:

- `"Aucun combat actif"` - Action combat sans combat démarré
- `"Statistique invalide"` - Stat inexistante
- `"Points insuffisants"` - Pas assez de skill points
- `"Or insuffisant"` - Pas assez d'or pour reset
