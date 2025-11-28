import React from 'react';
import { motion } from 'framer-motion';

const ActionButtons: React.FC = () => {
  const actions = [
    { id: 'attack', label: 'Attaquer', icon: '⚔️', color: 'from-red-500 to-red-600' },
    { id: 'defend', label: 'Défendre', icon: '🛡️', color: 'from-blue-500 to-blue-600' },
    { id: 'magic', label: 'Sort', icon: '✨', color: 'from-purple-500 to-purple-600' },
    { id: 'item', label: 'Objet', icon: '🧪', color: 'from-green-500 to-green-600' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4">
      {actions.map((action) => (
        <motion.button
          key={action.id}
          className={`p-6 rounded-2xl font-bold text-xl shadow-2xl hover:shadow-3xl active:scale-95 transition-all border-4 bg-gradient-to-r ${action.color} text-white relative overflow-hidden`}
          whileHover={{ y: -4 }}
          whileTap={{ scale: 0.98 }}
        >
          <span className="relative z-10">{action.icon}</span>
          <span className="block text-sm mt-1 relative z-10">{action.label}</span>
          <div className="absolute inset-0 bg-white/20 animate-pulse rounded-2xl"></div>
        </motion.button>
      ))}
    </div>
  );
};

export default ActionButtons;