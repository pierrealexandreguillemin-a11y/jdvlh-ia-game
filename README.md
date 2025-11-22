# JDVLH IA Game v0.2.0 - Livre Dont Vous Êtes Le Héros (IA Locale)

**Jeu narratif interactif pour enfants 10-14 ans** (thème LOTR/DnD).  
**Stack** : FastAPI (Python 3.12), Ollama/Mistral (IA locale), SQLite (persistance), WebSocket realtime. Multi-joueurs foyer (max 4), sécurité enfants renforcée.

**Score MVP** : 8/10 (robuste, extensible, safe, fun). **Testable maintenant !**

## 🚀 Installation (5 min)

### Prérequis
- Python 3.12+
- Ollama : `ollama pull mistral`
- Poetry (recommandé) : `pip install poetry`

### Poetry (Recommandé)
```
poetry install
poetry run python main.py
```

### Pip Alternatif
1. `python -m venv venv`
2. `venv\Scripts\activate && pip install -r requirements.txt`
3. `ollama serve` (nouveau terminal)
4. `python main.py`

### Vérif
- Serveur : http://localhost:8000/docs (FastAPI Swagger)
- Health : http://localhost:8000/health
- WS Test : Ouvrir `index.html`

## 🎮 Utilisation
1. Ouvrir `index.html` (double-clic/live server)
2. Jouer (choix IA 3-8s, WebSocket realtime)
3. PIN parents (1234) : Save/Load/Reset/Logs

**Multi** : Jusqu'à 4 onglets/joueurs (IDs uniques, limite serveur).

## 🛡️ Sécurité Enfants
- Blacklist mots sensibles (config.yaml)
- Rate-limit (SlowAPI)
- Sanitize inputs (Pydantic)
- Sessions TTL 30min + max 4 joueurs
- PIN parents : 1234 (Save/Reset/Logs)

## 📊 Perf (Ryzen 5 / 16Go)
- RAM : Ollama 6-8Go + serveur ~0.5Go
- Réponse : 3-8s (cache pré-généré 12 lieux)
- Max 4 joueurs simultanés

## 🏗️ Architecture

```
Client (index.html/WS) ───┐
                          ↓ WS /ws/{player_id}
FastAPI (game_server.py) ─┼── StateManager (SQLite game.db)
                          ↓
Services ────────────────┼── CacheService (JSON lieux: Comté, Moria...)
  ├── NarrativeService ───┘     (Ollama Mistral + Mémoire/Histoire)
  ├── EventBus
  └── ModelRouter
```

**Flux** : Choice → Prompt enrichi (mémoire + history) → Ollama JSON → Update state/cache → Response realtime.

## 🗂️ Structure Projet
```
jdvlh-ia-game/
├── main.py (launcher uvicorn)
├── config.yaml (central)
├── pyproject.toml (Poetry)
├── cache/*.json (12 lieux LOTR)
├── game.db (SQLite)
├── src/jdvlh_ia_game/
│   ├── core/game_server.py (FastAPI/WS)
│   ├── services/
│   │   ├── cache.py
│   │   ├── narrative.py (Ollama + mémoire)
│   │   ├── state_manager.py
│   │   └── ...
│   ├── db/models.py (SQLAlchemy)
│   ├── middleware/security.py
│   └── ...
└── index.html (Frontend simple)
```

## 📈 Roadmap
Voir [ROADMAP.md](ROADMAP.md) (Godot, visuels, Docker, tests avancés).

## 🔧 Debug & Outils
- **Logs** : Loguru (console)
- **Reset** : POST /reset/{player_id}
- **Migrations** : `poetry run migrate` (Alembic)
- **Tests** : `poetry run test` (Pytest)
- **Ollama** : Auto-retry (3x) + fallback statique

## 🤝 Contribution
1. Fork & PR
2. `poetry install --with dev`
3. Tests : `poetry run test`
4. Format : `poetry run black .`

**Changelog v0.2.0** : README enrichi (architecture, stack, Poetry, diagramme, outils).

1. Fork & PR
2. `poetry install --with dev`
3. Tests : `poetry run test`
4. Format : `poetry run black .`

**Changelog v0.2.0** : README enrichi (arch/archi, Poetry, diagramme).

