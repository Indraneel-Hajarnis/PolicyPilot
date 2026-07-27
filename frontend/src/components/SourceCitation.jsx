import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';

export default function SourceCitation({ source }) {
  const { t } = useLanguage();
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden text-xs transition-all hover:border-teal-500/30">
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between px-3.5 py-2.5 cursor-pointer bg-surface-800/40 hover:bg-white/10 transition-colors"
      >
        <div className="flex items-center gap-2 text-white/90 font-medium truncate">
          <FileText className="w-3.5 h-3.5 text-teal-400 shrink-0" />
          <span className="truncate">{source.document_name}</span>
          <span className="px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 text-[10px]">
            {t('pageLabel')} {source.page_number}
          </span>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-white/40 text-[11px]">
            {t('scoreLabel')} {(source.similarity_score * 100).toFixed(0)}%
          </span>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-white/50" />
          ) : (
            <ChevronDown className="w-4 h-4 text-white/50" />
          )}
        </div>
      </div>

      {expanded && (
        <div className="p-3 bg-black/20 border-t border-white/5 space-y-2">
          <p className="text-white/70 italic font-mono leading-relaxed bg-white/5 p-2.5 rounded-lg border border-white/5">
            "{source.chunk_text}"
          </p>
          <div className="flex justify-end pt-1">
            <Link
              to={`/documents/${source.document_id}`}
              className="inline-flex items-center gap-1 text-teal-400 hover:text-teal-300 transition-colors font-medium text-[11px]"
            >
              {t('viewFullDoc')} <ExternalLink className="w-3 h-3" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
