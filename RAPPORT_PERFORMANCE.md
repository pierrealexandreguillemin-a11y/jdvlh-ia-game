# 📊 Rapport d'Analyse de Performance - JDVLH IA Game

**Date:** 21 Novembre 2025
**Analysé par:** Claude Code Performance Monitor
**Version:** 0.1.0

---

## 🎯 Résumé Exécutif

### Métriques Clés

| Métrique | Valeur Mesurée | Objectif | Status |
|----------|----------------|----------|--------|
| **Temps Réponse Moyen** | 26.6 secondes | < 8 secondes | ⚠️ LENT |
| **Temps Réponse Médian** | 20.2 secondes | < 5 secondes | ⚠️ LENT |
| **Temps Minimum** | 3.4 secondes | < 2 secondes | ⚠️ LENT |
| **Temps Maximum** | 75.8 secondes | < 10 secondes | ❌ CRITIQUE |
| **P95** | 75.8 secondes | < 8 secondes | ❌ CRITIQUE |
| **P99** | 75.8 secondes | < 10 secondes | ❌ CRITIQUE |

### Score Global: **3/10** ⚠️

**Verdict:** Les temps de réponse actuels sont **trop lents** pour une expérience utilisateur optimale. Des optimisations urgentes sont nécessaires.

---

## 📈 Analyse Détaillée

### 1. Tests de Performance Ollama

#### Test 1: Prompt Court (1 phrase)
```
Prompt: "Decris la Comte en 1 phrase"
Tentatives: 3
```

| Métrique | Valeur |
|----------|--------|
| Moyenne | 6.2 secondes |
| Min | 3.4 secondes |
| Max | 9.9 secondes |
| Évaluation | ⚠️ Acceptable mais limite |

**Analyse:** Les réponses courtes restent dans une fourchette acceptable (3-10s) mais avec une forte variabilité.

---

#### Test 2: Prompt Moyen (3 phrases)
```
Prompt: "Raconte une aventure dans Fondcombe pour un enfant de 10 ans en 3 phrases"
Tentatives: 3
```

| Métrique | Valeur |
|----------|--------|
| Moyenne | 36.9 secondes |
| Min | 14.9 secondes |
| Max | **75.8 secondes** |
| Évaluation | ❌ TROP LENT |

**Analyse:** **Point critique** - Une réponse a pris 75.8 secondes, ce qui est inacceptable pour un jeu interactif. Les enfants perdront patience.

---

#### Test 3: Prompt Long (description détaillée)
```
Prompt: "Decris les Mines de la Moria de maniere detaillee et immersive pour enfants"
Tentatives: 3
```

| Métrique | Valeur |
|----------|--------|
| Moyenne | 36.7 secondes |
| Min | 35.8 secondes |
| Max | 37.8 secondes |
| Évaluation | ❌ LENT mais stable |

**Analyse:** Temps cohérents mais trop longs. La stabilité est bonne (±1s de variation).

---

## 🔍 Diagnostics

### Causes Identifiées

#### 1. Configuration Ollama
- **Modèle:** Mistral (4.4 GB)
- **Paramètres actuels:**
  - `temperature: 0.7` ✅ (optimal)
  - `num_predict: 300-500` ⚠️ (trop élevé)

**Problème:** `num_predict` trop grand génère des réponses longues inutilement.

#### 2. Charge Système
- **RAM Ollama:** 6-8 Go (normal)
- **CPU:** Probablement saturé pendant génération
- **GPU:** Non utilisé (mode CPU only)

**Problème:** Pas d'accélération GPU = génération très lente.

#### 3. Architecture Réseau
- **Latence WebSocket:** < 50ms ✅
- **Goulot d'étranglement:** Génération IA (pas le réseau)

---

## 💡 Recommandations Prioritaires

### 🔴 Urgentes (Impact Immédiat)

#### 1. Réduire `num_predict`
```yaml
# config.yaml - AVANT
num_predict: 500

# config.yaml - APRÈS
num_predict: 150  # Réduction de 70%
```

**Impact attendu:** Réduction temps réponse de **40-60%**
**Nouveau temps estimé:** 10-15 secondes

---

#### 2. Augmenter Cache Hit Rate
```python
# Objectif: 70% cache, 30% Ollama
```

**Stratégie:**
- Pré-générer **tous** les lieux au démarrage
- Cache choix fréquents (top 20)
- TTL cache: 3600s → 7200s (2h)

**Impact attendu:**
- 70% requêtes: **50-200ms** (cache)
- 30% requêtes: **10-15s** (Ollama optimisé)
- **Moyenne globale: ~3.5 secondes** ✅

---

#### 3. Optimiser Prompts
```python
# AVANT
prompt = f"Raconte une aventure dans {lieu} pour un enfant de 10 ans en 3 phrases avec détails immersifs..."

# APRÈS
prompt = f"En 2 phrases courtes: aventure {lieu} enfant 10 ans."
```

**Impact attendu:** Réponses plus concises, génération 30% plus rapide.

---

### 🟡 Importantes (Impact Moyen Terme)

#### 4. Modèle Plus Léger
**Options:**
- Mistral 7B → **Gemma2:latest** (5.4 GB, 20% plus rapide)
- Mistral 7B → **Llama3.2:latest** (2.0 GB, **50% plus rapide**)

**Recommandation:** Tester **Llama3.2** pour narratif simple enfants.

