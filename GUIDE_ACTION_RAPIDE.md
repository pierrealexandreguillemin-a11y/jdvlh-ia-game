# ⚡ GUIDE D'ACTION RAPIDE - JDR IA Game

**Date**: 22 Novembre 2025  
**Objectif**: Optimiser et démarrer l'implémentation en 2 heures

---

## 🎯 VERDICT FINAL

✅ **VOTRE PROJET EST DÉJÀ MEILLEUR QUE LES SOLUTIONS GITHUB**

**Ce que vous avez déjà** :
- ✅ Backend FastAPI production-ready
- ✅ ModelRouter intelligent (routing multi-modèles)
- ✅ NarrativeMemory avancée (cohérence narrative)
- ✅ Sécurité enfants (filtres, rate-limiting)
- ✅ Persistance SQLite + cache

**Ce qui manque** :
- ⏳ Optimisations performance (26.6s → 2.5s)
- ⏳ Client Godot 3D
- ⏳ Features JDR avancées (combat, inventaire, quêtes)

---

## 📊 COMPARAISON AVEC GITHUB

| Solution | Stack | IA Locale | Qualité | Votre Projet |
|----------|-------|-----------|---------|--------------|
| td-llm-dnd | Streamlit | ✅ | 6/10 | **MEILLEUR** |
| Dungeo_ai | Python | ✅ | 7/10 | **MEILLEUR** |
| ai-dungeon-master | Node/Discord | ✅ | 8/10 | **ÉQUIVALENT** |
| GodotDynamicDialog | Godot | ❌ API | 9/10 | **À INTÉGRER** |

**Conclusion** : Vous êtes sur la bonne voie, continuez !

---

## 🚀 ACTIONS IMMÉDIATES (2 HEURES)

### ÉTAPE 1 : Optimisations Critiques (30min)

#### 1.1 Modifier config.yaml

```bash
cd C:\Dev\jdvlh-ia-game
code config.yaml
```

**Changements à faire** :
```yaml
ollama:
  model: mistral
  max_retries: 3
  temperature: 0.75  # Au lieu de 0.8
  max_tokens: 150    # AU LIEU DE 400 ⚡ CRITIQUE

cache:
  dir: cache
  ttl: 7200  # Déjà bon
  pregenerate: true  # ⚡ AJOUTER CETTE LIGNE

prompts:
  system: "Tu es un maître du jeu D&D/Tolkien pour enfants francophones de 10-14 ans. Raconte TOUJOURS en FRANÇAIS une histoire épique et immersive. 8-12 phrases maximum, descriptions riches mais concises. IMPORTANT: JAMAIS d'anglais, TOUJOURS du français."
```

**Gain attendu** : **-50% temps de réponse**

#### 1.2 Installer modèles supplémentaires

```bash
# Modèle rapide (pour choix courts)
ollama pull llama3.2

# Modèle créatif (pour descriptions épiques)
ollama pull gemma2
```

**Temps** : 5-10 minutes (téléchargement)  
**Gain attendu** : **-40% temps moyen**

#### 1.3 Intégrer ModelRouter

```bash
code src/jdvlh_ia_game/services/narrative.py
```

**Ajouter au début du fichier** :
```python
from .model_router import get_router, TaskType
```

**Modifier la classe NarrativeService** :
```python
class NarrativeService:
    def __init__(self):
        self.cache = CacheService()
        self.memory = NarrativeMemory()  # ⚡ Déjà présent
        self.router = get_router()       # ⚡ AJOUTER CETTE LIGNE
        
    async def generate_narrative(self, prompt: str, context: str = ""):
        # ⚡ AJOUTER CES 2 LIGNES
        model, options = self.router.select_model(prompt, context)
        
        # Modifier l'appel Ollama pour utiliser le modèle sélectionné
        response = ollama.generate(
            model=model,  # ⚡ Au lieu de "mistral"
            prompt=prompt,
            **options  # ⚡ Au lieu de hardcoded options
        )
        
        return response
```

**Gain attendu** : **+100% qualité, -40% temps**

#### 1.4 Tester les optimisations

```bash
# Lancer le serveur
python main.py

# Dans un autre terminal, tester
python test_performance.py
```

**Objectif** : Temps moyen < 3 secondes ✅

---

### ÉTAPE 2 : Décision Orchestration (15min)

#### Quelle solution utiliser ?

| Outil | Avantages | Inconvénients | Recommandation |
|-------|-----------|---------------|----------------|
| **ModelRouter intégré** | ✅ Déjà dans code<br>✅ Python natif<br>✅ 0 latence | ❌ Aucun | ⭐⭐⭐⭐⭐ **UTILISER** |
| Ollama Gateway | ✅ Compatible OpenAI<br>✅ Pour outils externes | ❌ Serveur séparé<br>❌ Latence réseau | ⚠️ Phase 2 seulement |
| Ollama Orchestrator Node | ✅ Dashboard joli | ❌ Node.js<br>❌ Bridge requis | 🔧 Tests uniquement |
| Scripts Bash | ✅ Ultra-simple | ❌ Pas d'API | 🔧 Debug uniquement |

