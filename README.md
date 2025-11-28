# 🗡️ JDVLH IA Game v0.7.0 - Livre Dont Vous Êtes Le Héros 🧙‍♂️

[![Version](https://img.shields.io/badge/version-0.7.0-blue.svg)](https://github.com/user/jdvlh-ia-game)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Pathfinder 2e](https://img.shields.io/badge/Pathfinder-2e-red.svg)](https://paizo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Husky](https://img.shields.io/badge/husky-enabled-success.svg)](https://typicode.github.io/husky/)

**Jeu narratif interactif IA pour adolescents 14-18 ans** - Univers **Pathfinder 2e / Golarion**

**Stack:** FastAPI + Ollama/Mistral (IA locale) + React/Paper UI + WebSocket temps réel
**Frontend:** React + TypeScript + Framer Motion + Paper UI System (thème médiéval)
**Développement:** Solo dev + Claude Code + Grok (IA assistants)
**Qualité:** Hooks Git (Husky), commits conventionnels, formatting auto

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

### Frontend React

```bash
cd jdvlh-frontend
npm install
npm run dev
```

### Vérif

- Backend API : http://localhost:8000/docs (FastAPI Swagger)
- Health : http://localhost:8000/health
- Frontend : http://localhost:5173 (Vite dev server)

## 🎮 Utilisation

### Mode Connecté (Backend actif)

1. Démarrer le backend (`python main.py`)
2. Démarrer le frontend (`npm run dev` dans `jdvlh-frontend/`)
3. Jouer (WebSocket temps réel, IA génère les réponses)

### Mode Démo (Offline)

1. Démarrer uniquement le frontend
2. Le jeu fonctionne avec des réponses pré-définies
3. Parfait pour tester l'UI sans backend

**Lancé de dés:** Quand l'IA demande un jet de compétence (Perception, Athlétisme, etc.), une interface de dé d20 interactive s'affiche. Le joueur clique pour lancer le dé !

**Multi** : Jusqu'à 4 joueurs simultanés (sessions WebSocket indépendantes).

## 🛡️ Sécurité Ados (PEGI 16)

- **ContentFilter PEGI 16** : Violence fantasy acceptable, pas de gore extrême
- Blacklist mots sensibles (config.yaml)
- Rate-limit (SlowAPI)
- Sanitize inputs (Pydantic)
- Sessions TTL 30min + max 4 joueurs
- **Contrôle parental** : PIN 1234 (Settings/Logs/Export)

## 🎲 Pathfinder 2e Integration

Le jeu utilise l'univers **Golarion** et les règles **Pathfinder 2e** :

### Univers Golarion

- **Absalom** : Cité au Centre du Monde (point de départ)
- **Sandpoint** : Village côtier, ruines de Thassilon
- **Magnimar** : Cité des Monuments
- **Varisie** : Région d'aventures classiques
- Et bien d'autres lieux mythiques...

### Règles PF2e Intégrées

- **Système à 3 actions** par tour
- **Jets de dés interactifs** (d20 + modificateur vs DC)
- **Compétences PF2e** : Perception, Athlétisme, Arcanes, Diplomatie...
- **Sorts** : 1584 sorts disponibles avec traduction FR

### Lancé de Dés

Quand l'IA demande un jet de compétence :

1. Une modal s'affiche avec un **d20 interactif**
2. Le joueur **clique** pour lancer le dé
3. Animation de roulement + résultat (succès/échec/critique)
4. Le résultat est intégré à la narration

### API Endpoints

```bash
# Liste sorts
GET /api/pf2e/spells?level=3

# Détails sort avec traduction FR
GET /api/pf2e/spells/fireball  # → "Boule de feu"

# Recherche full-text
GET /api/pf2e/spells/search?q=feu&limit=5
```

**Documentation complète**: [data/pf2e/README.md](data/pf2e/README.md)

## 📊 Perf (Ryzen 5 / 16Go)

- RAM : Ollama 6-8Go + serveur ~0.5Go
- Réponse : 3-8s (cache pré-généré 12 lieux)
- Max 4 joueurs simultanés

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│  App.tsx ─── StoryDisplay ─── CharacterSheet ─── DiceRoller │
│      │                                                      │
│      └── useWebSocket hook (ws://localhost:8000/ws/{id})    │
└─────────────────────────────────────────────────────────────┘
                          ↓ WebSocket
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                       │
│  game_server.py ─┬── StateManager (SQLite)                  │
│                  ├── NarrativeService (Ollama + PF2e)       │
│                  ├── CombatEngine                           │
│                  ├── ParentalControl                        │
│                  └── SessionManager                         │
└─────────────────────────────────────────────────────────────┘
```

**Flux narratif** :

1. Joueur fait un choix → WebSocket
2. Backend génère prompt PF2e enrichi (mémoire + history + contexte Golarion)
3. Ollama génère réponse JSON
4. Si `DICE_ROLL:skill:DC` détecté → Frontend affiche modal dé
5. Joueur lance le dé → Résultat intégré → Narration affichée

## 🗂️ Structure Projet

```
jdvlh-ia-game/
├── main.py (launcher uvicorn)
├── config.yaml (central - PF2e config)
├── pyproject.toml (Poetry)
├── cache/*.json (lieux Golarion)
├── game.db (SQLite)
├── src/jdvlh_ia_game/
│   ├── core/game_server.py (FastAPI/WS)
│   ├── services/
│   │   ├── narrative.py (Ollama + PF2e + mémoire)
│   │   ├── combat_engine.py
│   │   ├── parental_control.py
│   │   ├── pf2e_content.py
│   │   └── ...
│   ├── db/models.py (SQLAlchemy)
│   └── middleware/security.py
├── jdvlh-frontend/           # React Frontend
│   ├── src/
│   │   ├── App.tsx           # Main app + WebSocket
│   │   ├── components/
│   │   │   ├── narrative/    # StoryDisplay, ChoiceButton
│   │   │   ├── character/    # CharacterSheet
│   │   │   ├── combat/       # DiceRoller, CombatInterface
│   │   │   └── ui/           # Paper UI components
│   │   ├── hooks/            # useWebSocket, useAudio
│   │   └── types/            # TypeScript types
│   └── public/assets/paper-ui/  # Humble Gift Paper UI sprites
└── data/pf2e/                # SRD Pathfinder 2e
```

## 📈 Roadmap

Voir [ROADMAP.md](ROADMAP.md) (Godot, visuels, Docker, tests avancés).

## 🔧 Debug & Outils

- **Logs** : Loguru (console)
- **Reset** : POST /reset/{player_id}
- **Migrations** : `poetry run migrate` (Alembic)
- **Tests** : `poetry run test` (Pytest)
- **Ollama** : Auto-retry (3x) + fallback statique

## 🔄 Git Workflow & Qualité du Code

### Hooks Git Automatiques (Husky)

Le projet utilise **Husky** pour garantir la qualité du code à chaque commit :

#### ✅ Pre-commit Hook

- Format automatique du code Python avec **Black**
- Vérification qualité avec **Flake8** (warnings non-bloquants)
- Linting fichiers staged avec **lint-staged**
- Exécution tests si présents

#### 📋 Commit-msg Hook

- Validation des messages de commit (Conventional Commits)
- Format requis: `type(scope): description`
- Types autorisés: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`

**Exemples de commits valides:**

```bash
feat: add narrative memory system
fix: correct unicode error in cache.py
docs: update README with git workflow
perf: optimize num_predict to 400 tokens
refactor: improve routing logic
```

#### 📊 Post-commit Hook

- Génération automatique du graphe Git (`git-graph.txt`)
- Mise à jour des statistiques (commits, fichiers, dernière modif)

### Commandes Git Utiles

```bash
# Voir le graphe des commits
git log --oneline --graph --all --decorate

# Créer une branche feature
git checkout -b feat/nouvelle-fonctionnalite

# Commit avec message conventionnel (validé auto par hook)
git commit -m "feat: add new location system"

# Voir les stats du projet
git shortlog -sn --all

# Historique d'un fichier
git log --follow -- path/to/file.py

# Générer le graphe manuellement
npm run generate-graph
```

### Structure des Branches

```
master (production)
  ├── feat/routing-integration (nouvelle feature)
  ├── fix/unicode-errors (correction bug)
  ├── docs/update-readme (documentation)
  └── perf/optimize-generation (performance)
```

### Scripts NPM Disponibles

```bash
npm run lint          # Vérifier code Python
npm run format        # Formatter code Python
npm run test          # Lancer tests
npm run generate-graph # Générer graphe Git
```

---

## 🤝 Développement Solo + IA

**Workflow:** Dev solo assisté par IA (Claude Code + Grok)

- **Claude Code:** Analyse architecture, génération code, refactoring
- **Grok:** Assistance contexte, debugging, suggestions
- **Husky:** Garantie qualité automatique à chaque commit

Pas besoin de CI/CD serveur (GitHub Actions/GitLab CI) pour un projet solo.
Les hooks Git locaux suffisent pour maintenir la qualité.

---

## 📚 Documentation

- **[INDEX_COMPLET.md](INDEX_COMPLET.md)** - Guide navigation master
- **[DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md)** - Quick start 3 niveaux
- **[GIT_ANALYSIS.md](GIT_ANALYSIS.md)** - Analyse Git complète avec diagrammes Mermaid
- **[RAPPORT_FINAL.md](RAPPORT_FINAL.md)** - Synthèse session complète
- **[RAPPORT_PERFORMANCE.md](RAPPORT_PERFORMANCE.md)** - Analyse performance détaillée
- **[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)** - Guide routing multi-modèles
- **[MEMOIRE_CONTEXTUELLE.md](MEMOIRE_CONTEXTUELLE.md)** - Guide mémoire narrative

---

## 📝 Changelog

### v0.7.0 (2025-11-28)

- ✅ **Pivot Pathfinder 2e** : Univers Golarion remplace Terre du Milieu
- ✅ **Frontend React** : Interface complète avec Paper UI System
- ✅ **Lancé de dés** : Modal d20 interactif avec animation
- ✅ **WebSocket** : Connexion temps réel + mode démo offline
- ✅ **PEGI 16** : ContentFilter adapté adolescents 14-18 ans
- ✅ **Paper UI** : Assets Humble Gift intégrés (dialogue, headers, HUD)

### v0.6.0 (2025-11-22)

- ✅ **CI/CD:** Husky hooks (pre-commit, commit-msg, post-commit)
- ✅ **Quality:** Conventional commits, auto-formatting, lint-staged
- ✅ **Git:** Analyse complète avec diagrammes Mermaid
- ✅ **Docs:** README mis à jour, 12 guides complets
- ✅ **Perf:** Optimisations narrative (400 tokens, structure 8-12 phrases)
- ✅ **UX:** Langue française forcée, textes riches, temps de lecture

### v0.5.0

- Dependencies tracking (requirements, poetry.lock, package.json)

### v0.4.0

- Documentation complète (4800+ lignes)

### v0.3.0

- Outils d'analyse et dashboards

### v0.2.0

- Services core (narrative, routing, memory)

### v0.1.0

- Initial commit - Base projet

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour détails
