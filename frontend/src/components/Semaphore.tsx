import React from 'react';
import { cn } from '@/lib/utils';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface SemaphoreProps {
  score: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
}

const Semaphore: React.FC<SemaphoreProps> = ({ score, size = 'md' }) => {
  const getLevel = () => {
    if (score < 30) return { color: 'text-risk-green', bg: 'bg-risk-green/10', border: 'border-risk-green/30', icon: CheckCircle, label: 'Bajo Riesgo' };
    if (score < 70) return { color: 'text-risk-yellow', bg: 'bg-risk-yellow/10', border: 'border-risk-yellow/30', icon: AlertTriangle, label: 'Sospechoso' };
    return { color: 'text-risk-red', bg: 'bg-risk-red/10', border: 'border-risk-red/30', icon: XCircle, label: 'Alto Riesgo' };
  };

  const level = getLevel();
  const Icon = level.icon;

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs gap-1',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-6 py-3 text-lg gap-3 font-bold',
  };

  return (
    <div className={cn(
      "inline-flex items-center rounded-full border transition-all",
      level.bg,
      level.border,
      level.color,
      sizeClasses[size]
    )}>
      <Icon className={cn(size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-6 h-6')} />
      <span>{level.label}</span>
      <span className="opacity-70 font-mono">({score}%)</span>
    </div>
  );
};

export default Semaphore;
