# Contexte d'Origine du Projet JDVLH IA Game

**Date de genèse**: 21 Novembre 2025 (estimation)
**Sources**:

- Conversation Claude: https://claude.ai/share/dec3a3f1-6ebe-4ad1-a811-7a7ef04a91cc (inaccessible)
- Conversation Grok: https://grok.com/share/c2hhcmQtMi1jb3B5_950945ea-c6d5-4c18-91f8-a398285200b3

---

## Vision Initiale du Projet

### Objectif Principal

Créer un **jeu narratif interactif type "Livre dont vous êtes le héros" (LDVELH)** avec génération IA locale pour enfants de 10-14 ans, thématique LOTR/D&D.

### Public Cible

- **Âge**: 10-14 ans
- **Contexte**: Enfants du développeur
- **Usage**: Familial, multi-device (portables)

### Vision Technique Originale

- **IA locales** Ollama (zéro coût, privacy)
- **Serveur maison** sur laptop backend
- **Clients** sur portables des enfants
- **Visuel** 3D low-poly "scotchant"
- **Budget**: 0€ (tier gratuit uniquement)

---

## Contraintes Hardware Validées

### Laptop Serveur (Specs Réelles)

```
CPU: AMD Ryzen 5 5600H (6 cœurs/12 threads)
RAM: 16 GB DDR4
GPU: AMD Radeon Graphics INTÉGRÉS ⚠️
Storage: Ollama 46 GB (9 modèles installés)
```

### Modèles Ollama Disponibles

```
Production ready:
- mistral:latest (4.4 GB) - Narration principale
- deepseek-coder-v2 (8.9 GB) - Génération code
- gemma2 - Raisonnement/énigmes
- qwen2.5 - Dialogues NPC
- llama3.2 - Descriptions environnements

Chess agents (customisés):
- deepseek-chess
- gemma2-chess
- qwen2.5-chess
- llama3.2-chess
```

---

## Décisions Architecturales Initiales

### Stack Technologique Recommandée (par Grok)

#### Backend

- **Python FastAPI** (API REST légère + WebSocket)
- **Ollama Client** (réutiliser code chess-app)
- **WebSocket** pour sync temps réel
- **Modelfile custom** "game-master" optimisé LOTR/DnD

#### Frontend

- **Godot 4.3** (export HTML5) ✅ RECOMMANDÉ
  - Léger: 180 MB vs 7+ GB Unity
  - Optimisé GPU faibles
  - Export web natif
  - 3D low-poly fluide (<3k polygones/scène)

- **Unity** ❌ NON RECOMMANDÉ
  - Trop lourd pour GPU intégré
  - Compilation lente
  - Chauffe laptop

#### Architecture Orchestration IA

```
┌─────────────────────────────────────────┐
│  GAME MASTER ORCHESTRATOR               │
├─────────────────────────────────────────┤
│  Narration Engine                       │
│  - Mistral (principal, 4.4GB)           │
│  - Fallback: gemma2 si busy             │
│                                         │
│  Dialogue NPC Engine                    │
│  - Qwen2.5 (personnalités variées)      │
│                                         │
│  World Building / Descriptions          │
│  - Llama3.2 (rapide, environnements)    │
│                                         │
│  Code Generation (runtime si besoin)    │
│  - DeepSeek-Coder-V2                    │
└─────────────────────────────────────────┘
         ↓ WebSocket
┌─────────────────────────────────────────┐
│  GODOT CLIENT (HTML5 sur portables)     │
└─────────────────────────────────────────┘
```

### Stratégie "One Model at a Time"

**Contrainte RAM critique**: Maximum 1-2 modèles Ollama actifs simultanément

**Consommation estimée**:

- Ollama inference: ~2-4 GB RAM par modèle
- Serveur backend: ~500 MB
- Godot 3D: ~1 GB
- **Total**: 4-8 GB (reste 8-12 GB pour OS)

---

## Contraintes et Limitations Identifiées

### Limitation GPU Intégrée ⚠️

**Impact sur visuels "scotchants"**:

- ❌ Scènes 3D complexes (>10k polygones) = lag
- ❌ Effets visuels avancés (particules, shaders) = framerate faible
- ❌ Éclairage dynamique = <30 fps

**Visuels réalistes avec GPU intégré**:

- ✅ Low-poly stylisé (style Wind Waker, Minecraft)
- ✅ Environnements <3k-5k polygones/scène
- ✅ Animations fluides mais basiques
- ✅ Particules ultra-légères (max 50 particles)
- ✅ Effet "scotchant" via narration IA + sons immersifs

### Risques Techniques Anticipés

