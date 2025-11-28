import React from 'react';

const QuestLog: React.FC = () => {
  const quests = [
    { id: '1', title: 'Sauver la Comté', status: 'active' as const },
    { id: '2', title: 'Trouver l\'Anneau', status: 'completed' as const },
  ];

  return (
    <div className="bg-slate-800/90 p-6 rounded-2xl shadow-xl border border-amber-500/30 max-h-96 overflow-y-auto">
      <h3 className="text-2xl font-bold text-amber-400 mb-6 text-center">📜 Journal de Quêtes</h3>
      <ul className="space-y-3">
        {quests.map((quest) => (
          <li key={quest.id} className="p-4 rounded-xl border-l-4 transition-all hover:bg-slate-700/50">
            <div className="font-bold text-lg mb-1">
              {quest.title}
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              quest.status === 'active' 
                ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50' 
                : 'bg-green-500/20 text-green-300 border-green-500/50'
            } border`}>
              {quest.status === 'active' ? 'En cours' : 'Terminée'}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default QuestLog;