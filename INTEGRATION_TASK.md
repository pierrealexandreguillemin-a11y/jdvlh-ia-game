# 🎯 TÂCHE : Option C - Intégration Complète WebSocket + HTML

## 📋 CONTEXTE

**Projet** : JDVLH IA Game - JDR Narratif IA + Godot
**État actuel** :
- ✅ Backend complet (5 services JDR : combat, inventory, quests, character_progression, narrative)
- ✅ 27 tests unitaires (100% pass)
- ✅ Performance optimisée (llama3.2, 150 tokens)
- ✅ 1 endpoint WebSocket narratif fonctionnel : `/ws/{player_id}`
- ✅ Client HTML basique (texte narratif + choix)

**Objectif** : Créer une intégration complète avec UI interactive et endpoints WebSocket pour TOUS les systèmes de jeu.

---

## 🎯 LIVRABLES ATTENDUS

### 1. Client HTML Complet (`game_client.html`)

**Sections UI à créer** :

#### A. Header avec Stats Joueur (HUD)
```html
<div id="player-hud">
    <div class="player-info">
        <h3 id="player-name">Aragorn</h3>
        <span id="player-level">Niveau 5</span>
        <span id="player-class">Guerrier</span>
    </div>

    <!-- Barres de stats -->
    <div class="stat-bars">
        <div class="stat-bar hp">
            <label>HP:</label>
            <div class="bar"><div class="fill"></div></div>
            <span class="value">75/100</span>
        </div>
        <div class="stat-bar mana">
            <label>Mana:</label>
            <div class="bar"><div class="fill"></div></div>
            <span class="value">25/50</span>
        </div>
        <div class="stat-bar stamina">
            <label>Stamina:</label>
            <div class="bar"><div class="fill"></div></div>
            <span class="value">80/100</span>
        </div>
    </div>

    <!-- Stats secondaires -->
    <div class="secondary-stats">
        <span>💰 Or: <strong id="gold">250</strong></span>
        <span>⭐ XP: <strong id="xp">450/600</strong></span>
    </div>
</div>
```

#### B. Zone Narrative (existant à améliorer)
```html
<div id="narrative-panel">
    <div id="location-banner">📍 <span id="current-location">la Comté</span></div>
    <div id="narrative-text">
        <!-- Texte généré par l'IA -->
    </div>
    <div id="narrative-choices">
        <!-- Boutons de choix -->
    </div>
</div>
```

#### C. Panneau Combat (conditionnel)
```html
<div id="combat-panel" style="display:none">
    <h3>⚔️ Combat en cours</h3>

    <!-- Liste des ennemis -->
    <div id="enemies-list">
        <div class="enemy-card">
            <img src="orc.png" alt="Orc">
            <div class="enemy-info">
                <h4>Orc des plaines</h4>
                <div class="hp-bar">
                    <div class="fill" style="width: 60%"></div>
                </div>
                <span class="hp-text">48/80 HP</span>
            </div>
        </div>
    </div>

    <!-- Actions de combat -->
    <div id="combat-actions">
        <button class="action-btn attack" onclick="combatAction('attack', 0)">
            ⚔️ Attaquer
        </button>
        <button class="action-btn spell" onclick="showSpells()">
            ✨ Sort
        </button>
        <button class="action-btn item" onclick="showCombatItems()">
            🧪 Objet
        </button>
        <button class="action-btn defend" onclick="combatAction('defend')">
            🛡️ Défendre
        </button>
    </div>

    <!-- Sélecteur de sorts -->
    <div id="spell-selector" style="display:none">
        <!-- Liste des sorts disponibles -->
    </div>
</div>
```