| Risque                                    | Sévérité  | Mitigation                          |
| ----------------------------------------- | --------- | ----------------------------------- |
| Chauffe laptop (Ollama + serveur + Godot) | 🔴 Élevé  | Sous-volting CPU, refroidisseur     |
| Framerate instable (<30 fps 3D)           | 🟠 Modéré | Fallback 2D isometric si besoin     |
| Scope creep ("scotcher les kids")         | 🟠 Modéré | MVP strict, itération post-feedback |
| WiFi lag multi-device                     | 🟡 Faible | WebSocket léger, optimisation       |

---

## Points Critiques Soulevés par Grok

### Sécurité Enfants (CRITIQUE) 🔴

**Statut initial**: ❌ ABSENT

- Pas de filtre contenu IA
- Pas de modération
- Pas de contrôle parental

**Actions requises**:

- Implémenter LlamaGuard ou filtre similaire
- Liste noire mots étendue (100+ termes)
- Logs accessibles parents
- Disclaimer légal

### Performance Réaliste

**Annoncé initialement**: 2-4s par génération
**Réalité mesurée**: 4-8s (voire 26.6s selon tests)
**Cible optimisée**: <3s après optimisations

### Architecture Client

**Problème initial**: HTML pur = impasse technique
**Solution**: Migration Godot HTML5 ou React/Vue moderne

---

## Roadmap Originale (par Grok)

### Phase 1 : Setup + Prototype Narratif Pur (Semaine 1)

- Installer Godot 4.3
- Backend Flask/FastAPI + Ollama client
- Test narration texte pure (0 visuel)
- Validation IA + serveur

### Phase 2 : Visuel Low-Poly Basique (Semaine 2)

- Scène 3D minimale Godot (1 perso, 1 environnement)
- Test perfs GPU intégré (>30 fps ?)
- Si lag: fallback 2D isometric

### Phase 3 : Animations Réactives (Semaine 3)

- Map outputs IA → triggers animations
- 5-10 animations clés (idle, marche, attaque, sort)
- Particules ultra-légères

### Phase 4 : Multi-Device (Semaine 4)

- Export HTML5 Godot
- WebSocket serveur ↔ clients
- Test 1-2 portables sur WiFi local

### Phase 5-6 : Polish "Scotchant" (Semaines 5-6)

- Sons immersifs (ambiance + SFX)
- UI tactile kid-friendly
- 3-5 scènes (forêt, château, caverne)
- Beta test avec enfants → itération

**Timeline totale**: 4-6 semaines

---

## Contradictions Détectées (Analyses Post-Dev)

### Analyse Claude (Optimiste)

- Score MVP: 9/10
- "Testable maintenant !"
- Backend complet décrit (WebSocket, cache, sécurité)

### Analyse Cline (Réaliste)

- Score Global: 3/10
- "PROJET EN PHASE D'INITIALISATION"
- "Littéralement vide : pas de code source"

**Interprétation probable**:

- Analyse Claude = Vision/Blueprint (ce qui devrait exister)
- Analyse Cline = Audit réel (état actuel du code)
- **OU**: Développement entre les deux analyses

---

## Expérience Préalable (Chess-App)

### Projet chess-app (Référence)

L'utilisateur a déjà créé un système d'orchestration Ollama pour audit de code échecs:

**Architecture**:

- 4 agents spécialisés (deepseek-chess, gemma2-chess, qwen2.5-chess, llama3.2-chess)
- Orchestration séquentielle (audit code statique)
- Gain: 82% réduction tokens
- Statut: Production, validé

**Différence avec jdvlh-ia-game**:
| Critère | Chess-App | JDVLH Game |
|---------|-----------|------------|
| Usage | Séquentiel, offline | Concurrent, temps réel |
| Output | Documents statiques | Narration dynamique streaming |
| Modèles | 4 agents spécialisés | 5+ modèles polyvalents |
| Latence | Non critique | <3s critique (UX enfants) |

---

## Prompt Recommandé pour Claude Code (par Grok)

