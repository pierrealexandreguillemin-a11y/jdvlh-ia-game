#!/bin/bash
# deploy.sh - Déploiement JDVLH IA Game laptop local

set -e

echo "🚀 Déploiement JDVLH IA Game"

# 1. Build images
docker compose build --no-cache

# 2. Start services
docker compose up -d

# 3. Wait postgres ready
echo "⏳ Attente PostgreSQL..."
docker compose exec -T postgres pg_isready --timeout 30

# 4. Backend migrations
echo "🔄 Alembic migrations..."
docker compose exec backend alembic upgrade head || true  # Ignore if no migrations

# 5. Migrate SQLite data if exists
if [ -f "data/game.db" ]; then
  echo "📤 Migration SQLite -> PostgreSQL..."
  docker compose exec backend python scripts/migrate_sqlite_to_postgres.py
fi

# 6. Check Ollama models
echo "🧠 Ollama models:"
docker compose exec backend ollama list || echo "Téléchargez models: ollama pull llama3.2"

# 7. Health checks
echo "✅ Health checks:"
curl -f http://localhost:8000/health || echo "Ajoutez /health endpoint"

# 8. URLs
echo ""
echo "✅ Déploiement terminé!"
echo "Backend API: http://localhost:8000/docs"
echo "Frontend: http://localhost"
echo "Portables enfants: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📱 Test multi-device: Ouvrez plusieurs onglets/portables"
echo "🔒 Contrôle parental: localhost/parental (PIN 1234)"
echo ""
echo "Stop: docker compose down"
echo "Logs: docker compose logs -f backend"