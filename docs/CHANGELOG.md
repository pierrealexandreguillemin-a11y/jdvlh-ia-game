# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

## [Unreleased]

### Added

- Documentation complète (`docs/ARCHITECTURE.md`, `DEVELOPMENT.md`, `API.md`)

---

## [0.2.0] - 2025-01-XX

### Added

- **Frontend React 19** avec Vite 7 et TypeScript 5.9
- **Paper UI System** - Thème médiéval avec assets parchemin
- Composants principaux:
  - `StoryDisplay` - Affichage narratif avec effet typewriter
  - `CharacterSheet` - Fiche personnage complète et compacte
  - `ChoiceButton` - Boutons stylisés médiévaux
  - `GameLayout` - Layout bureau-livre médiéval
- Configuration Tailwind CSS v4 avec `@tailwindcss/vite`
- Proxy WebSocket vers backend Python
- Types TypeScript pour `Character`, `NarrativeResponse`, `Item`

### Changed

- Structure projet avec dossier `jdvlh-frontend/` séparé

---

## [0.1.0] - 2025-01-XX

### Added

- **ContentFilter PEGI 16** - Filtrage contenu pour adolescents
  - Violence réaliste autorisée
  - Langage grossier autorisé
  - Horreur intense autorisée
  - Bloque: pornographie explicite, torture extrême, discrimination
- 39 tests unitaires pour validation PEGI 16
- Intégration ContentFilter dans `NarrativeService`
- Filtrage double: entrée joueur + sortie IA

### Security

- Protection contre injection contenu inapproprié
- Conformité PEGI 16 (Pan European Game Information)

---

## [0.0.1] - 2024-XX-XX

### Added

- Structure projet initiale
- **FastAPI** backend avec WebSocket
- **NarrativeService** - Génération narrative via Ollama
- **CombatEngine** - Système combat tour par tour
- **QuestManager** - Quêtes dynamiques générées IA
- **InventoryManager** - Gestion inventaire/équipement
- **CharacterProgression** - Système de niveau et compétences
- **NarrativeMemory** - Mémoire contextuelle pour IA
- **ModelRouter** - Routage intelligent modèles Ollama
- **PF2eContent** - Intégration données Pathfinder 2e
- **i18n** - Système internationalisation (FR par défaut)
- Modèles SQLAlchemy pour persistance
- Configuration YAML centralisée

### Infrastructure

- Poetry pour gestion dépendances
- Pytest pour tests
- Black + isort + flake8 pour qualité code
- Commitlint pour conventional commits
