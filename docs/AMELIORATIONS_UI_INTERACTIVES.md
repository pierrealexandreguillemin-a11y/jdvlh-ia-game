# Options d'Améliorations UI Interactives - JDVLH v0.7.0

> Analyse complète des éléments interactifs à implémenter (session 2025-11-28)

## Statut Actuel

| Catégorie     | Implémenté | Partiel | À faire |
| ------------- | ---------- | ------- | ------- |
| Jets de dés   | 5          | 1       | 1       |
| Combat        | 10         | 0       | 3       |
| Inventaire    | 8          | 0       | 4       |
| Quêtes        | 6          | 0       | 5       |
| Progression   | 4          | 0       | 6       |
| Notifications | 3          | 0       | 6       |
| **Total**     | **36**     | **1**   | **25**  |

---

## Priorité 1 - Modals Essentiels

### 1.1 Level Up Modal

**Fichier**: `character_progression.py:176-191`
**Status**: NON IMPLÉMENTÉ

```tsx
// Composant suggéré: LevelUpModal.tsx
interface LevelUpModalProps {
  newLevel: number;
  statsGained: { hp: number; mana: number };
  skillPointsGained: number;
  newSkillsUnlocked: Skill[];
}
```

**Affichage**:

- Animation célébration (confetti, glow)
- Résumé stats gagnées
- Bouton allocation points
- Son fanfare

---

### 1.2 Loot Screen Modal

**Fichier**: `game_server.py:390-396`
**Status**: JSON OK, UI manquante

```tsx
// Composant suggéré: LootModal.tsx
interface LootModalProps {
  items: Item[]; // Avec rarity color
  goldGained: number;
  xpGained: number;
  leveledUp?: boolean;
}
```

**Affichage**:

- Coffre qui s'ouvre (animation)
- Items avec bordure couleur rarity
- Compteur or animé
- Barre XP qui se remplit

---

### 1.3 Combat Damage Popup

**Fichier**: `combat_engine.py:303-322`
**Status**: NON IMPLÉMENTÉ

```tsx
// Composant suggéré: DamagePopup.tsx
interface DamagePopupProps {
  amount: number;
  type: "physical" | "magical" | "heal" | "critical";
  position: { x: number; y: number };
}
```

**Affichage**:

- Chiffres flottants au-dessus de la cible
- Rouge (dégâts), Vert (soins), Or (critique)
- Animation float-up + fade-out

---

### 1.4 Skill Tree Modal

**Fichier**: `character_progression.py:14-142`
**Status**: NON IMPLÉMENTÉ

```tsx
// Composant suggéré: SkillTreeModal.tsx
interface SkillTreeModalProps {
  availableSkills: Skill[];
  learnedSkills: string[];
  skillPoints: number;
  playerLevel: number;
}
```

**Affichage**:

- Arbre visuel avec connexions
- Nœuds grisés si prérequis non remplis
- Tooltips descriptifs au hover
- Bouton "Apprendre" si éligible

---

## Priorité 2 - Notifications & Alertes

### 2.1 Toast Notifications System

**Status**: NON IMPLÉMENTÉ

```tsx
// Types de toasts
type ToastType =
  | "success" // Vert - Action réussie
  | "error" // Rouge - Erreur système
  | "warning" // Orange - Attention requise
  | "info" // Bleu - Information
  | "gold" // Or - Gain de richesse
  | "xp"; // Violet - Gain d'XP
```

**Cas d'utilisation**:

- Pas assez de mana (`combat_engine.py:218`)
- Inventaire plein (`inventory_manager.py:64`)
- Pas assez d'or (`inventory_manager.py:301`)
- Objet équipé/déséquipé
- Quête acceptée/abandonnée

---

### 2.2 Session Timeout Warning

**Fichier**: `parental_control.py:32-35`
**Status**: NON IMPLÉMENTÉ

```tsx
// Composant suggéré: SessionTimeoutModal.tsx
interface SessionTimeoutProps {
  minutesRemaining: number;
  onExtend?: () => void; // Si parent autorise
  onLogout: () => void;
}
```

**Affichage**:

- Countdown visible
- Message adapté ado
- Bouton sauvegarde rapide

---

## Priorité 3 - Interactions Narratives

### 3.1 NPC Dialogue Modal

**Fichier**: `narrative.py:73`
**Status**: NON IMPLÉMENTÉ

```tsx
// Composant suggéré: NPCDialogueModal.tsx
interface NPCDialogueProps {
  npcName: string;
  npcPortrait?: string;
  dialogue: string;
  responses: string[];
  onResponse: (choice: string) => void;
}
```

**Affichage**:

- Portrait PNJ (Paper UI frame)
- Bulle de dialogue stylisée
- Choix de réponses numérotés
- Effet machine à écrire

---

### 3.2 Event Banner

**Fichier**: `narrative.py:116-123`
**Status**: NON IMPLÉMENTÉ

```tsx
// Composant suggéré: EventBanner.tsx
interface EventBannerProps {
  title: string;
  importance: 1 | 2 | 3 | 4 | 5;
  description?: string;
}
```

**Affichage**:

- Banner slide-in depuis le haut
- Couleur selon importance
- Auto-dismiss après 3-5s
- Icône thématique

