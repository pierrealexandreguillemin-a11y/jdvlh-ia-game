import { Howl } from 'howler';

export class AudioManager {
  private static instance: AudioManager;
  private bgm: Howl | null = null;
  private sfxCache: Map<string, Howl> = new Map();

  private constructor() {}

  static getInstance(): AudioManager {
    if (!AudioManager.instance) {
      AudioManager.instance = new AudioManager();
    }
    return AudioManager.instance;
  }

  playAmbiance(location: string): void {
    // Stop current BGM
    this.bgm?.stop();

    const tracks: Record<string, string[]> = {
      shire: ['/audio/peaceful_shire.mp3'],
      moria: ['/audio/dark_caves.mp3'],
      rivendell: ['/audio/elven_realm.mp3'],
      // Add more
      default: ['/audio/ambient_default.mp3'],
    };

    const src = tracks[location] || tracks.default;
    this.bgm = new Howl({
      src,
      loop: true,
      volume: 0.3,
      preload: true,
    });
    this.bgm.play();
  }

  playSFX(action: string): void {
    const sounds: Record<string, string[]> = {
      choice_click: ['/audio/paper_rustle.mp3'],
      attack: ['/audio/sword_swing.mp3'],
      spell_cast: ['/audio/spell_cast.mp3'],
      level_up: ['/audio/fanfare.mp3'],
      footsteps: ['/audio/footsteps.mp3'],
      // Add more
      default: ['/audio/click_default.mp3'],
    };

    const src = sounds[action] || sounds.default;
    const soundKey = `sfx_${action}`;

    if (!this.sfxCache.has(soundKey)) {
      this.sfxCache.set(soundKey, new Howl({ src }));
    }

    const sound = this.sfxCache.get(soundKey)!;
    sound.play();
  }

  stopBGM(): void {
    this.bgm?.stop();
  }

  stopAll(): void {
    this.bgm?.stop();
    this.sfxCache.forEach(sound => sound.stop());
    this.sfxCache.clear();
  }

  setVolume(volume: number): void {
    this.bgm?.volume(volume);
    this.sfxCache.forEach(sound => sound.volume(volume));
  }
}