#### D. Inventaire + Équipement
```html
<div id="inventory-panel">
    <h3>📦 Inventaire</h3>

    <!-- Équipement (slots) -->
    <div id="equipment-slots">
        <div class="equipment-grid">
            <div class="slot head" data-slot="head">
                <span class="slot-label">Casque</span>
                <div class="item-slot empty"></div>
            </div>
            <div class="slot chest" data-slot="chest">
                <span class="slot-label">Plastron</span>
                <div class="item-slot empty"></div>
            </div>
            <div class="slot weapon" data-slot="weapon_main">
                <span class="slot-label">Arme</span>
                <div class="item-slot">
                    <img src="sword.png" title="Épée de Fer (+15 dmg)">
                </div>
            </div>
            <!-- ... autres slots ... -->
        </div>
    </div>

    <!-- Sac d'items -->
    <div id="inventory-items">
        <div class="item-grid">
            <div class="item" data-item-id="health_potion" draggable="true">
                <img src="potion_red.png">
                <span class="quantity">x3</span>
                <div class="tooltip">
                    <strong>Potion de soin</strong><br>
                    Restaure 50 HP
                </div>
            </div>
            <!-- ... autres items ... -->
        </div>
    </div>

    <!-- Infos item sélectionné -->
    <div id="item-details">
        <h4 id="item-name">-</h4>
        <p id="item-description">-</p>
        <div id="item-actions">
            <button onclick="useItem()">Utiliser</button>
            <button onclick="equipItem()">Équiper</button>
            <button onclick="dropItem()">Jeter</button>
        </div>
    </div>
</div>
```

#### E. Journal de Quêtes
```html
<div id="quests-panel">
    <h3>📜 Journal de Quêtes</h3>

    <div class="quests-tabs">
        <button class="tab active" onclick="showQuests('active')">En cours</button>
        <button class="tab" onclick="showQuests('completed')">Terminées</button>
    </div>

    <div id="active-quests">
        <div class="quest-card main-quest">
            <div class="quest-header">
                <h4>🌟 Détruire l'Anneau Unique</h4>
                <span class="quest-level">Niveau 1</span>
            </div>
            <p class="quest-description">
                Apportez l'Anneau au Mont Destin...
            </p>
            <div class="quest-objectives">
                <div class="objective completed">
                    ✓ Quitter la Comté
                </div>
                <div class="objective in-progress">
                    ⏳ Rejoindre Gandalf à Fondcombe (1/1)
                </div>
                <div class="objective locked">
                    🔒 Atteindre le Mont Destin (0/1)
                </div>
            </div>
            <div class="quest-rewards">
                <span>🏆 1000 XP</span>
                <span>⭐ Gloire éternelle</span>
            </div>
        </div>
    </div>
</div>
```

#### F. Panneau Progression
```html
<div id="character-panel">
    <h3>📊 Personnage</h3>

    <!-- Attributs -->
    <div class="attributes">
        <div class="attribute">
            <span class="attr-name">💪 Force:</span>
            <span class="attr-value">15</span>
            <button class="attr-increase" onclick="increaseAttr('strength')">+</button>
        </div>
        <div class="attribute">
            <span class="attr-name">🧠 Intelligence:</span>
            <span class="attr-value">10</span>
            <button class="attr-increase" onclick="increaseAttr('intelligence')">+</button>
        </div>
        <!-- ... autres attributs ... -->
    </div>

    <div class="skill-points">
        Points disponibles: <strong id="skill-points">3</strong>
    </div>

    <!-- Arbre de compétences -->
    <div id="skill-tree">
        <h4>🌳 Compétences - Guerrier</h4>
        <div class="skills-grid">
            <div class="skill learned" data-skill="charge">
                <img src="skill_charge.png">
                <span>Charge</span>
                <div class="skill-tooltip">
                    <strong>Charge</strong><br>
                    Foncez vers l'ennemi<br>
                    +50% dégâts<br>
                    <em>Coût: 1 point</em>
                </div>
            </div>
            <div class="skill available" data-skill="tourbillon">
                <img src="skill_whirlwind.png">
                <span>Tourbillon</span>
                <div class="skill-tooltip">
                    <strong>Tourbillon d'acier</strong><br>
                    Attaque tous les ennemis<br>
                    <em>Niveau 5 requis</em><br>
                    <em>Prérequis: Charge</em><br>
                    <em>Coût: 2 points</em>
                </div>
            </div>
            <div class="skill locked" data-skill="rage">
                <img src="skill_rage.png" class="grayscale">
                <span>Rage</span>
            </div>
        </div>
    </div>
</div>
```