---

## Priorité 4 - Shop & Commerce

### 4.1 Shop Modal

**Fichier**: `inventory_manager.py:286-325`
**Status**: NON IMPLÉMENTÉ

```tsx
// Composant suggéré: ShopModal.tsx
interface ShopModalProps {
  merchantName: string;
  inventory: ShopItem[];
  playerGold: number;
  onBuy: (itemId: string) => void;
  onSell: (itemId: string) => void;
}
```

**Affichage**:

- Deux colonnes: Marchand | Joueur
- Prix avec icône or
- Boutons Acheter/Vendre
- Confirmation si item cher

---

## Priorité 5 - Améliorations Combat

### 5.1 Turn Transition Animation

**Fichier**: `combat_engine.py:157`
**Status**: NON IMPLÉMENTÉ

```tsx
// Animation entre tours
const TurnTransition = ({ whose }: { whose: "player" | "enemy" }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    exit={{ opacity: 0 }}
  >
    {whose === "player" ? "Votre tour !" : "Tour ennemi..."}
  </motion.div>
);
```

---

### 5.2 Status Effects Display

**Fichier**: `character_progression.py:30-43`
**Status**: NON IMPLÉMENTÉ

```tsx
// Composant suggéré: StatusEffectsBar.tsx
interface StatusEffect {
  id: string;
  name: string;
  icon: string;
  turnsRemaining: number;
  type: "buff" | "debuff";
}
```

**Affichage**:

- Icônes sous la barre de vie
- Tooltip au hover
- Compteur de tours
- Couleur buff (vert) / debuff (rouge)

---

## Priorité 6 - Sons & Musique

### 6.1 Audio Service Enhancement

**Fichier**: `useAudio.ts`
**Status**: PARTIEL (hook existe, peu utilisé)

```tsx
// Sons à implémenter
const SFX_MAP = {
  // Combat
  attack_hit: "/audio/sfx/attack_hit.mp3",
  attack_miss: "/audio/sfx/attack_miss.mp3",
  spell_cast: "/audio/sfx/spell_cast.mp3",
  critical_hit: "/audio/sfx/critical.mp3",

  // UI
  dice_roll: "/audio/sfx/dice_roll.mp3",
  level_up: "/audio/sfx/level_up.mp3",
  gold_gain: "/audio/sfx/coins.mp3",
  item_equip: "/audio/sfx/equip.mp3",

  // Ambiance
  tavern: "/audio/ambiance/tavern.mp3",
  forest: "/audio/ambiance/forest.mp3",
  combat: "/audio/ambiance/combat.mp3",
  city: "/audio/ambiance/city.mp3",
};
```

---

## Assets Paper UI Disponibles

Les sprites suivants sont déjà copiés et utilisables:

```
public/assets/paper-ui/
├── book-desk/     # Fonds bureau (7 variantes)
├── buttons/       # Boutons stylisés
├── dialogue/      # Boîtes dialogue (header, body, footer)
├── headers/       # En-têtes décoratifs (4 styles)
├── hud/           # Interface joueur
├── icons/         # Icônes décoratives
├── items/         # Conteneurs items
├── notification/  # Bulles notification (2 styles)
├── panels/        # Panneaux fond
├── paper/         # Textures parchemin (52 variantes!)
└── progress/      # Barres de progression
```

---

## Estimation Effort

| Priorité               | Composants | Effort estimé |
| ---------------------- | ---------- | ------------- |
| P1 - Modals essentiels | 4          | 2-3 jours     |
| P2 - Notifications     | 2          | 1 jour        |
| P3 - Narratif          | 2          | 1-2 jours     |
| P4 - Shop              | 1          | 1 jour        |
| P5 - Combat            | 2          | 1 jour        |
| P6 - Audio             | 1          | 0.5 jour      |
| **Total**              | **12**     | **6-8 jours** |

---

## Ordre d'Implémentation Suggéré

1. **Toast Notifications** - Base pour feedback utilisateur
2. **Level Up Modal** - Gratification immédiate
3. **Loot Modal** - Fin de combat satisfaisante
4. **Damage Popups** - Combat plus dynamique
5. **NPC Dialogue** - Narration enrichie
6. **Skill Tree** - Progression visible
7. **Shop Modal** - Économie du jeu
8. **Audio SFX** - Immersion finale

---

## Notes Techniques

### WebSocket Events à Écouter

```typescript
// Messages backend déclenchant des modals
type WSMessage =
  | { type: "level_up"; data: LevelUpData }
  | { type: "combat_end"; data: LootData }
  | { type: "quest_complete"; data: QuestRewardData }
  | { type: "error"; message: string }
  | { type: "session_warning"; minutesLeft: number };
```

### Zustand Store Suggéré

```typescript
// Store pour gérer les modals globalement
interface UIStore {
  activeModal: ModalType | null;
  modalData: unknown;
  toasts: Toast[];
  openModal: (type: ModalType, data?: unknown) => void;
  closeModal: () => void;
  addToast: (toast: Toast) => void;
  removeToast: (id: string) => void;
}
```

---

_Document généré le 2025-11-28 - Session Claude Code_
