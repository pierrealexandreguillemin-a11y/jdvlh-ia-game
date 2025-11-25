import { useState, useEffect, useRef } from 'react';

interface StoryDisplayProps {
  narrative: string;
  choices: string[];
  location: string;
  isLoading: boolean;
  onChoiceSelect: (choice: string) => void;
}

/**
 * StoryDisplay - Main narrative display component
 * Styled with Paper UI medieval/parchment theme
 */
export function StoryDisplay({
  narrative,
  choices,
  location,
  isLoading,
  onChoiceSelect,
}: StoryDisplayProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const textRef = useRef<HTMLDivElement>(null);

  // Typewriter effect for narrative
  useEffect(() => {
    if (!narrative) return;

    setIsTyping(true);
    setDisplayedText('');
    let index = 0;

    const timer = setInterval(() => {
      if (index < narrative.length) {
        setDisplayedText(narrative.slice(0, index + 1));
        index++;
      } else {
        setIsTyping(false);
        clearInterval(timer);
      }
    }, 30); // Typing speed

    return () => clearInterval(timer);
  }, [narrative]);

  // Auto-scroll as text appears
  useEffect(() => {
    if (textRef.current) {
      textRef.current.scrollTop = textRef.current.scrollHeight;
    }
  }, [displayedText]);

  // Skip typing animation on click
  const handleSkipTyping = () => {
    if (isTyping) {
      setDisplayedText(narrative);
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Location Header */}
      <div className="relative mb-4">
        <div
          className="bg-cover bg-center h-12 flex items-center justify-center"
          style={{
            backgroundImage: "url('/assets/paper-ui/dialogue/1.png')",
            backgroundSize: '100% 100%',
          }}
        >
          <span className="text-lg font-bold tracking-wide text-amber-900">
            {location || 'Terre du Milieu'}
          </span>
        </div>
      </div>

      {/* Main Narrative Panel */}
      <div
        className="flex-1 relative cursor-pointer"
        onClick={handleSkipTyping}
      >
        {/* Paper background */}
        <div
          className="absolute inset-0 bg-cover"
          style={{
            backgroundImage: "url('/assets/paper-ui/dialogue/2.png')",
            backgroundSize: '100% 100%',
          }}
        />

        {/* Narrative text */}
        <div
          ref={textRef}
          className="relative z-10 p-6 h-64 overflow-y-auto text-lg leading-relaxed"
          style={{ color: 'var(--paper-text)' }}
        >
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-pulse text-amber-700">
                Le destin s'écrit...
              </div>
            </div>
          ) : (
            <>
              <p className="whitespace-pre-wrap">{displayedText}</p>
              {isTyping && (
                <span className="inline-block w-2 h-5 bg-amber-800 animate-pulse ml-1" />
              )}
            </>
          )}
        </div>

        {/* Click to skip hint */}
        {isTyping && (
          <div className="absolute bottom-2 right-4 text-xs text-amber-600 opacity-60">
            Cliquez pour passer
          </div>
        )}
      </div>

      {/* Choices Panel */}
      {!isTyping && choices.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="text-sm text-amber-700 mb-2 font-semibold">
            Que faites-vous ?
          </div>
          {choices.map((choice, index) => (
            <button
              key={index}
              onClick={() => onChoiceSelect(choice)}
              disabled={isLoading}
              className="w-full text-left px-4 py-3 transition-all duration-200
                         bg-amber-100/80 hover:bg-amber-200/90
                         border-2 border-amber-700/50 hover:border-amber-600
                         rounded shadow-md hover:shadow-lg
                         disabled:opacity-50 disabled:cursor-not-allowed
                         flex items-center gap-3"
              style={{
                backgroundImage: "url('/assets/paper-ui/buttons/1.png')",
                backgroundSize: '100% 100%',
              }}
            >
              <span className="text-amber-800 font-bold">{index + 1}.</span>
              <span className="text-amber-900">{choice}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default StoryDisplay;