#### G. CSS Moderne (glassmorphism)
```css
/* Variables globales */
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --glass-bg: rgba(255, 255, 255, 0.1);
    --glass-border: rgba(255, 255, 255, 0.2);
}

/* Glassmorphism cards */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Barres de stats animées */
.stat-bar .fill {
    transition: width 0.5s ease;
    background: linear-gradient(90deg, var(--success), #34d399);
}

/* Drag & drop inventaire */
.item[draggable="true"] {
    cursor: grab;
}
.item[draggable="true"]:active {
    cursor: grabbing;
}
```

---

### 2. Backend - Endpoints WebSocket

**Fichier** : `src/jdvlh_ia_game/core/game_server.py`

#### A. Endpoint Combat
```python
@app.websocket("/ws/combat/{player_id}")
async def combat_websocket(
    websocket: WebSocket,
    player_id: str,
    combat_engine: CombatEngine = Depends(get_combat_engine),
    state_manager: StateManager = Depends(get_state_manager)
):
    """
    WebSocket pour gérer les combats en temps réel

    Messages REÇUS (du client) :
    {
        "action": "start_combat",
        "enemies": ["orc_01", "gobelin_01"]
    }
    {
        "action": "attack",
        "target_index": 0
    }
    {
        "action": "cast_spell",
        "spell_id": "fireball",
        "target_index": 0
    }
    {
        "action": "use_item",
        "item_id": "health_potion"
    }
    {
        "action": "defend"
    }

    Messages ENVOYÉS (au client) :
    {
        "type": "combat_start",
        "combat_id": "combat_123",
        "intro": "Un orc surgit !",
        "enemies": [
            {
                "enemy_id": "e1",
                "name": "Orc",
                "hp": 80,
                "max_hp": 80,
                "level": 1
            }
        ],
        "player": {
            "hp": 100,
            "max_hp": 100,
            "mana": 50,
            "max_mana": 50
        }
    }
    {
        "type": "combat_result",
        "narrative": "Vous frappez l'orc !",
        "player_damage": 0,
        "enemy_damages": [25],
        "animations": ["attack"],
        "player": { "hp": 100 },
        "enemies": [{ "hp": 55 }]
    }
    {
        "type": "combat_end",
        "victory": true,
        "narrative": "Victoire !",
        "loot": [...],
        "gold_gained": 50,
        "xp_gained": 100
    }
    """

    await websocket.accept()
    active_combat = None

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")

            if action == "start_combat":
                # Créer un nouveau combat
                player = load_player(player_id, state_manager)
                enemies = create_enemies(message["enemies"])

                combat_state = await combat_engine.start_combat(
                    player, enemies, player.current_location
                )
                active_combat = combat_state

                await websocket.send_json({
                    "type": "combat_start",
                    "combat_id": combat_state.combat_id,
                    "intro": combat_state.intro_text,
                    "enemies": [e.to_dict() for e in enemies],
                    "player": {
                        "hp": player.hp,
                        "max_hp": player.max_hp,
                        "mana": player.mana,
                        "max_mana": player.max_mana
                    }
                })

            elif action in ["attack", "cast_spell", "use_item", "defend"]:
                if not active_combat:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Aucun combat actif"
                    })
                    continue

                # Créer l'action de combat
                combat_action = CombatAction(
                    action_type=action,
                    target_index=message.get("target_index", 0),
                    spell_id=message.get("spell_id"),
                    item_id=message.get("item_id")
                )

                # Exécuter le tour de combat
                result = await combat_engine.execute_turn(
                    active_combat, combat_action
                )

                # Envoyer le résultat
                response = {
                    "type": "combat_result",
                    "narrative": result.narrative,
                    "player_damage": result.player_damage,
                    "enemy_damages": result.enemy_damages,
                    "animations": result.animations,
                    "player": {
                        "hp": active_combat.player.hp,
                        "max_hp": active_combat.player.max_hp
                    },
                    "enemies": [
                        {"hp": e.hp, "max_hp": e.max_hp, "alive": e.is_alive()}
                        for e in active_combat.enemies
                    ]
                }

                if result.is_victory or result.is_defeat:
                    response["type"] = "combat_end"
                    response["victory"] = result.is_victory
                    response["loot"] = [item.to_dict() for item in result.loot]
                    response["gold_gained"] = result.gold_gained
                    response["xp_gained"] = result.xp_gained
                    active_combat = None

                await websocket.send_json(response)

    except WebSocketDisconnect:
        print(f"Combat WebSocket disconnected: {player_id}")
```