```
Je veux créer un Game Master Orchestrator pour un jeu narratif
LOTR/DnD destiné à mes enfants (10-14 ans).

ARCHITECTURE CIBLE:
- Backend Python (FastAPI + WebSocket)
- Orchestration intelligente de mes 9 modèles Ollama
- Export pour serveur standalone (pas juste dev VSCode)
- Communication temps réel avec clients Godot (HTML5)

MODÈLES DISPONIBLES:
- mistral:latest (narration principale)
- qwen2.5 (dialogues NPC)
- llama3.2 (descriptions environnements)
- gemma2 (raisonnement/énigmes)
- deepseek-coder-v2 (génération code si besoin)

BESOINS SPÉCIFIQUES:
1. Route WebSocket /game/narrative (stream événements)
2. Endpoint /game/world-description (descriptions lieux)
3. Endpoint /game/npc-dialogue (dialogues personnages)
4. Système de contexte (mémoire conversation par joueur)
5. Gestion "One Model at a Time" (RAM limitée: 16GB)

CONTRAINTES:
- Laptop AMD Ryzen 5 5600H, 16GB RAM, GPU intégré
- Maximum 1-2 modèles Ollama actifs simultanément
- Architecture low-latency (<3s par génération)

OUTPUTS ATTENDUS:
- Code serveur Python complet
- Client test simple (HTML/JS)
- Scripts de démarrage
- Documentation configuration

Peux-tu créer cette architecture maintenant ?
```

---

## Questions Clés Non Résolues (fin conversation Grok)

### Question 1 : Tu acceptes les contraintes GPU ?

- **Oui** → Godot low-poly stylisé
- **Non** → Attendre GPU dédié (non réaliste court-terme)

### Question 2 : Priorité visuels vs narration ?

- **60% visuel / 40% IA** → Godot 3D simple
- **40% visuel / 60% IA** → Godot 2D isometric + narration riche

### Question 3 : Chronologie ?

- **MVP 2 semaines** (narratif pur + visuel basique)
- **Full project 6 semaines** (multi-device + polish)

**Statut**: Questions posées par Grok, réponses non documentées

---

## État Actuel du Projet (24 Novembre 2025)

D'après les commits Git et analyses:

### Ce qui a été implémenté (confirmé)

- ✅ Backend FastAPI avec 5 WebSockets
- ✅ Services JDR complets (combat, quêtes, inventory, progression)
- ✅ Intégration PF2e SRD (1584 sorts, traductions FR)
- ✅ Système i18n FR/EN (80+ clés)
- ✅ Guide joueur français complet
- ✅ Tests unitaires (51 passés)
- ✅ Documentation exhaustive (12+ guides)

### Ce qui reste à faire (analyse production)

- ❌ Frontend moderne (HTML basique actuel)
- ❌ Docker/déploiement
- ❌ Godot client 3D (non démarré)
- ❌ Multi-device effectif
- ❌ Sécurité enfants renforcée
- ❌ Migration PostgreSQL (SQLite actuel)

---

## Alignement avec Vision Originale

### Points Alignés ✅

1. **IA locale Ollama** → Implémenté (multi-modèles via ModelRouter)
2. **Backend serveur maison** → FastAPI opérationnel
3. **Thématique LOTR/DnD** → PF2e intégré (système D&D-like)
4. **Public 10-14 ans** → Guide joueur FR adapté
5. **Budget 0€** → Stack gratuite (Python, FastAPI, SQLite)

### Écarts avec Vision Originale ⚠️

1. **Godot 3D** → Pas encore démarré (HTML client actuel)
2. **Multi-device portables** → Non implémenté
3. **Visuels "scotchants"** → Interface basique actuelle
4. **Sécurité enfants** → Partiellement implémentée

### Évolution Architecture

**Vision Grok** (Novembre début):

```
Ollama → FastAPI → Godot HTML5 (portables)
```

**Réalité Actuelle** (24 Novembre):

```
Ollama → FastAPI + 10 services → index.html basique
         ↓
    PF2e SRD (1584 sorts) + i18n FR/EN
```

**Progression**: Backend excellent (70% production-ready), frontend à refondre

---

## Recommandations Finales (Synthèse)

### Court Terme (Semaines 1-2)

1. **Décider stack frontend**:
   - Option A: Godot 4.3 (vision originale)
   - Option B: React/Vue moderne (recommandation analyse)

2. **Implémenter sécurité enfants** (CRITIQUE)
   - Filtre contenu IA
   - Contrôle parental

3. **Tester performance réelle**
   - Valider <3s par génération
   - Mesurer chauffe laptop

### Moyen Terme (Semaines 3-6)

- Créer client moderne (Godot ou React)
- Docker + déploiement
- Tests multi-device effectifs
- Beta test avec enfants

### Questions pour Utilisateur

1. **Maintenir vision Godot 3D** ou **pivoter vers React/Vue** ?
2. **Priorité immédiate**: Frontend ou sécurité enfants ?
3. **Timeline cible**: MVP 2 semaines ou production complète 6-8 semaines ?

---

**Document créé**: 24 Novembre 2025
**Par**: Claude Code (Assistant)
**Base**: Conversations Grok + Claude + Analyse codebase réel
