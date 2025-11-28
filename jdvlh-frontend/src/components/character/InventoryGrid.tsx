import React from 'react';

const InventoryGrid: React.FC = () => {
  return (
    <div className="grid grid-cols-4 gap-4 p-6 bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl shadow-2xl border border-amber-500/30">
      <div className="p-4 bg-amber-100/80 backdrop-blur-sm rounded-lg shadow-md hover:shadow-xl transition-all cursor-grab border-2 border-amber-200/50 active:scale-95">
        🗡️ Épée
      </div>
      <div className="p-4 bg-blue-100/80 backdrop-blur-sm rounded-lg shadow-md hover:shadow-xl transition-all cursor-grab border-2 border-blue-200/50 active:scale-95">
        🧪 Potion
      </div>
      <div className="p-4 bg-green-100/80 backdrop-blur-sm rounded-lg shadow-md hover:shadow-xl transition-all cursor-grab border-2 border-green-200/50 active:scale-95">
        🛡️ Armure
      </div>
      <div className="p-4 bg-purple-100/80 backdrop-blur-sm rounded-lg shadow-md hover:shadow-xl transition-all cursor-grab border-2 border-purple-200/50 active:scale-95">
        💍 Anneau
      </div>
    </div>
  );
};

export default InventoryGrid;