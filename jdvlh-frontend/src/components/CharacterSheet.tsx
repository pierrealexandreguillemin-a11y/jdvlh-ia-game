import type { Character } from '../types/game';

interface CharacterSheetProps {
  character: Character;
  compact?: boolean;
}

interface StatBarProps {
  label: string;
  current: number;
  max: number;
  color: 'red' | 'blue' | 'gold';
}

function StatBar({ label, current, max, color }: StatBarProps) {
  const percentage = Math.min(100, (current / max) * 100);
  const colorClasses = {
    red: 'bg-red-600',
    blue: 'bg-blue-600',
    gold: 'bg-amber-500',
  };

  return (
    <div className="mb-2">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-amber-800 font-medium">{label}</span>
        <span className="text-amber-700">
          {current}/{max}
        </span>
      </div>
      <div className="h-3 bg-amber-200/50 rounded-full border border-amber-700/30 overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

interface StatDisplayProps {
  label: string;
  value: number;
  modifier?: number;
}

function StatDisplay({ label, value, modifier }: StatDisplayProps) {
  const mod = modifier ?? Math.floor((value - 10) / 2);
  const modStr = mod >= 0 ? `+${mod}` : `${mod}`;

  return (
    <div className="text-center p-2 bg-amber-100/50 rounded border border-amber-600/30">
      <div className="text-xs text-amber-700 uppercase tracking-wide">
        {label}
      </div>
      <div className="text-2xl font-bold text-amber-900">{value}</div>
      <div className="text-sm text-amber-600">({modStr})</div>
    </div>
  );
}

/**
 * CharacterSheet - Display character information
 * Paper UI styled character panel
 */
export function CharacterSheet({ character, compact = false }: CharacterSheetProps) {
  const { name, race, class: charClass, level, stats } = character;

  if (compact) {
    return (
      <div className="panel-paper p-3">
        {/* Compact Header */}
        <div className="flex items-center gap-3 mb-3">
          <div
            className="w-12 h-12 rounded-full border-2 border-amber-700 bg-amber-200 flex items-center justify-center"
            style={{
              backgroundImage: "url('/assets/paper-ui/icons/1.png')",
              backgroundSize: 'cover',
            }}
          >
            <span className="text-xl font-bold text-amber-800">
              {name.charAt(0)}
            </span>
          </div>
          <div>
            <div className="font-bold text-amber-900">{name}</div>
            <div className="text-sm text-amber-700">
              {race} {charClass} Niv.{level}
            </div>
          </div>
        </div>

        {/* Compact Bars */}
        <StatBar label="PV" current={stats.hp} max={stats.maxHp} color="red" />
        <StatBar label="PM" current={stats.mp} max={stats.maxMp} color="blue" />
        <StatBar label="XP" current={stats.xp} max={stats.xpToNext} color="gold" />
      </div>
    );
  }

  return (
    <div
      className="panel-paper"
      style={{
        backgroundImage: "url('/assets/paper-ui/book-desk/1.png')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Header */}
      <div className="text-center mb-4 pb-3 border-b-2 border-amber-700/30">
        <h2 className="text-2xl font-bold text-amber-900 mb-1">{name}</h2>
        <div className="text-amber-700">
          {race} {charClass} - Niveau {level}
        </div>
      </div>

      {/* Vitals */}
      <div className="mb-6">
        <h3 className="text-sm font-bold text-amber-800 mb-2 uppercase tracking-wide">
          Vitalité
        </h3>
        <StatBar label="Points de Vie" current={stats.hp} max={stats.maxHp} color="red" />
        <StatBar label="Points de Magie" current={stats.mp} max={stats.maxMp} color="blue" />
        <StatBar label="Expérience" current={stats.xp} max={stats.xpToNext} color="gold" />
      </div>

      {/* Stats Grid */}
      <div className="mb-4">
        <h3 className="text-sm font-bold text-amber-800 mb-2 uppercase tracking-wide">
          Caractéristiques
        </h3>
        <div className="grid grid-cols-3 gap-2">
          <StatDisplay label="FOR" value={stats.strength} />
          <StatDisplay label="DEX" value={stats.dexterity} />
          <StatDisplay label="CON" value={stats.constitution} />
          <StatDisplay label="INT" value={stats.intelligence} />
          <StatDisplay label="SAG" value={stats.wisdom} />
          <StatDisplay label="CHA" value={stats.charisma} />
        </div>
      </div>

      {/* Equipment Preview */}
      {character.equipment && (
        <div>
          <h3 className="text-sm font-bold text-amber-800 mb-2 uppercase tracking-wide">
            Équipement
          </h3>
          <div className="space-y-1 text-sm">
            {character.equipment.weapon && (
              <div className="flex items-center gap-2">
                <span className="text-amber-600">⚔️</span>
                <span className="text-amber-800">{character.equipment.weapon.name}</span>
              </div>
            )}
            {character.equipment.armor && (
              <div className="flex items-center gap-2">
                <span className="text-amber-600">🛡️</span>
                <span className="text-amber-800">{character.equipment.armor.name}</span>
              </div>
            )}
            {character.equipment.accessory && (
              <div className="flex items-center gap-2">
                <span className="text-amber-600">💍</span>
                <span className="text-amber-800">{character.equipment.accessory.name}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default CharacterSheet;
