import { create } from 'zustand';
import type { Character, NarrativeResponse } from '../types/game';

interface GameState {
  playerId: string;
  character: Character | null;
  narrative: NarrativeResponse | null;
  isLoading: boolean;
  setPlayerId: (playerId: string) => void;
  setCharacter: (character: Character) => void;
  setNarrative: (narrative: NarrativeResponse) => void;
  setLoading: (loading: boolean) => void;
}

export const useGameState = create<GameState>((set) => ({
  playerId: `player_${Date.now()}`,
  character: null,
  narrative: null,
  isLoading: false,
  setPlayerId: (playerId) => set({ playerId }),
  setCharacter: (character) => set({ character }),
  setNarrative: (narrative) => set({ narrative }),
  setLoading: (loading) => set({ isLoading: loading }),
}));