#### B. Endpoint Inventaire
```python
@app.websocket("/ws/inventory/{player_id}")
async def inventory_websocket(
    websocket: WebSocket,
    player_id: str,
    inventory_manager: InventoryManager = Depends(get_inventory_manager),
    state_manager: StateManager = Depends(get_state_manager)
):
    """
    Messages REÇUS :
    {
        "action": "get_inventory"
    }
    {
        "action": "equip",
        "item_id": "sword_01",
        "slot": "weapon_main"
    }
    {
        "action": "unequip",
        "slot": "weapon_main"
    }
    {
        "action": "use_item",
        "item_id": "health_potion"
    }
    {
        "action": "drop",
        "item_id": "rusty_sword"
    }

    Messages ENVOYÉS :
    {
        "type": "inventory_full",
        "inventory": [...],
        "equipped": {...},
        "stats": {...}
    }
    {
        "type": "item_action_result",
        "success": true,
        "message": "Épée équipée !",
        "inventory": [...],
        "equipped": {...}
    }
    """

    await websocket.accept()
    player = load_player(player_id, state_manager)

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")

            if action == "get_inventory":
                await websocket.send_json({
                    "type": "inventory_full",
                    "inventory": [item.to_dict() for item in player.inventory],
                    "equipped": {
                        slot: item.to_dict()
                        for slot, item in player.equipped.items()
                    },
                    "stats": inventory_manager.get_total_stats(player),
                    "gold": player.gold
                })

            elif action == "equip":
                result = inventory_manager.equip_item(
                    player,
                    message["item_id"],
                    message["slot"]
                )
                await websocket.send_json({
                    "type": "item_action_result",
                    **result,
                    "inventory": [item.to_dict() for item in player.inventory],
                    "equipped": {
                        slot: item.to_dict()
                        for slot, item in player.equipped.items()
                    }
                })
                save_player(player, state_manager)

            # ... autres actions similaires ...

    except WebSocketDisconnect:
        print(f"Inventory WebSocket disconnected: {player_id}")
```

#### C. Endpoint Quêtes
```python
@app.websocket("/ws/quests/{player_id}")
async def quests_websocket(
    websocket: WebSocket,
    player_id: str,
    quest_manager: QuestManager = Depends(get_quest_manager),
    state_manager: StateManager = Depends(get_state_manager)
):
    """
    Messages REÇUS :
    {
        "action": "get_quests"
    }
    {
        "action": "accept_quest",
        "quest_id": "q1"
    }
    {
        "action": "abandon_quest",
        "quest_id": "q1"
    }

    Messages ENVOYÉS :
    {
        "type": "quests_list",
        "active": [...],
        "completed": [...]
    }
    {
        "type": "quest_accepted",
        "quest": {...}
    }
    {
        "type": "quest_progress",
        "quest_id": "q1",
        "objective_id": "obj1",
        "progress": "2/3"
    }
    {
        "type": "quest_completed",
        "quest": {...},
        "rewards": {
            "xp": 200,
            "gold": 100,
            "items": [...]
        }
    }
    """

    # Implementation similaire aux autres endpoints
    pass
```

#### D. Endpoint Personnage
```python
@app.websocket("/ws/character/{player_id}")
async def character_websocket(
    websocket: WebSocket,
    player_id: str,
    character_progression: CharacterProgression = Depends(get_character_progression),
    state_manager: StateManager = Depends(get_state_manager)
):
    """
    Messages REÇUS :
    {
        "action": "get_character"
    }
    {
        "action": "allocate_stat",
        "stat": "strength"
    }
    {
        "action": "learn_skill",
        "skill_id": "charge"
    }
    {
        "action": "reset_skills"
    }

    Messages ENVOYÉS :
    {
        "type": "character_info",
        "player": {...},
        "available_skills": [...],
        "learned_skills": [...]
    }
    {
        "type": "stat_allocated",
        "stat": "strength",
        "new_value": 16,
        "skill_points_remaining": 2
    }
    {
        "type": "level_up",
        "level": 6,
        "skill_points": 3,
        "bonuses": {...}
    }
    {
        "type": "skill_learned",
        "skill": {...}
    }
    """

    # Implementation similaire
    pass
```

