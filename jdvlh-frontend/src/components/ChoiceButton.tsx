import type { ButtonHTMLAttributes } from 'react';

interface ChoiceButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

/**
 * ChoiceButton - Medieval styled button component
 */
export function ChoiceButton({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled,
  ...props
}: ChoiceButtonProps) {
  const baseClasses = `
    relative overflow-hidden
    font-medium tracking-wide
    border-2 rounded
    transition-all duration-200
    disabled:opacity-50 disabled:cursor-not-allowed
    active:scale-95
  `;

  const variantClasses = {
    primary: `
      bg-amber-100 hover:bg-amber-200
      border-amber-700 hover:border-amber-600
      text-amber-900
      shadow-md hover:shadow-lg
    `,
    secondary: `
      bg-stone-100 hover:bg-stone-200
      border-stone-600 hover:border-stone-500
      text-stone-800
      shadow-sm hover:shadow-md
    `,
    danger: `
      bg-red-100 hover:bg-red-200
      border-red-700 hover:border-red-600
      text-red-900
      shadow-md hover:shadow-lg
    `,
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {/* Paper texture overlay */}
      <div
        className="absolute inset-0 opacity-10 pointer-events-none"
        style={{
          backgroundImage: "url('/assets/paper-ui/buttons/1.png')",
          backgroundSize: 'cover',
        }}
      />
      <span className="relative z-10">{children}</span>
    </button>
  );
}

export default ChoiceButton;
