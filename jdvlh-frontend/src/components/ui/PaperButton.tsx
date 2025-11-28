import React from 'react';
import { motion } from 'framer-motion';

interface PaperButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

const PaperButton: React.FC<PaperButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'md',
  disabled = false,
}) => {
  const baseClasses = 'relative overflow-hidden font-bold uppercase tracking-wide shadow-2xl border-4 rounded-2xl transition-all duration-200 active:scale-95 focus:outline-none focus:ring-4';
  const variants = {
    primary: 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 border-amber-400 text-slate-900 shadow-amber-400/50',
    secondary: 'bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-800 hover:to-slate-700 border-slate-500 text-amber-200 shadow-slate-500/50',
    danger: 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 border-red-400 text-white shadow-red-400/50',
  };
  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      type={type}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      onClick={onClick}
      disabled={disabled}
      whileHover={!disabled ? { y: -2, boxShadow: '0 20px 40px rgba(0,0,0,0.3)' } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
    >
      <div className="absolute inset-0 bg-white/20 -skew-x-12 -skew-y-6 transform rotate-[-5deg] animate-pulse opacity-0 group-hover:opacity-100 transition-opacity"></div>
      <span className="relative">{children}</span>
    </motion.button>
  );
};

export default PaperButton;
export { PaperButton };