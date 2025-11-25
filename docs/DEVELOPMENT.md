# Guide de Développement

## Prérequis

- Python 3.12+
- Node.js 20+
- Poetry (gestionnaire dépendances Python)
- Ollama (LLM local)

## Installation

### Backend

```bash
# Cloner le repo
git clone https://github.com/your-repo/jdvlh-ia-game.git
cd jdvlh-ia-game

# Installer dépendances Python
poetry install

# Installer Ollama et télécharger modèle
ollama pull mistral
```

### Frontend

```bash
cd jdvlh-frontend

# Installer dépendances
npm install
```

## Lancer le projet

### Backend (port 8000)

```bash
poetry run uvicorn jdvlh_ia_game.core.game_server:app --reload
```

### Frontend (port 3000)

```bash
cd jdvlh-frontend
npm run dev
```

## Tests

### Backend

```bash
# Tous les tests
poetry run pytest

# Avec couverture
poetry run pytest --cov=src/jdvlh_ia_game

# Tests spécifiques
poetry run pytest tests/test_content_filter.py -v
```

### Frontend

```bash
cd jdvlh-frontend
npm run lint
npm run build  # Vérifie types TypeScript
```

## Conventions de code

### Python

- **Black** pour le formatage
- **isort** pour les imports
- **Flake8** pour le linting

```bash
# Formatter
poetry run black src/ tests/
poetry run isort src/ tests/

# Lint
poetry run flake8 src/ tests/
```

### TypeScript/React

- **ESLint** pour le linting
- **TypeScript strict mode**
- **Imports type-only** pour les types

```typescript
// Correct
import type { Character } from "../types/game";

// Incorrect
import { Character } from "../types/game";
```

## Commits

Format **Conventional Commits**:

```
feat(scope): description courte

Corps du message (optionnel)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types autorisés:

- `feat` - Nouvelle fonctionnalité
- `fix` - Correction bug
- `docs` - Documentation
- `refactor` - Refactoring
- `test` - Ajout/modification tests
- `chore` - Maintenance

## Ajouter un nouveau service

1. Créer fichier dans `src/jdvlh_ia_game/services/`
2. Ajouter factory dans `game_server.py`
3. Ajouter tests dans `tests/`

Exemple:

```python
# src/jdvlh_ia_game/services/my_service.py
class MyService:
    def __init__(self):
        pass

    async def do_something(self) -> dict:
        return {"result": "ok"}

# game_server.py
def get_my_service() -> MyService:
    return MyService()
```

## Ajouter un composant React

1. Créer fichier dans `jdvlh-frontend/src/components/`
2. Exporter dans `components/index.ts`
3. Suivre le style Paper UI

```typescript
// src/components/MyComponent.tsx
interface MyComponentProps {
  title: string;
}

export function MyComponent({ title }: MyComponentProps) {
  return (
    <div className="panel-paper p-4">
      <h2 className="text-amber-900">{title}</h2>
    </div>
  );
}

// src/components/index.ts
export { MyComponent } from './MyComponent';
```

## Classes CSS Paper UI

```css
/* Panel parchemin */
.panel-paper {
  background-color: rgba(244, 228, 188, 0.95);
  border: 8px solid;
  border-image: url(/assets/paper-ui/dialogue/3.png) 30 round;
}

/* Couleurs thème */
.text-amber-900  /* Texte principal */
.text-amber-700  /* Texte secondaire */
.bg-amber-100    /* Fond boutons */
.border-amber-700 /* Bordures */
```

## Variables d'environnement

Créer `.env` à la racine:

```env
# Ollama
OLLAMA_HOST=http://localhost:11434

# Server
MAX_PLAYERS=100
DEBUG=true
```

## Debug

### Backend

```python
# Activer logs détaillés dans config.yaml
debug: true

# Utiliser print pour debug rapide
print(f"[DEBUG] Variable: {variable}")
```

### Frontend

```typescript
// Console browser
console.log('Debug:', data);

// React DevTools
npm install -D @types/react-devtools
```

## Troubleshooting

### Ollama ne répond pas

```bash
# Vérifier service
ollama list

# Redémarrer
ollama serve
```

### TypeScript erreurs d'import

```bash
# Reconstruire types
cd jdvlh-frontend
rm -rf node_modules/.vite
npm run build
```

### Tests échouent

```bash
# Vérifier dépendances
poetry install --sync

# Nettoyer cache pytest
poetry run pytest --cache-clear
```