---

### 3. JavaScript Client (WebSocket Manager)

**Fichier** : `game_client.html` (section script)

```javascript
class GameWebSocketManager {
    constructor(playerId) {
        this.playerId = playerId;
        this.connections = {
            narrative: null,
            combat: null,
            inventory: null,
            quests: null,
            character: null
        };
    }

    // Connexion narrative (existant)
    connectNarrative() {
        const ws = new WebSocket(`ws://localhost:8000/ws/${this.playerId}`);

        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleNarrativeMessage(data);
        };

        this.connections.narrative = ws;
    }

    // Connexion combat
    connectCombat() {
        const ws = new WebSocket(`ws://localhost:8000/ws/combat/${this.playerId}`);

        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleCombatMessage(data);
        };

        this.connections.combat = ws;
    }

    // Connexion inventaire
    connectInventory() {
        const ws = new WebSocket(`ws://localhost:8000/ws/inventory/${this.playerId}`);

        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleInventoryMessage(data);
        };

        this.connections.inventory = ws;
    }

    // Handlers de messages
    handleCombatMessage(data) {
        switch(data.type) {
            case 'combat_start':
                showCombatUI();
                displayEnemies(data.enemies);
                updatePlayerStats(data.player);
                showNarrative(data.intro);
                break;

            case 'combat_result':
                showNarrative(data.narrative);
                animateDamage(data.enemy_damages, data.player_damage);
                updateCombatState(data);
                break;

            case 'combat_end':
                if (data.victory) {
                    showVictory(data);
                    displayLoot(data.loot);
                    updatePlayerXP(data.xp_gained);
                    updatePlayerGold(data.gold_gained);
                } else {
                    showDefeat(data);
                }
                hideCombatUI();
                break;
        }
    }

    handleInventoryMessage(data) {
        switch(data.type) {
            case 'inventory_full':
                displayInventory(data.inventory);
                displayEquipment(data.equipped);
                updateStatsDisplay(data.stats);
                break;

            case 'item_action_result':
                showNotification(data.message, data.success ? 'success' : 'error');
                if (data.success) {
                    displayInventory(data.inventory);
                    displayEquipment(data.equipped);
                }
                break;
        }
    }

    // Actions
    combatAction(action, targetIndex = 0, spellId = null, itemId = null) {
        this.connections.combat.send(JSON.stringify({
            action: action,
            target_index: targetIndex,
            spell_id: spellId,
            item_id: itemId
        }));
    }

    equipItem(itemId, slot) {
        this.connections.inventory.send(JSON.stringify({
            action: 'equip',
            item_id: itemId,
            slot: slot
        }));
    }

    learnSkill(skillId) {
        this.connections.character.send(JSON.stringify({
            action: 'learn_skill',
            skill_id: skillId
        }));
    }
}

// Initialisation
const wsManager = new GameWebSocketManager('player_' + Math.random().toString(36).substr(2, 9));
wsManager.connectNarrative();
wsManager.connectCombat();
wsManager.connectInventory();
wsManager.connectQuests();
wsManager.connectCharacter();
```

---

### 4. Fonctions UI Helper

```javascript
// UI Updates
function updatePlayerStats(stats) {
    document.getElementById('player-hp').style.width = `${(stats.hp / stats.max_hp) * 100}%`;
    document.getElementById('player-hp-text').textContent = `${stats.hp}/${stats.max_hp}`;
    document.getElementById('player-mana').style.width = `${(stats.mana / stats.max_mana) * 100}%`;
    // ...
}

function displayInventory(items) {
    const grid = document.getElementById('inventory-grid');
    grid.innerHTML = '';

    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        div.dataset.itemId = item.item_id;
        div.innerHTML = `
            <img src="assets/${item.icon_path}" alt="${item.name}">
            ${item.stackable ? `<span class="quantity">x${item.quantity}</span>` : ''}
        `;
        div.onclick = () => selectItem(item);
        grid.appendChild(div);
    });
}

function showCombatUI() {
    document.getElementById('combat-panel').style.display = 'block';
    document.getElementById('narrative-panel').classList.add('compact');
}

