import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

export default function ConfidenceBadge({ confidence = 0 }) {
  const percent = Math.round(confidence * 100);

  let badgeStyle = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
  let Icon = CheckCircle2;
  let label = 'High Confidence';

  if (confidence < 0.5) {
    badgeStyle = 'bg-rose-500/20 text-rose-300 border-rose-500/30';
    Icon = XCircle;
    label = 'Low Confidence';
  } else if (confidence < 0.8) {
    badgeStyle = 'bg-amber-500/20 text-amber-300 border-amber-500/30';
    Icon = AlertTriangle;
    label = 'Medium Confidence';
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${badgeStyle} backdrop-blur-md shadow-sm transition-all hover:scale-105`}
      title={`Confidence Score: ${percent}% based on semantic context match`}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{label} ({percent}%)</span>
    </div>
  );
}
