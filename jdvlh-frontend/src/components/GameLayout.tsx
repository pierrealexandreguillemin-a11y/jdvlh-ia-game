import type { ReactNode } from 'react';

interface GameLayoutProps {
  children: ReactNode;
  sidebar?: ReactNode;
  header?: ReactNode;
}

/**
 * GameLayout - Main game layout with medieval book desk style
 */
export function GameLayout({ children, sidebar, header }: GameLayoutProps) {
  return (
    <div
      className="min-h-screen bg-amber-900"
      style={{
        backgroundImage: "url('/assets/paper-ui/book-desk/2.png')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
      }}
    >
      {/* Header */}
      {header && (
        <header className="bg-amber-950/80 backdrop-blur-sm border-b-2 border-amber-700/50 p-4">
          {header}
        </header>
      )}

      {/* Main Content Area */}
      <div className="container mx-auto p-4 flex gap-4 min-h-[calc(100vh-80px)]">
        {/* Main Story Area */}
        <main className="flex-1">
          <div
            className="h-full rounded-lg shadow-2xl p-6"
            style={{
              backgroundColor: 'rgba(244, 228, 188, 0.95)',
              borderImage: 'url(/assets/paper-ui/dialogue/3.png) 30 round',
              borderWidth: '8px',
              borderStyle: 'solid',
            }}
          >
            {children}
          </div>
        </main>

        {/* Sidebar (Character Sheet, etc.) */}
        {sidebar && (
          <aside className="w-80 flex-shrink-0">
            <div className="sticky top-4">{sidebar}</div>
          </aside>
        )}
      </div>
    </div>
  );
}

export default GameLayout;
