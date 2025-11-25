/**
 * Game Types for JDVLH Frontend
 */

export interface Character {
  name: string;
  race: string;
  class: string;
  level: number;
  stats: CharacterStats;
  inventory: InventoryItem[];
  equipment: Equipment;
}

export interface CharacterStats {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  hp: number;
  maxHp: number;
  mp: number;
  maxMp: number;
  xp: number;
  xpToNext: number;
}

export interface InventoryItem {
  id: string;
  name: string;
  description: string;
  type: 'weapon' | 'armor' | 'consumable' | 'quest' | 'misc';
  quantity: number;
  icon?: string;
}

export interface Equipment {
  weapon?: InventoryItem;
  armor?: InventoryItem;
  accessory?: InventoryItem;
}

export interface NarrativeResponse {
  narrative: string;
  choices: string[];
  location: string;
  animation_trigger?: string;
  sfx?: string;
  content_filtered?: boolean;
}

export interface GameState {
  character: Character | null;
  currentNarrative: NarrativeResponse | null;
  history: string[];
  location: string;
  isLoading: boolean;
  error: string | null;
}

export interface Quest {
  id: string;
  title: string;
  description: string;
  status: 'available' | 'active' | 'completed' | 'failed';
  objectives: QuestObjective[];
  rewards?: QuestReward[];
}

export interface QuestObjective {
  id: string;
  description: string;
  completed: boolean;
  progress?: number;
  target?: number;
}

export interface QuestReward {
  type: 'xp' | 'gold' | 'item';
  amount?: number;
  item?: InventoryItem;
}

export interface CombatState {
  inCombat: boolean;
  enemies: Enemy[];
  turn: 'player' | 'enemy';
  round: number;
}

export interface Enemy {
  id: string;
  name: string;
  hp: number;
  maxHp: number;
  damage: number;
  icon?: string;
}