function animateDamage(enemyDamages, playerDamage) {
    enemyDamages.forEach((dmg, i) => {
        if (dmg > 0) {
            showDamageNumber(dmg, `enemy-${i}`);
        }
    });

    if (playerDamage > 0) {
        showDamageNumber(playerDamage, 'player-hud', true);
    }
}

function showDamageNumber(amount, targetId, isPlayerDamage = false) {
    const target = document.getElementById(targetId);
    const dmgSpan = document.createElement('span');
    dmgSpan.className = `damage-number ${isPlayerDamage ? 'player-damage' : 'enemy-damage'}`;
    dmgSpan.textContent = `-${amount}`;
    dmgSpan.style.position = 'absolute';
    dmgSpan.style.animation = 'floatUp 1s ease-out';
    target.appendChild(dmgSpan);

    setTimeout(() => dmgSpan.remove(), 1000);
}
```

---

## 🎯 CRITÈRES DE SUCCÈS

1. **UI Complète** ✓
   - HUD avec stats en temps réel
   - Inventaire drag & drop fonctionnel
   - Combat UI avec animations
   - Journal de quêtes avec progression
   - Arbre de compétences interactif

2. **WebSocket Endpoints** ✓
   - 5 endpoints fonctionnels
   - Messages JSON structurés
   - Gestion des erreurs
   - Reconnexion automatique

3. **Intégration** ✓
   - Tous les services backend connectés
   - Synchronisation état client/serveur
   - Sauvegarde automatique
   - Tests end-to-end

4. **UX** ✓
   - Animations fluides
   - Feedback visuel (notifications, animations)
   - Design moderne (glassmorphism)
   - Responsive (mobile-friendly)

---

## 📦 STRUCTURE FICHIERS FINALE

```
jdvlh-ia-game/
├── game_client.html          # Client complet (nouveau)
├── assets/                    # Assets UI (nouveau)
│   ├── icons/
│   ├── skills/
│   └── items/
├── src/jdvlh_ia_game/
│   ├── core/
│   │   └── game_server.py    # + 4 endpoints WebSocket
│   ├── services/             # Déjà fait ✅
│   │   ├── combat_engine.py
│   │   ├── inventory_manager.py
│   │   ├── quest_manager.py
│   │   ├── character_progression.py
│   │   └── narrative.py
│   └── models/               # Déjà fait ✅
│       └── game_entities.py
└── tests/
    └── test_integration.py   # Tests end-to-end (nouveau)
```

---

## ⚡ HINTS & TIPS

1. **Drag & Drop Inventaire** : Utiliser HTML5 Drag & Drop API
2. **Animations Combat** : CSS animations + setTimeout pour séquencer
3. **WebSocket Reconnexion** : Implémenter backoff exponentiel
4. **State Management** : Garder un cache local côté client pour éviter requêtes inutiles
5. **Notifications** : Toast library (ou custom CSS animations)
6. **Icons** : Utiliser emojis OU icons SVG gratuits (game-icons.net)

---

## 🚀 ORDRE D'EXÉCUTION RECOMMANDÉ

1. **Phase 1** : Backend endpoints (2-3h)
   - Créer les 4 nouveaux endpoints WebSocket
   - Tester avec Postman/insomnia

2. **Phase 2** : Client HTML structure (2h)
   - Créer la structure HTML complète
   - CSS glassmorphism de base

3. **Phase 3** : WebSocket Manager JS (2h)
   - Classe GameWebSocketManager
   - Handlers de messages

4. **Phase 4** : UI Interactions (3h)
   - Fonctions updateUI
   - Animations
   - Drag & drop

5. **Phase 5** : Tests & Polish (2h)
   - Tests d'intégration
   - Bug fixes
   - UX improvements

**TOTAL ESTIMÉ** : 11-12h (1.5 jours)

---

## 📝 NOTES IMPORTANTES

- **Performance** : Limiter les updates WebSocket (throttle si nécessaire)
- **Sécurité** : Valider TOUTES les actions côté serveur (ne jamais faire confiance au client)
- **UX Enfants** : Interface simple, feedback clair, pas trop de texte
- **Compatibilité** : Tester sur Chrome, Firefox, Edge
- **Mobile** : Design responsive (media queries)

---

**BON COURAGE ! 🚀**
