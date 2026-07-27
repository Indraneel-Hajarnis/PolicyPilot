import React, { useState } from 'react';
import { FileText, CheckCircle, Calendar, ListChecks, Copy, Check, Download } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function SummaryCard({ summary }) {
  const { t } = useLanguage();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(summary.full_summary || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(summary, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `policy_summary_${summary.document_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 sm:p-8 space-y-6 animate-fade-in shadow-2xl backdrop-blur-xl max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-teal-500/10 text-teal-300 border border-teal-500/30">
            {t('policyExecBrief')}
          </span>
          <h2 className="text-2xl font-extrabold text-white mt-2 leading-tight">{summary.title || summary.document_name}</h2>
          <p className="text-xs text-slate-400 mt-1 font-mono">{summary.document_name}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleExportJson}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-teal-300 border border-slate-700 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{t('exportJson')}</span>
          </button>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-500/15 hover:bg-teal-500/25 text-xs font-semibold text-teal-300 border border-teal-500/30 transition-all"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? t('copied') : t('copyAnswer')}</span>
          </button>
        </div>
      </div>

      {/* Key Points */}
      {summary.key_points && summary.key_points.length > 0 && (
        <div className="space-y-3">
          <h3 className="flex items-center gap-2 text-base font-bold text-teal-300">
            <CheckCircle className="w-4 h-4 text-teal-400" /> {t('keyPoints')}
          </h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {summary.key_points.map((pt, i) => (
              <li key={i} className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs sm:text-sm text-slate-200 leading-relaxed shadow-sm">
                <span className="w-2 h-2 rounded-full bg-teal-400 mt-1.5 shrink-0" />
                <span>{pt}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Sections */}
      {summary.sections && summary.sections.length > 0 && (
        <div className="space-y-3">
          <h3 className="flex items-center gap-2 text-base font-bold text-white">
            <FileText className="w-4 h-4 text-teal-400" /> {t('sections')}
          </h3>
          <div className="space-y-3">
            {summary.sections.map((sec, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
                <h4 className="text-sm font-bold text-teal-300">{sec.title}</h4>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">{sec.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grid for Dates & Action Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        {/* Important Dates */}
        {summary.important_dates && summary.important_dates.length > 0 && (
          <div className="space-y-3">
            <h3 className="flex items-center gap-2 text-sm font-bold text-amber-300">
              <Calendar className="w-4 h-4 text-amber-400" /> {t('importantDates')}
            </h3>
            <div className="space-y-2">
              {summary.important_dates.map((d, i) => (
                <div key={i} className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200 font-medium">
                  {d}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Items */}
        {summary.action_items && summary.action_items.length > 0 && (
          <div className="space-y-3">
            <h3 className="flex items-center gap-2 text-sm font-bold text-emerald-300">
              <ListChecks className="w-4 h-4 text-emerald-400" /> {t('actionItems')}
            </h3>
            <div className="space-y-2">
              {summary.action_items.map((act, i) => (
                <div key={i} className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-200 font-medium">
                  {act}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Full Executive Narrative */}
      {summary.full_summary && (
        <div className="space-y-2 pt-4 border-t border-slate-800">
          <h3 className="text-sm font-bold text-slate-200">{t('executiveSummary')}</h3>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800 whitespace-pre-line">
            {summary.full_summary}
          </p>
        </div>
      )}
    </div>
  );
}
