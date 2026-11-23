'use client';

interface ClassificationBadgeProps {
  classification: string;
  size?: 'sm' | 'md' | 'lg';
}

const classStyles: Record<string, { bg: string; text: string; label: string }> = {
  human_like: { bg: 'bg-forest/10', text: 'text-forest', label: 'HUMAN-LIKE' },
  automated_like: { bg: 'bg-accent-red/10', text: 'text-accent-red', label: 'AUTOMATED' },
  suspicious: { bg: 'bg-accent-amber/10', text: 'text-accent-amber', label: 'SUSPICIOUS' },
  inconclusive: { bg: 'bg-warm-muted/10', text: 'text-warm-muted', label: 'INCONCLUSIVE' },
};

export default function ClassificationBadge({ classification, size = 'md' }: ClassificationBadgeProps) {
  const style = classStyles[classification] || classStyles.inconclusive;
  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-[10px] px-3 py-1',
    lg: 'text-xs px-4 py-1.5',
  };

  return (
    <span className={`inline-flex items-center font-mono font-semibold tracking-wide ${style.bg} ${style.text} ${sizeClasses[size]}`}>
      {style.label}
    </span>
  );
}
