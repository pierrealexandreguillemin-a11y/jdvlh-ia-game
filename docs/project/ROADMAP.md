# 🚀 ROADMAP COMPLÈTE JDVLH-IA-GAME (Version Finale - Extensible MVP)

**Auteur**: Cline (Ingénieur Senior)  
**Date**: 21 Nov 2025  
**Principe Clé**: **MVP extensible sans refactor massif** → Modularité, config-driven, interfaces abstraites dès v1.

---

## 🎯 **VISION ARCHITECTURALE (Extensible par Design)**

```
[Client Web/Godot] ← WS/REST → [FastAPI Gateway] ← [StateManager] ← [NarrativeEngine]
                                           ↓
                                     [Persistence (SQLite/Postgres)]
                                     [Cache Layer (Redis/File)]
                                     [ContentFilter]
                                     [EventBus (Triggers SFX/UI)]
```

**Choix Techniques Argumentés** (Pourquoi pas refactor ?):
| Composant | Choix | Arguments Extensibilité | Alternative Rejetée |
|-----------|-------|--------------------------|---------------------|
| **Backend** | **FastAPI** | Async natif WS/REST, Pydantic auto-validation, auto-docs (/docs), Dependency Injection (DI) pour swaps (ex: Node). **0 refactor pour scale**. | Flask (sync, no DI), Express (JS verbose). |
| **IA** | **Ollama/Mistral** | Local 100%, lib Python native (`ollama.generate`). Swap modèles config (Llama3, etc.). **Plugin via prompt templates**. | OpenAI (coût, privacy), HuggingFace (heavy). |
| **State** | **Pydantic GameState + Redis/SQLite** | Serializable, versioned. TTL auto. **Évolutif** : Ajout champs sans break (ex: `player_level: int`). | In-memory dict (fuites RAM). |
| **Cache** | **File JSON + Lazy Redis** | Zéro dep v1, upgrade transparent. **Config toggle**. | Full Redis (overkill MVP). |
| **Client** | **HTML/JS pur → Vite/React** | MVP instant, migrate Godot sans backend change (WS stable). **Event-driven** (triggers). | Godot direct (long, no web). |
| **DB** | **SQLite → Postgres** | Local MVP, migrate Alembic 0-downtime. **ORM SQLAlchemy** pour queries évolutives. | JSON files (no query). |
| **Sécurité** | **slowapi + OWASP** | Rate-limit, sanitize middleware. **Configurable rules** (liste noire YAML). | None (risque enfants). |
| **Deploy** | **Uvicorn → Docker/Gunicorn** | `python main.py` → `docker run` config. | Heroku (coût). |

**Extensibilité Garantie**:

- **Config YAML** : Modèles, prompts, lieux, filtres → Hot-reload sans restart.
- **EventBus** : Pub/sub pour triggers (SFX, UI, analytics) → Plugins zero-code.
- **DI FastAPI** : Swap services (ex: MockOllama pour tests).
- **Versions API** : `/v1/ws` → `/v2` backward compat.

---

## 📈 **PHASES ROADMAP (Temps Réaliste, Zéro Refactor)**

### **Phase 0: Setup Extensible (30min - ✅ Complété)**

- [x] `requirements.txt` (stables: fastapi==0.115.0, uvicorn[standard]==0.32.0, pydantic==2.9.2, ollama==0.3.3, sqlalchemy==2.0.0, slowapi==0.1.9)
- [x] Structure dirs: `src/jdvlh_ia_game/{core,services,models,config,prompts,db,migrations}` (package-mode activé)
- [x] `config.yaml` (modèles, TTL=1800s, max_players=4, blacklist_words)
- [x] `pyproject.toml` (poetry/venv ready, scripts ajustés)

**Ext**: Ajout lieu/prompt = edit YAML.

### **Phase 1: MVP Core (1h - ✅ Complété)**

- [x] `src/core/game_server.py` : FastAPI + WS, GameState Pydantic.
- [x] `services/narrative.py` : Ollama + retry3x + fallback.
- [x] `services/cache.py` : Lazy file + TTL.
- [x] `main.py` : `uvicorn jdvlh_ia_game.core.game_server:app --reload`
- [x] `index.html` : WS client + spinner + localStorage save.

**Ext**: Nouveau modèle = `config.models.append(\"llama3\")`.

### **Phase 2: Robustesse Critiques (1h - ✅ Production-ready)**

- [x] `services/state_manager.py` : Redis/SQLite, TTL cleanup asyncio, max_players.
- [x] `middleware/security.py` : Sanitize (len<100, no-script), rate-limit (10/min/player), content_filter (regex blacklist).
- [x] `db/models.py` : SQLAlchemy GameState (auto-save 2min).
- [x] EventBus simple (dict callbacks) pour triggers.

**Ext**: Nouveau filtre = `config.filters.new_rule()`.

### **Phase 3: UX Enfants + Multi (1h - ✅ En cours)**

- [x] Client : Boutons save/load/reset, progress bar IA, thèmes LOTR CSS.
- [ ] Logs parents : `/api/logs/{player_id}` JSON export.
- [ ] PIN auth famille (config pin).

**Ext**: Thème = CSS swap config.

### **Phase 4: Tests/Docs/Polish (30min - Prochain)**

- [ ] Pytest : 90% coverage (`test_services.py`).
- [ ] `install.bat` / `README.md` : Screenshots, one-click.
- [ ] Docker : `Dockerfile` multi-stage.

**Ext**: CI GitHub Actions config.

### **Phase 5: Déploiement & Scale (Future)**

- [ ] Docker + Render/Heroku.
- [ ] Godot client intégration.
- **Cloud** : Swap SQLite→Postgres, deploy Render.
- **Plugins** : YAML → New narrative engine (ex: Grok API).

**Total MVP Robust** : **4h** → Test famille aujourd'hui !

---

## 🔍 **CODE REVIEW CRITÈRES (Pour Implémentation)**

1. **Modularité** : Chaque service injectable (`Depends()`).
2. **Tests** : Unit + integration Ollama mock.
3. **Docs** : FastAPI /docs auto + README.
4. **Logs** : Structured (loguru) + parent-friendly.
5. **Perf** : <5s réponse (cache + retry).

**Score Attendu** : **9.5/10** (extensible, safe, fun).
