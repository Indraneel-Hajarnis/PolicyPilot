import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';

export default function SourceCitation({ source, index }) {
  const [expanded, setExpanded] = useState(false);
  const { t } = useLanguage();

  // Backend sends: { score, text, page, document_id, chunk_index }
  const scorePercent =
    source.score != null && !isNaN(source.score)
      ? `${(source.score * 100).toFixed(0)}%`
      : null;

  const locationLabel =
    source.page != null
      ? `Page ${source.page}`
      : source.chunk_index != null
      ? `Chunk ${source.chunk_index + 1}`
      : `Source ${(index ?? 0) + 1}`;

  // Short preview of chunk text shown in collapsed header
  const preview = source.text
    ? source.text.slice(0, 90).trim() + (source.text.length > 90 ? '…' : '')
    : 'No preview available';

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden text-xs transition-all hover:border-teal-500/30">
      {/* Collapsed header — always visible */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between px-3.5 py-2.5 cursor-pointer bg-slate-800/40 hover:bg-white/10 transition-colors"
      >
        <div className="flex items-center gap-2 text-white/90 font-medium min-w-0">
          <FileText className="w-3.5 h-3.5 text-teal-400 shrink-0" />
          <span className="px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 text-[10px] shrink-0">
            {locationLabel}
          </span>
          <span className="truncate text-white/60 italic">{preview}</span>
        </div>
        <div className="flex items-center gap-2 shrink-0 ml-2">
          {scorePercent && (
            <span className="text-white/50 text-[11px] font-mono">
              {scorePercent}
            </span>
          )}
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-white/50" />
          ) : (
            <ChevronDown className="w-4 h-4 text-white/50" />
          )}
        </div>
      </div>

      {/* Expanded detail panel */}
      {expanded && (
        <div className="p-3 bg-black/20 border-t border-white/5 space-y-2">
          <p className="text-white/75 font-mono leading-relaxed bg-white/5 p-2.5 rounded-lg border border-white/5 whitespace-pre-wrap text-[11px]">
            {source.text || 'No text available.'}
          </p>
          {source.document_id && (
            <div className="flex justify-end pt-1">
              <Link
                to={`/documents/${source.document_id}`}
                className="inline-flex items-center gap-1 text-teal-400 hover:text-teal-300 transition-colors font-medium text-[11px]"
              >
                View Full Document <ExternalLink className="w-3 h-3" />
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
