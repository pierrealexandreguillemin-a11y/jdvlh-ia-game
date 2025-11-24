# 🗡️ JDVLH IA Game v0.6.0 - Livre Dont Vous Êtes Le Héros 🧙‍♂️

[![Version](https://img.shields.io/badge/version-0.6.0-blue.svg)](https://github.com/user/jdvlh-ia-game)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Husky](https://img.shields.io/badge/husky-enabled-success.svg)](https://typicode.github.io/husky/)

**Jeu narratif interactif IA pour enfants 10-14 ans** - Thème Terre du Milieu (LOTR/D&D)

**Stack:** FastAPI + Ollama/Mistral (IA locale) + SQLite + WebSocket temps réel
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

## 🎲 Pathfinder 2e Integration

Le jeu intègre le **SRD Pathfinder 2e complet** avec traduction française prioritaire:

### Contenu Disponible

- ✅ **1584 sorts** (860 sorts MVP niveau ≤3)
- ✅ **Traduction FR** (6 sorts prioritaires + fallback EN automatique)
- ✅ **Feature flags** (MVP/Intermediate/Full)
- ✅ **API REST** pour accès sorts
- ✅ **Intégration NarrativeService** (détection automatique sorts)

### Configuration

```yaml
# config.yaml
pf2e:
  active_level: mvp # mvp (10-12 ans) | intermediate (12-14 ans) | full (14+)
```

### API Endpoints

```bash
# Liste sorts MVP (niveau ≤3)
GET /api/pf2e/spells?level=3

# Détails sort avec traduction FR
GET /api/pf2e/spells/fireball  # → "Boule de feu"

# Recherche full-text
GET /api/pf2e/spells/search?q=feu&limit=5
```

### Usage en Jeu

Les joueurs peuvent utiliser des sorts dans leurs actions:

```
Joueur: "Je lance spell:fireball sur les orques"
→ IA reçoit: "Sort utilisé: Boule de feu (niveau 3) - Vous créez une explosion de flammes"
```

**Documentation complète**: [data/pf2e/README.md](data/pf2e/README.md)

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
