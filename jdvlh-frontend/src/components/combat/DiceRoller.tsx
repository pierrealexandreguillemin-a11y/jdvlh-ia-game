import { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface DiceRollerProps {
  skill: string;
  dc: number;
  modifier: number;
  onRoll: (total: number, success: boolean) => void;
}

const skillLabels: Record<string, string> = {
  perception: 'Perception',
  stealth: 'Discrétion',
  athletics: 'Athlétisme',
  acrobatics: 'Acrobaties',
  arcana: 'Arcanes',
  diplomacy: 'Diplomatie',
  intimidation: 'Intimidation',
  deception: 'Tromperie',
  nature: 'Nature',
  religion: 'Religion',
  society: 'Société',
  thievery: 'Vol',
  medicine: 'Médecine',
  survival: 'Survie',
  crafting: 'Artisanat',
  performance: 'Représentation',
  occultism: 'Occultisme',
};

/**
 * DiceRoller - Interactive d20 roller for Pathfinder 2e skill checks
 * Player clicks to roll the dice on screen
 */
export function DiceRoller({ skill, dc, modifier, onRoll }: DiceRollerProps) {
  const [isRolling, setIsRolling] = useState(false);
  const [diceValue, setDiceValue] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);

  const skillName = skillLabels[skill.toLowerCase()] || skill;
  const modStr = modifier >= 0 ? `+${modifier}` : `${modifier}`;

  const rollDice = useCallback(() => {
    if (isRolling) return;

    setIsRolling(true);
    setShowResult(false);

    // Animate dice rolling
    let rollCount = 0;
    const maxRolls = 15;

    const rollInterval = setInterval(() => {
      setDiceValue(Math.floor(Math.random() * 20) + 1);
      rollCount++;

      if (rollCount >= maxRolls) {
        clearInterval(rollInterval);

        // Final result
        const finalRoll = Math.floor(Math.random() * 20) + 1;
        const total = finalRoll + modifier;
        const success = total >= dc;

        setDiceValue(finalRoll);
        setIsRolling(false);
        setShowResult(true);

        // Delay before calling onRoll to show result
        setTimeout(() => {
          onRoll(total, success);
        }, 2000);
      }
    }, 80);
  }, [isRolling, modifier, dc, onRoll]);

  // Handle keyboard
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === 'Space' || e.code === 'Enter') {
        e.preventDefault();
        rollDice();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [rollDice]);

  const total = diceValue !== null ? diceValue + modifier : null;
  const isSuccess = total !== null && total >= dc;
  const isCritSuccess = diceValue === 20;
  const isCritFail = diceValue === 1;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-amber-100 rounded-lg p-8 max-w-md w-full mx-4 shadow-2xl border-4 border-amber-800"
        style={{
          backgroundImage: "url('/assets/paper-ui/dialogue/2.png')",
          backgroundSize: 'cover',
        }}
      >
        {/* Header */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-amber-900 mb-2">
            Jet de {skillName}
          </h2>
          <div className="text-amber-700">
            DC {dc} | Modificateur: {modStr}
          </div>
        </div>

        {/* Dice Display */}
        <div className="flex justify-center mb-6">
          <motion.button
            onClick={rollDice}
            disabled={isRolling || showResult}
            className={`
              relative w-32 h-32 rounded-lg
              flex items-center justify-center
              text-5xl font-bold
              transition-all duration-200
              ${isRolling ? 'cursor-wait' : showResult ? 'cursor-default' : 'cursor-pointer hover:scale-105'}
              ${isCritSuccess ? 'bg-green-600 text-white' :
                isCritFail ? 'bg-red-600 text-white' :
                'bg-amber-800 text-amber-100'}
              shadow-lg
            `}
            animate={isRolling ? {
              rotate: [0, 15, -15, 10, -10, 5, -5, 0],
              scale: [1, 1.1, 0.95, 1.05, 1],
            } : {}}
            transition={{ duration: 0.3, repeat: isRolling ? Infinity : 0 }}
          >
            {/* D20 shape outline */}
            <div className="absolute inset-2 border-2 border-amber-300/30 rotate-45" />
            <div className="absolute inset-2 border-2 border-amber-300/30 -rotate-45" />

            <span className="relative z-10">
              {diceValue !== null ? diceValue : '?'}
            </span>

            {/* Critical indicators */}
            {showResult && isCritSuccess && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded"
              >
                CRIT!
              </motion.div>
            )}
            {showResult && isCritFail && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-2 -right-2 bg-red-400 text-red-900 text-xs font-bold px-2 py-1 rounded"
              >
                FUMBLE!
              </motion.div>
            )}
          </motion.button>
        </div>

        {/* Result Display */}
        <AnimatePresence>
          {showResult && total !== null && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center"
            >
              {/* Calculation breakdown */}
              <div className="text-amber-700 mb-3">
                {diceValue} {modifier >= 0 ? '+' : ''} {modifier} = <span className="text-2xl font-bold text-amber-900">{total}</span>
              </div>

              {/* Success/Failure */}
              <div className={`text-2xl font-bold ${isSuccess ? 'text-green-600' : 'text-red-600'}`}>
                {isCritSuccess ? 'Succès Critique !' :
                 isCritFail ? 'Échec Critique !' :
                 isSuccess ? 'Succès !' : 'Échec...'}
              </div>

              <div className="mt-4 text-sm text-amber-600">
                Résultat appliqué dans 2 secondes...
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Instructions */}
        {!showResult && (
          <div className="text-center text-amber-700">
            {isRolling ? (
              <span className="animate-pulse">Le dé roule...</span>
            ) : (
              <span>Cliquez sur le dé ou appuyez sur [Espace] pour lancer</span>
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default DiceRoller;
