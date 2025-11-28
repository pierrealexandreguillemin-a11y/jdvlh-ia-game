import { useCallback } from 'react';
import { AudioManager } from '../services/audio';

export const useAudio = () => {
  const audio = AudioManager.getInstance();

  const playAmbiance = useCallback((location: string) => {
    audio.playAmbiance(location);
  }, [audio]);

  const playSFX = useCallback((action: string) => {
    audio.playSFX(action);
  }, [audio]);

  const stopBGM = useCallback(() => {
    audio.stopBGM();
  }, [audio]);

  const stopAll = useCallback(() => {
    audio.stopAll();
  }, [audio]);

  return { playAmbiance, playSFX, stopBGM, stopAll };
};