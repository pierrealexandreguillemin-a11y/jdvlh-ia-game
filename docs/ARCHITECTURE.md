# Architecture JDVLH-IA-Game

## Vue d'ensemble

JDVLH (Jeu Dont Vous êtes Le Héros) est un jeu narratif interactif utilisant l'IA pour générer des aventures dynamiques dans l'univers de la Terre du Milieu.

```
┌─────────────────────────────────────────────────────────────────┐
│                      JDVLH-IA-Game                               │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React 19 + Vite + Tailwind v4)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ StoryDisplay│ │CharacterSheet│ │ChoiceButton│               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                    Paper UI Theme                               │
├─────────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + WebSocket)                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    WebSocket Endpoints                       ││
│  │  /ws/{player_id}        - Narrative principale              ││
│  │  /ws/combat/{player_id} - Système de combat                 ││
│  │  /ws/inventory/{player_id} - Gestion inventaire             ││
│  │  /ws/quests/{player_id} - Quêtes dynamiques                 ││
│  │  /ws/character/{player_id} - Progression personnage         ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Services Layer                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │NarrativeServ │ │CombatEngine  │ │QuestManager  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ContentFilter │ │InventoryMgr │ │CharProgress  │            │
│  │  (PEGI 16)   │ └──────────────┘ └──────────────┘            │
│  └──────────────┘                                               │
├─────────────────────────────────────────────────────────────────┤
│  AI Layer (Ollama)                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ModelRouter   │ │NarrativeMemory│ │PF2eContent  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │SQLAlchemy    │ │StateManager  │ │CacheService  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Stack Technique

### Backend

- **Python 3.12+**
- **FastAPI 0.115** - Framework API async
- **Uvicorn** - Serveur ASGI
- **Ollama** - LLM local (Mistral/Llama)
- **SQLAlchemy 2.0** - ORM
- **Alembic** - Migrations DB
- **Pydantic 2.9** - Validation données

### Frontend

- **React 19.2** - UI Framework
- **Vite 7** - Build tool
- **TypeScript 5.9** - Type safety
- **Tailwind CSS 4** - Styling
- **Paper UI System** - Assets médiévaux

### Sécurité

- **ContentFilter PEGI 16** - Filtrage contenu approprié adolescents
- **SlowAPI** - Rate limiting
- **CORS** - Protection cross-origin

## Structure des dossiers

```
jdvlh-ia-game/
├── src/jdvlh_ia_game/
│   ├── core/
│   │   └── game_server.py      # FastAPI app + WebSocket endpoints
│   ├── services/
│   │   ├── narrative.py        # Génération narrative IA
│   │   ├── content_filter.py   # Filtrage PEGI 16
│   │   ├── combat_engine.py    # Système de combat
│   │   ├── quest_manager.py    # Quêtes dynamiques
│   │   ├── inventory_manager.py # Gestion items
│   │   ├── character_progression.py # Leveling
│   │   ├── model_router.py     # Routage modèles IA
│   │   ├── narrative_memory.py # Mémoire contextuelle
│   │   ├── pf2e_content.py     # Intégration Pathfinder 2e
│   │   └── i18n.py             # Internationalisation
│   ├── models/
│   │   └── game_entities.py    # Entités du jeu
│   ├── db/
│   │   └── models.py           # Modèles SQLAlchemy
│   ├── middleware/
│   │   └── security.py         # Middleware sécurité
│   └── config/
│       └── config.yaml         # Configuration
├── jdvlh-frontend/
│   ├── src/
│   │   ├── components/         # Composants React
│   │   ├── types/              # Types TypeScript
│   │   └── App.tsx             # Application principale
│   └── public/assets/          # Paper UI assets
├── tests/
│   └── test_content_filter.py  # Tests PEGI 16
└── docs/                       # Documentation
```

## Flux de données

### Narrative Flow

```
Player Choice → ContentFilter (input) → NarrativeService
                                            ↓
                                      ModelRouter
                                            ↓
                                      Ollama LLM
                                            ↓
                                    Parse JSON Response
                                            ↓
                              ContentFilter (output) → Player
```

### Combat Flow

```
Combat Action → CombatEngine → Calculate Results → Update Player State
                     ↓
              Generate Narrative → Send via WebSocket
```

## Services principaux

### NarrativeService

Génère les réponses narratives via Ollama avec:

- Mémoire contextuelle (NarrativeMemory)
- Enrichissement PF2e (sorts, équipement)
- Filtrage double (input/output)

### ContentFilter (PEGI 16)

Classification Pan-European Game Information adaptée aux 16+:

- Violence réaliste autorisée
- Langage grossier autorisé
- Horreur intense autorisée
- Bloque: pornographie, torture extrême, discrimination

### CombatEngine

Système de combat tour par tour avec:

- Actions: attaque, sort, objet, défense
- Calcul dégâts basé stats
- Génération narrative dynamique

### QuestManager

Quêtes dynamiques générées par IA avec:

- Objectifs multiples
- Récompenses (XP, or, items)
- Suivi progression

## Configuration

Fichier `config/config.yaml`:

```yaml
ollama:
  model: "mistral"
  max_retries: 3
  temperature: 0.7
  max_tokens: 500

server:
  max_players: 100

prompts:
  system: "Tu es un Maître du Jeu..."
```

## Scalabilité

- **Stateless**: Chaque requête indépendante
- **Cache**: Pré-génération contenus
- **WebSocket**: Connexions persistantes efficaces
- **Async**: Traitement non-bloquant
