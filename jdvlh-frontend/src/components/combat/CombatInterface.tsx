import React from 'react';
import { motion } from 'framer-motion';
import { useGameState } from '../../stores/useGameState';

const CombatInterface: React.FC = () => {
  const { character } = useGameState();

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 bg-gradient-to-b from-red-900/90 to-slate-900 rounded-2xl shadow-2xl border-4 border-red-500/50 relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-orange-500/10 animate-pulse"></div>
      <h2 className="text-3xl font-bold text-red-400 mb-8 text-center relative z-10 drop-shadow-lg">
        ⚔️ Interface Combat Tactique
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
        <motion.div 
          className="p-8 bg-red-800/70 backdrop-blur-sm rounded-xl text-center border-2 border-red-400/50"
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring' }}
        >
          <h3 className="text-xl font-bold text-red-300 mb-6">Ennemis</h3>
          <div className="space-y-4">
            <div className="bg-red-600/80 w-full h-10 rounded-full overflow-hidden">
              <motion.div 
                className="bg-green-400 h-10 rounded-full"
                initial={{ width: '100%' }}
                animate={{ width: '75%' }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>
            <span className="text-sm text-gray-200 block">Gobelin (7/7 HP)</span>
          </div>
        </motion.div>
        <motion.div 
          className="p-8 bg-green-800/70 backdrop-blur-sm rounded-xl text-center border-2 border-green-400/50"
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring' }}
        >
          <h3 className="text-xl font-bold text-green-300 mb-6">{character?.name || 'Héros'}</h3>
          <div className="bg-green-600/80 w-full h-10 rounded-full overflow-hidden">
            <motion.div 
              className="bg-green-400 h-10 rounded-full"
              initial={{ width: '100%' }}
              animate={{ width: '100%' }}
            />
          </div>
          <span className="text-sm text-gray-200 block">24/24 HP</span>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default CombatInterface;