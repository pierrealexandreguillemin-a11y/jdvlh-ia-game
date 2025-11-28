import React from 'react';

interface ContentFilterDisplayProps {
  filterResult?: {
    is_safe: boolean;
    severity: string;
    violation_count: number;
    categories: string[];
  };
}

const ContentFilterDisplay: React.FC<ContentFilterDisplayProps> = ({ filterResult }) => {
  if (!filterResult || filterResult.is_safe) {
    return null;
  }

  return (
    <div className="bg-amber-100 border-l-4 border-amber-500 p-3 rounded text-sm">
      <div className="flex items-center gap-2">
        <span className="text-amber-600">⚠️</span>
        <span className="text-amber-800 font-medium">
          Contenu filtré ({filterResult.severity})
        </span>
      </div>
      {filterResult.categories.length > 0 && (
        <div className="mt-1 text-amber-700 text-xs">
          Catégories: {filterResult.categories.join(', ')}
        </div>
      )}
    </div>
  );
};

export default ContentFilterDisplay;
export { ContentFilterDisplay };