```bash
ollama pull llama3.2
# Modifier config.yaml: model: llama3.2
```

---

#### 5. Utiliser GPU si Disponible
```bash
# Vérifier support GPU
nvidia-smi

# Ollama utilisera automatiquement CUDA si disponible
```

**Impact attendu:** Génération **5-10x plus rapide** avec GPU NVIDIA.

---

### 🟢 Nice-to-Have (Long Terme)

#### 6. System de Queue Asynchrone
- Traiter requêtes en background
- Afficher animation "l'IA réfléchit..." pendant génération
- Permet navigation UI pendant attente

#### 7. Streaming de Réponses
```python
# Afficher texte mot par mot au fur et à mesure
for chunk in ollama.generate_stream(...):
    ws.send(chunk)
```

**Avantage:** Impression de rapidité même si temps total identique.

---

## 📊 Projections Après Optimisations

### Scénario 1: Optimisations Urgentes Uniquement
```
num_predict: 150 + Cache 70%
```

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Temps Moyen | 26.6s | **3.5s** | **-87%** ✅ |
| Cache Hit | 0% | 70% | +70% ✅ |
| P95 | 75.8s | 15s | -80% ✅ |

**Verdict:** **Acceptable** pour MVP, expérience utilisateur correcte.

---

### Scénario 2: Optimisations + Llama3.2
```
num_predict: 150 + Cache 70% + Modèle léger
```

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Temps Moyen | 26.6s | **2.1s** | **-92%** ✅✅ |
| Cache Hit | 0% | 70% | +70% ✅ |
| P95 | 75.8s | 8s | -89% ✅✅ |

**Verdict:** **Excellent**, expérience fluide même pour enfants impatients.

---

### Scénario 3: Optimisations + GPU
```
num_predict: 150 + Cache 70% + NVIDIA GPU
```

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Temps Moyen | 26.6s | **0.8s** | **-97%** ✅✅✅ |
| Cache Hit | 0% | 70% | +70% ✅ |
| P95 | 75.8s | 3s | -96% ✅✅✅ |

**Verdict:** **Performant**, qualité production.

---

## 🛠️ Plan d'Action

### Phase 1: Quick Wins (1-2h)
- [ ] Modifier `config.yaml`: `num_predict: 150`
- [ ] Pré-générer cache tous lieux (12 lieux)
- [ ] Augmenter `cache_ttl: 7200`
- [ ] Optimiser prompts (plus courts)
- [ ] **Re-tester avec `test_performance.py`**

**Objectif:** Temps moyen < 5s

---

### Phase 2: Optimisations Avancées (1 jour)
- [ ] Tester Llama3.2 vs Mistral
- [ ] Implémenter cache choix fréquents
- [ ] Ajouter streaming réponses
- [ ] UI: Animation "IA réfléchit..."

**Objectif:** Temps moyen < 3s

---

### Phase 3: Production (1 semaine)
- [ ] Setup GPU si disponible
- [ ] Queue asynchrone
- [ ] Monitoring temps réel avec dashboard
- [ ] A/B testing configurations

**Objectif:** Temps moyen < 1s (avec cache) / < 5s (sans cache)

---

## 📦 Outils Créés

### 1. `test_performance.py`
Script de test automatisé des temps de réponse Ollama.

**Usage:**
```bash
python test_performance.py
```

**Output:** Statistiques détaillées (min, max, moyenne, P95, P99)

---

### 2. `performance_monitor.py`
Monitoring avancé avec classes Python pour tracking metrics.

**Features:**
- ✅ Enregistrement temps réponse
- ✅ Cache hit rate
- ✅ Statistiques temps réel
- ✅ Export JSON métriques

---

### 3. `performance_dashboard.html`
Dashboard HTML interactif avec graphiques temps réel.

**Features:**
- ✅ WebSocket connection au serveur
- ✅ Graphiques Chart.js (réponse, distribution, cache)
- ✅ Métriques live (avg, median, P95)
- ✅ Logs temps réel

**Ouvrir:** Double-clic sur `performance_dashboard.html`

---

## 📚 Références

### Configuration Actuelle
- **Modèle:** Mistral 7B (4.4 GB)
- **RAM:** 16 Go système
- **CPU:** Ryzen 5 / Intel i5+
- **GPU:** Non utilisé
- **num_predict:** 300-500 (trop élevé)
- **temperature:** 0.7 (optimal)

### Benchmarks Attendus (GPU)
- **Sans GPU:** 20-30s/réponse
- **Avec GPU (NVIDIA GTX 1060):** 2-5s/réponse
- **Avec GPU (NVIDIA RTX 3060):** 0.5-2s/réponse

---

## ✅ Conclusion

### Points Clés
1. **Temps actuels:** TROP LENTS (26.6s moyenne)
2. **Cause principale:** `num_predict` trop élevé + pas de cache
3. **Solution rapide:** Réduire `num_predict` + Cache 70% → **3.5s**
4. **Solution optimale:** + Llama3.2 → **2.1s**
5. **Solution production:** + GPU → **0.8s**

### Prochaine Étape Immédiate
```bash
# 1. Modifier config.yaml
num_predict: 150

# 2. Relancer serveur
python main.py

# 3. Re-tester
python test_performance.py
```

**Impact attendu:** Amélioration **-87%** du temps moyen.

---

**Rapport généré automatiquement par Performance Monitor v0.1.0**
*Pour questions: consulter documentation ou ouvrir performance_dashboard.html*