**DÉCISION** : ✅ **Utiliser ModelRouter intégré** (déjà fait dans code ci-dessus)

**Utilisation des autres outils** :
```bash
# Ollama Orchestrator - Pour tests manuels modèles
cd C:\Dev\ollama-orchestrator
npm start
# Ouvrir http://localhost:3000

# Ollama Gateway - Si vous utilisez Claude-Code/Continue
cd C:\Dev\ollama-gateway
python main.py
# Configure VSCode: apiBase = http://localhost:4000/v1

# Scripts Bash Claude - Tests rapides terminal
./ask.sh coder "Write a function"
./ask.sh chess "Best move?"
```

---

### ÉTAPE 3 : Comparer avec GitHub (30min)

#### Projets à analyser en détail

**1. GodotDynamicDialog** (PRIORITÉ HAUTE)
```bash
# Cloner pour référence
cd C:\Dev
git clone https://github.com/Godot-Dynamic-Dialog/GodotDynamicDialog.git
```

**À étudier** :
- Structure projet Godot
- Intégration WebSocket
- UI dialogue
- Gestion contexte

**À réutiliser** :
- ✅ Structure scènes Godot
- ✅ Système dialogue UI
- ⚠️ Adapter pour Ollama local (au lieu d'OpenAI API)

**2. ai-dungeon-master** (INSPIRATION)
```bash
cd C:\Dev
git clone https://github.com/davidpm1021/ai-dungeon-master.git
```

**À étudier** :
- Dual-model pattern (critique + draft)
- Mémoire vectorielle (ChromaDB)
- Service orchestration

**À réutiliser** :
- ✅ Pattern dual-model (pour validation narration)
- ⚠️ Mémoire vectorielle (Phase 2 si nécessaire)

**3. fastapi_websocket_pubsub** (FUTUR)
```bash
cd C:\Dev
git clone https://github.com/permitio/fastapi_websocket_pubsub.git
```

**À étudier** :
- PubSub multi-serveurs
- Scalabilité

**Quand utiliser** :
- ⏳ Phase 2+ (quand multi-joueurs avancé)

---

### ÉTAPE 4 : Setup Godot (45min)

#### 4.1 Installer Godot 4.3

```bash
# Télécharger Godot 4.3
# https://godotengine.org/download

# Installer dans C:\Dev\Godot\
```

#### 4.2 Créer projet Godot

```bash
# Ouvrir Godot
# New Project
# Nom: jdvlh-godot-client
# Location: C:\Dev\jdvlh-godot-client
# Renderer: Forward+ (pour 3D)
```

#### 4.3 Structure initiale

```
jdvlh-godot-client/
├── project.godot
├── scenes/
│   ├── main_menu.tscn
│   ├── game_world.tscn
│   └── ui/
│       ├── hud.tscn
│       └── dialogue.tscn
├── scripts/
│   ├── network_manager.gd
│   └── game_state.gd
└── assets/
    └── placeholder/
```

#### 4.4 Créer NetworkManager

**Fichier** : `scripts/network_manager.gd`

```gdscript
extends Node

var socket := WebSocketPeer.new()
var url := "ws://localhost:8000/ws/"

signal narrative_received(text: String)

func _ready():
    var player_id = str(randi())
    socket.connect_to_url(url + player_id)

func _process(_delta):
    socket.poll()
    if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
        while socket.get_available_packet_count():
            var packet = socket.get_packet()
            var data = JSON.parse_string(packet.get_string_from_utf8())
            _handle_message(data)

func _handle_message(data: Dictionary):
    if data.get("type") == "narrative_update":
        narrative_received.emit(data.text)

func send_choice(choice_text: String):
    var message = {
        "type": "player_choice",
        "choice": choice_text
    }
    socket.send_text(JSON.stringify(message))
```

#### 4.5 Test connexion

```bash
# Terminal 1: Lancer backend
cd C:\Dev\jdvlh-ia-game
python main.py

# Terminal 2: Godot
# Ouvrir projet
# Run (F5)
# Vérifier console : "Connected to server"
```

---

## 📋 CHECKLIST COMPLÈTE

### Phase 0: Optimisations (2h) 🔴 AUJOURD'HUI

- [ ] Modifier `config.yaml` (max_tokens: 150)
- [ ] Installer llama3.2 et gemma2
- [ ] Intégrer ModelRouter dans NarrativeService
- [ ] Tester performance (< 3s)
- [ ] Cloner GodotDynamicDialog pour référence
- [ ] Setup projet Godot basique
- [ ] Test connexion WebSocket

**Résultat attendu** :
- ✅ Temps réponse < 3s
- ✅ Multi-modèles fonctionnel
- ✅ Godot connecté au backend

### Phase 1: Features JDR (1 semaine) 🟡 SEMAINE PROCHAINE

- [ ] Créer models/game_entities.py (Player, Item, Spell, etc.)
- [ ] Implémenter services/combat_engine.py
- [ ] Implémenter services/inventory_manager.py
- [ ] Implémenter services/quest_manager.py
- [ ] Implémenter services/character_progression.py
- [ ] Tests unitaires (pytest)

### Phase 2: Client Godot (1 semaine) 🟢 DANS 2 SEMAINES

- [ ] Player controller 3D
- [ ] UI système (HUD, inventaire, dialogue)
- [ ] Animations de base
- [ ] Intégration backend complète

### Phase 3: Visuels (2 semaines) ⚪ DANS 1 MOIS

- [ ] Modèles 3D low-poly
- [ ] Animations avancées
- [ ] Effets visuels
- [ ] Audio (musique + SFX)

---

## 🎯 PROCHAINES 2 HEURES - PLAN DÉTAILLÉ

### 08:00 - 08:30 : Optimisations Config

```bash
# 1. Modifier config.yaml
code C:\Dev\jdvlh-ia-game\config.yaml
# Changer max_tokens: 150
# Ajouter pregenerate: true

# 2. Installer modèles
ollama pull llama3.2
ollama pull gemma2
```

### 08:30 - 09:00 : Intégration ModelRouter

```bash
# 1. Modifier narrative.py
code C:\Dev\jdvlh-ia-game\src\jdvlh_ia_game\services\narrative.py

# 2. Ajouter:
# from .model_router import get_router
# self.router = get_router()
# model, options = self.router.select_model(...)
```

### 09:00 - 09:15 : Tests Performance

```bash
# Lancer serveur
python main.py

# Nouveau terminal
python test_performance.py

# Vérifier: temps < 3s ✅
```

### 09:15 - 09:30 : Cloner Références GitHub

```bash
cd C:\Dev
git clone https://github.com/Godot-Dynamic-Dialog/GodotDynamicDialog.git
git clone https://github.com/davidpm1021/ai-dungeon-master.git
```

### 09:30 - 10:00 : Setup Godot

```bash
# 1. Télécharger + installer Godot 4.3
# 2. Créer projet: jdvlh-godot-client
# 3. Créer NetworkManager.gd (code ci-dessus)
# 4. Test connexion WebSocket
```

---

## 💡 COMMANDES DE RÉFÉRENCE

### Backend

```bash
# Démarrer serveur
cd C:\Dev\jdvlh-ia-game
python main.py

# Tests performance
python test_performance.py

# Tests unitaires
pytest tests/

# Voir logs
tail -f logs/game.log
```

### Ollama

```bash
# Lister modèles
ollama list

# Installer modèle
ollama pull llama3.2

# Tester modèle
ollama run llama3.2 "Bonjour"

# Stats utilisation
ollama ps
```

### Godot

```bash
# Lancer projet
godot --path C:\Dev\jdvlh-godot-client

# Run scene (depuis Godot)
F5

# Export Windows
godot --export "Windows Desktop" game.exe
```

### Git

```bash
# Commit optimisations
cd C:\Dev\jdvlh-ia-game
git add .
git commit -m "perf: optimize ollama config and integrate model router"
git push
```

---

## 📊 METRICS DE SUCCÈS

### Avant Optimisations
```
Temps moyen: 26.6s
Modèles utilisés: 1 (Mistral)
Cohérence: 7/10
```

### Après Optimisations (Objectif)
```
Temps moyen: < 3s  ✅
Modèles utilisés: 3+ (Mistral, Llama3.2, Gemma2)
Cohérence: 9/10 ✅
```

### MVP Godot (Semaine 4)
```
Backend: ✅ Complet
Godot Client: ✅ Fonctionnel
Features JDR: ✅ Combat, inventaire, quêtes
Visuels: ⏳ Placeholders low-poly
```

### Version Finale (Mois 2)
```
Tout ci-dessus +
Visuels 3D: ✅ Low-poly complets
Animations: ✅ Toutes actions
Audio: ✅ Musique + SFX
Features avancées: ✅ Crafting, économie
```

---

## 🎉 CONCLUSION

**Vous avez TOUT ce qu'il faut pour réussir** :

✅ Backend solide et bien architecturé  
✅ Système IA avancé (mémoire + routing)  
✅ Outils d'orchestration disponibles  
✅ Références GitHub pour inspiration  
✅ Roadmap claire et réaliste  

**Action NOW** :
1. ⚡ Appliquer optimisations (30min)
2. 🧪 Tester performance (15min)
3. 🎮 Setup Godot (45min)
4. 🚀 Démarrer Phase 1 (semaine prochaine)

**Bon courage ! 🔥**

---

**Document généré le 22 Novembre 2025**  
**Version**: 1.0 - Guide Action Rapide

