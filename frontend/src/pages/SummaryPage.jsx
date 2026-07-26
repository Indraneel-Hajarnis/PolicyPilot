import React, { useState, useEffect } from 'react';
import { FileText, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { getSummary } from '../api/client';
import SummaryCard from '../components/SummaryCard';
import LanguageSelector from '../components/LanguageSelector';
import { useAppContext } from '../context/AppContext';
import { useLanguage } from '../context/LanguageContext';

export default function SummaryPage() {
  const { documents, refreshDocuments } = useAppContext();
  const { language, setLanguage, t } = useLanguage();
  const [selectedDocId, setSelectedDocId] = useState('');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  const handleGenerateSummary = async (docId, targetLang = language) => {
    if (!docId) return;
    setLoading(true);
    setError(null);

    try {
      const data = await getSummary(docId, targetLang);
      setSummary(data);
    } catch (err) {
      console.error('Summary generation error:', err);
      setError(err.response?.data?.error || 'Failed to generate summary.');
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    if (selectedDocId) {
      handleGenerateSummary(selectedDocId, newLang);
    }
  };

  return (
    <div className="page-container space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-teal-500/10 border border-teal-500/30 text-xs font-bold text-teal-300 shadow-sm">
          <Sparkles className="w-4 h-4 text-teal-400 animate-pulse" /> Multi-Language Policy Summarizer
        </div>
        <h1 className="section-title text-3xl sm:text-4xl font-extrabold text-white">{t('summaryTitle')}</h1>
        <p className="section-subtitle text-slate-400 max-w-3xl">
          {t('summarySubtitle')}
        </p>
      </div>

      {/* Controls Card */}
      <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 shadow-2xl backdrop-blur-xl max-w-3xl space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Target Policy selector */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              {t('selectDoc')}
            </label>
            <select
              value={selectedDocId}
              onChange={(e) => {
                setSelectedDocId(e.target.value);
                if (e.target.value) handleGenerateSummary(e.target.value, language);
              }}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-teal-400 transition-all shadow-inner"
            >
              <option value="" className="bg-slate-900 text-white">
                -- Select a document ({documents.length} available) --
              </option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id} className="bg-slate-900 text-white">
                  {doc.original_name || doc.filename}{doc.page_count ? ` (${doc.page_count} pages)` : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Language Selector */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              {t('langLabel')}
            </label>
            <LanguageSelector selectedLanguage={language} onChange={handleLanguageChange} />
          </div>
        </div>

        <button
          onClick={() => handleGenerateSummary(selectedDocId, language)}
          disabled={!selectedDocId || loading}
          className="w-full sm:w-auto bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 disabled:opacity-50 text-white font-bold px-6 py-3 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-teal-500/20"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
          <span>{t('generateSummary')}</span>
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="bg-slate-900/80 border border-teal-500/30 rounded-2xl p-12 text-center space-y-4 animate-pulse shadow-2xl max-w-3xl">
          <Loader2 className="w-10 h-10 animate-spin text-teal-400 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-white">Generating Tri-Lingual Summary...</h3>
            <p className="text-xs text-slate-400">
              Extracting key policy points, section briefs, dates, and compliance steps...
            </p>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm max-w-3xl">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Summary Card */}
      {summary && <SummaryCard summary={summary} />}
    </div>
  );
}
