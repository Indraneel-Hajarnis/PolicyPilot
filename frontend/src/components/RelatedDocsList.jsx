import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, ArrowRight, Sparkles } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function RelatedDocsList({ docs = [] }) {
  const { t } = useLanguage();

  if (!docs || docs.length === 0) return null;

  return (
    <div className="space-y-3 pt-4 border-t border-white/10">
      <div className="flex items-center gap-2 text-xs font-semibold text-teal-400 uppercase tracking-wider">
        <Sparkles className="w-3.5 h-3.5" />
        <span>{t('relatedPolicyDocs')}</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {docs.map((doc) => (
          <Link
            key={doc.id}
            to={`/documents/${doc.id}`}
            className="group glass-card p-3.5 rounded-xl border-white/10 hover:border-teal-400/40 hover:bg-white/10 transition-all flex items-center justify-between"
          >
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-300 shrink-0">
                <FileText className="w-4 h-4" />
              </div>
              <div className="truncate">
                <h4 className="text-xs font-medium text-white group-hover:text-teal-300 truncate">
                  {doc.original_name}
                </h4>
                <p className="text-[10px] text-white/40">{doc.page_count} {t('pagesLabel')} • {doc.language.toUpperCase()}</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-white/30 group-hover:text-teal-400 group-hover:translate-x-1 transition-all shrink-0" />
          </Link>
        ))}
      </div>
    </div>
  );
}
