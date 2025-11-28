import React from 'react';

interface PaperCardProps {
  title?: string;
  variant?: 'parchment' | 'book-desk' | 'large-parchment';
  children: React.ReactNode;
  className?: string;
}

const PaperCard: React.FC<PaperCardProps> = ({ title, variant = 'parchment', children, className = '' }) => {
  const variantStyles = {
    parchment: 'from-amber-100 to-amber-200 border-amber-700/30',
    'book-desk': 'from-slate-800/95 to-slate-900/95 border-slate-500/30',
    'large-parchment': 'from-amber-50 to-amber-100 border-amber-600/40',
  };

  return (
    <div className={`bg-gradient-to-br ${variantStyles[variant]} backdrop-blur-xl rounded-3xl shadow-2xl border p-8 ${className}`}>
      {title && (
        <h3 className="text-2xl font-bold text-amber-900 mb-6 pb-4 border-b-2 border-amber-500/30">
          {title}
        </h3>
      )}
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
};

export default PaperCard;
export { PaperCard };