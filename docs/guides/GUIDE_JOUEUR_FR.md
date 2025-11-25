# Guide du Joueur - JDVLH IA Game

**Bienvenue, aventurier !**

Ce guide vous accompagnera dans votre périple épique à travers la Terre du Milieu. Découvrez comment jouer, progresser, et devenir un héros légendaire !

---

## Table des matières

1. [Démarrage rapide](#d%C3%A9marrage-rapide)
2. [Création de personnage](#cr%C3%A9ation-de-personnage)
3. [Interface de jeu](#interface-de-jeu)
4. [Système de combat](#syst%C3%A8me-de-combat)
5. [Inventaire et équipement](#inventaire-et-%C3%A9quipement)
6. [Quêtes et progression](#qu%C3%AAtes-et-progression)
7. [Magie et sorts](#magie-et-sorts)
8. [Conseils et astuces](#conseils-et-astuces)

---

## Démarrage rapide

### Première connexion

1. **Connexion au jeu**
   - Accédez au serveur de jeu via WebSocket
   - Votre identifiant joueur est généré automatiquement
   - Le jeu sauvegarde automatiquement votre progression

2. **Message de bienvenue**

   ```
   Bienvenue en Terre du Milieu !
   Que fais-tu dans la Comté ?
   ```

3. **Premiers choix**
   - Explorer la forêt
   - Rencontrer un hobbit
   - Chercher un trésor

### Navigation

- **Choix narratifs** : Sélectionnez une option pour avancer l'histoire
- **Actions contextuelles** : Vos choix influencent le récit
- **Lieux** : Explorez la Comté, Fondcombe, les Mines de la Moria, et plus !

---

## Création de personnage

### Races disponibles

| Race       | Bonus           | Description                                |
| ---------- | --------------- | ------------------------------------------ |
| **Humain** | Polyvalent      | +1 à toutes les statistiques, adaptabilité |
| **Elfe**   | Agilité +2      | Grâce naturelle, vision nocturne           |
| **Nain**   | Constitution +2 | Robuste, résistant aux poisons             |
| **Hobbit** | Discrétion +2   | Petite taille, chanceux                    |

### Classes disponibles

| Classe       | Style de jeu        | Armes favorites            |
| ------------ | ------------------- | -------------------------- |
| **Guerrier** | Combat rapproché    | Épées, haches, boucliers   |
| **Mage**     | Magie offensive     | Bâtons, sorts destructeurs |
| **Rôdeur**   | Distance et nature  | Arcs, pièges, survie       |
| **Clerc**    | Soutien et guérison | Masses, magie divine       |

### Statistiques de base

- **Force (FOR)** : Dégâts au corps-à-corps, capacité de charge
- **Intelligence (INT)** : Puissance magique, compétences mentales
- **Agilité (AGI)** : Esquive, précision à distance, vitesse
- **Constitution (CON)** : Points de vie, résistance
- **Sagesse (SAG)** : Perception, magie divine
- **Charisme (CHA)** : Influence sociale, commandement

**Répartition initiale** : 60 points à distribuer (minimum 8, maximum 18 par stat)

---

## Interface de jeu

### Informations du personnage

```
┌─────────────────────────────┐
│ Aventurier - Niveau 5       │
│ Guerrier Humain             │
├─────────────────────────────┤
│ PV:  85/100  ████████░░     │
│ MP:  40/60   ██████░░░░     │
│ XP:  1250/2000               │
├─────────────────────────────┤
│ Or: 350 po                  │
│ Lieu: la Comté              │
└─────────────────────────────┘
```

### Barre d'actions

- **Attaquer** : Attaque basique avec l'arme équipée
- **Sort** : Lancer un sort de votre grimoire
- **Objet** : Utiliser un consommable (potion, parchemin)
- **Défendre** : Réduire les dégâts reçus de 50%
- **Fuir** : Tenter d'échapper au combat (jet d'agilité)

### Notifications

- 🎖️ **Niveau supérieur** : Vous gagnez un niveau !
- ⚔️ **Combat** : Un ennemi apparaît
- 📜 **Quête** : Nouvelle quête disponible
- 💰 **Trésor** : Vous trouvez de l'or ou un objet
- ⚠️ **Danger** : Attention, piège ou ennemi puissant

---

## Système de combat

### Déroulement d'un tour

1. **Initiative** : L'ordre des actions est déterminé par l'agilité
2. **Tour du joueur** : Choisissez une action
3. **Tour des ennemis** : Les adversaires attaquent
4. **Résolution** : Calcul des dégâts et effets
5. **Répéter** jusqu'à victoire ou défaite

### Actions de combat

#### Attaque basique

- **Dégâts** : Basés sur votre arme + Force
- **Précision** : Jet de dé 1d20 + modificateur
- **Critique** : Sur un 20 naturel (dégâts x2)

#### Lancer un sort

- **Coût** : Points de mana selon le niveau du sort
- **Effets** : Dégâts, soin, contrôle, ou buffs
- **Exemples** :
  - _Boule de feu_ (6d6 dégâts de feu)
  - _Guérison_ (2d8+5 PV restaurés)
  - _Bouclier_ (+5 AC pendant 1 minute)

#### Défense

- **Réduction** : -50% dégâts reçus ce tour
- **Bonus** : +2 à la classe d'armure
- **Stratégie** : Utilisez quand vous êtes bas en PV

#### Utiliser un objet

- **Potions de soins** : Restaurent 2d4+2 PV instantanément
- **Parchemins** : Lancent un sort sans coût de mana
- **Élixirs** : Buffs temporaires (+2 FOR pendant 3 tours)

### Ennemis communs

| Ennemi                 | Niveau | PV   | Attaque | Stratégie               |
| ---------------------- | ------ | ---- | ------- | ----------------------- |
| **Gobelin voleur**     | 1      | 50   | 10      | Attaquez rapidement     |
| **Orc des plaines**    | 3      | 80   | 15      | Défendez, puis attaquez |
| **Troll des cavernes** | 5      | 150  | 25      | Utilisez la magie       |
| **Dragon**             | 10+    | 300+ | 40+     | Combat d'équipe requis  |

### Butin et récompenses

**Après victoire** :

- **Or** : 10-100 pièces selon l'ennemi
- **Expérience** : Proportionnelle au niveau de l'adversaire
- **Objets** : Chance de loot (armes, armures, potions)

**Formule XP** :

```
XP gagnés = (Niveau ennemi × 100) + bonus de difficulté
```

---

## Inventaire et équipement

### Gestion de l'inventaire

**Capacité** : 20 emplacements (augmentable avec des sacs)

**Types d'objets** :

- **Armes** : Épées, arcs, bâtons, dagues
- **Armures** : Légères, moyennes, lourdes
- **Accessoires** : Anneaux, amulettes, ceintures
- **Consommables** : Potions, parchemins, nourritures
- **Quête** : Objets spéciaux pour missions

### Emplacements d'équipement

```
┌───────────────────────┐
│  Tête:    [Casque]    │
│  Torse:   [Cotte]     │
│  Mains:   [Gants]     │
│  Arme:    [Épée]      │
│  Off:     [Bouclier]  │
│  Jambes:  [Jambières] │
│  Pieds:   [Bottes]    │
│  Anneau1: [Vide]      │
│  Anneau2: [Vide]      │
│  Amulette:[Vide]      │
└───────────────────────┘
```

### Rareté des objets

- **Commun** (gris) : Objets de base
- **Peu commun** (vert) : Bonus modérés
- **Rare** (bleu) : Bons bonus, effets spéciaux
- **Épique** (violet) : Très puissants, rares
- **Légendaire** (orange) : Uniques, quête ou boss

### Amélioration d'équipement

**Chez le forgeron** :

1. **Réparation** : 10% du prix de l'objet
2. **Amélioration** : +1 aux stats (coût = valeur × 2)
3. **Enchantement** : Ajoute un effet magique (500 po minimum)

---

## Quêtes et progression

### Types de quêtes

#### Quêtes principales

- **Storyline** : Progression de l'histoire principale
- **Récompenses** : XP élevés, équipement unique
- **Difficulté** : Adaptée à votre niveau
- **Linéaire** : Suit une narration spécifique

#### Quêtes secondaires

- **Exploration** : Découvrir des lieux cachés
- **Chasse** : Éliminer X ennemis d'un type
- **Collecte** : Récupérer des objets spécifiques
- **Escorte** : Protéger un PNJ
- **Récompenses** : Or, objets, réputation

#### Quêtes dynamiques

- **Générées aléatoirement** par l'IA
- **Adaptées à votre niveau** et localisation
- **Variées** : Chaque partie est unique

### Objectifs et progression

```
📜 Quête: "La menace gobeline"
   ├─ ✅ Parler au chef du village
   ├─ ⏳ Éliminer 10 gobelins (7/10)
   └─ 🔒 Trouver le repaire (non débloqué)

Récompenses:
   - 500 XP
   - 100 po
   - Épée longue +1
```

### Montée de niveau

**Niveau 1 → 2** : 1000 XP
**Formule** : `XP requis = niveau × 1000`

**Gains par niveau** :

- +10 PV max
- +5 MP max (pour les classes magiques)
- +1 point de compétence
- Choix : +1 stat ou nouvelle compétence

---

## Magie et sorts

### Écoles de magie (Pathfinder 2e)

| École           | Type         | Sorts typiques                           |
| --------------- | ------------ | ---------------------------------------- |
| **Évocation**   | Dégâts       | Boule de feu, Éclair, Projectile magique |
| **Abjuration**  | Protection   | Bouclier, Protection contre le mal       |
| **Nécromancie** | Vie/Mort     | Drain de vie, Animation des morts        |
| **Divination**  | Connaissance | Détection de la magie, Vision            |
| **Illusion**    | Tromperie    | Image miroir, Invisibilité               |
| **Invocation**  | Créatures    | Convocation d'animal, Alliés planaires   |

### Sorts par niveau (MVP - Niveaux 0-3)

#### Cantrips (Niveau 0) - Sans coût de mana

- **Lumière** : Crée une source de lumière
- **Rayon de givre** : 1d4+1 dégâts de froid
- **Détection de la magie** : Révèle les auras magiques
- **Prestidigitation** : Petits effets magiques

#### Niveau 1 - 5 MP

- **Projectile magique** : 3 projectiles, 1d4+1 chacun (ne rate jamais)
- **Guérison** : Restaure 2d8+5 PV
- **Bouclier** : +5 AC pendant 1 minute
- **Mains brûlantes** : Cône 15 pieds, 3d6 dégâts de feu

#### Niveau 2 - 10 MP

- **Invisibilité** : Invisible pendant 10 minutes
- **Image miroir** : 3 copies illusoires
- **Arme spirituelle** : Attaque magique bonus
- **Restauration** : Soigne maladies et poisons

#### Niveau 3 - 15 MP

- **Boule de feu** : 20 pieds de rayon, 6d6 dégâts de feu
- **Éclair** : Ligne 100 pieds, 8d6 dégâts d'électricité
- **Rapidité** : +1 action par tour pendant 1 minute
- **Vol** : Volezpendant 10 minutes

### Lancer un sort en combat

1. **Sélectionner** "Sort" dans le menu combat
2. **Choisir** le sort dans votre grimoire
3. **Cibler** l'ennemi ou l'allié
4. **Dépenser** les points de mana
5. **Résoudre** l'effet (jet de sauvegarde ennemi si applicable)

### Récupération de mana

- **Repos court** (10 min) : 25% du mana max
- **Repos long** (8h) : 100% du mana max
- **Potion de mana** : Restaure 2d4+2 MP instantanément

---

## Conseils et astuces

### Pour débutants

1. **Sauvegardez souvent** : Le jeu sauvegarde automatiquement, mais vous pouvez forcer une sauvegarde avec `/save`

2. **Équilibrez votre inventaire** :
   - 5 potions de soins minimum
   - 2-3 potions de mana (pour les mages)
   - 1-2 parchemins de téléportation d'urgence

3. **Priorités de combat** :
   - Ciblez les ennemis faibles en premier
   - Gardez les sorts puissants pour les boss
   - Défendez quand vous êtes bas en PV

4. **Gestion de l'or** :
   - Ne vendez pas les objets rares sans réfléchir
   - Investissez dans l'amélioration d'équipement
   - Gardez 200 po de réserve pour urgences

### Stratégies avancées

#### Build Guerrier tank

- **Stats** : CON > FOR > AGI
- **Équipement** : Armure lourde + bouclier
- **Compétences** : Charge, Second souffle, Mur de fer
- **Rôle** : Absorber les dégâts, protéger les alliés

#### Build Mage DPS

- **Stats** : INT > SAG > CON
- **Sorts** : Boule de feu, Éclair, Projectile magique
- **Compétences** : Intensification de sort, Magie rapide
- **Rôle** : Dégâts de zone, contrôle du champ de bataille

#### Build Rôdeur polyvalent

- **Stats** : AGI > FOR > SAG
- **Équipement** : Arc long + dague
- **Compétences** : Tir précis, Pistage, Pièges
- **Rôle** : Dégâts à distance, exploration, survie

### Erreurs à éviter

❌ **Ne pas lire les descriptions** : Chaque objet et sort a des effets uniques
❌ **Gaspiller le mana** : Les cantrips sont gratuits, utilisez-les !
❌ **Ignorer les quêtes secondaires** : Elles donnent beaucoup d'XP
❌ **Vendre tout le butin** : Certains objets servent pour des quêtes
❌ **Combattre des ennemis trop forts** : Fuyez si l'ennemi est +3 niveaux

### Ressources utiles

- **Wiki du jeu** : [En construction]
- **Forum communautaire** : [À venir]
- **Support technique** : GitHub Issues
- **Règles Pathfinder 2e** : https://2e.aonprd.com/

---

## Glossaire

| Terme        | Signification                      |
| ------------ | ---------------------------------- |
| **AC**       | Classe d'Armure (défense)          |
| **PV**       | Points de Vie                      |
| **MP**       | Points de Mana                     |
| **XP**       | Points d'Expérience                |
| **DPS**      | Dégâts par Seconde                 |
| **Tank**     | Personnage qui absorbe les dégâts  |
| **Buff**     | Amélioration temporaire            |
| **Debuff**   | Affaiblissement temporaire         |
| **AoE**      | Area of Effect (zone d'effet)      |
| **DoT**      | Damage over Time (dégâts continus) |
| **Proc**     | Déclenchement d'un effet spécial   |
| **Cooldown** | Temps de recharge                  |

---

## Crédits

**Développement** : Claude Code + Équipe JDVLH
**Système de jeu** : Pathfinder 2e (Paizo Inc.)
**Traductions** : Black Book Éditions + Communauté Pathfinder-FR
**Univers** : Tolkien - Terre du Milieu (inspiration)

**Licence contenu PF2e** : Open Gaming License (OGL)

---

**Bon jeu, et que la chance soit avec vous, aventurier !** ⚔️🛡️🔮

_Guide mis à jour le 24 Novembre 2025_
