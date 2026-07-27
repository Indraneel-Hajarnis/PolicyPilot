import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { FileText, ArrowLeft, MessageSquare, FileSearch, Layers, HardDrive, Globe, Calendar, Loader2, AlertCircle } from 'lucide-react';
import { getDocument, getSummary } from '../api/client';
import SummaryCard from '../components/SummaryCard';
import { useLanguage } from '../context/LanguageContext';

export default function DocumentViewerPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    const fetchDoc = async () => {
      try {
        setLoading(true);
        const data = await getDocument(id);
        setDoc(data);
      } catch (err) {
        console.error('Fetch doc error:', err);
        setError(t('docNotFoundLoad'));
      } finally {
        setLoading(false);
      }
    };

    fetchDoc();
  }, [id, t]);

  const handleFetchSummary = async () => {
    try {
      setLoadingSummary(true);
      const data = await getSummary(id);
      setSummary(data);
    } catch (err) {
      console.error('Summary fetch error:', err);
    } finally {
      setLoadingSummary(false);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-10 h-10 animate-spin text-teal-400" />
      </div>
    );
  }

  if (error || !doc) {
    return (
      <div className="page-container space-y-4">
        <button onClick={() => navigate('/documents')} className="btn-ghost flex items-center gap-2 text-xs">
          <ArrowLeft className="w-4 h-4" /> {t('backToDocs')}
        </button>
        <div className="p-6 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300">
          <AlertCircle className="w-6 h-6 shrink-0" />
          <span>{error || t('docNotFound')}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container space-y-8 animate-fade-in">
      {/* Back Button */}
      <button onClick={() => navigate('/documents')} className="btn-ghost inline-flex items-center gap-2 text-xs">
        <ArrowLeft className="w-4 h-4" /> {t('backToDocsList')}
      </button>

      {/* Header Info */}
      <div className="glass-card p-6 sm:p-8 border-teal-500/20 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-xs font-semibold text-teal-300">
            <FileText className="w-3.5 h-3.5" /> {t('policyDocId')}{doc.id}
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">{doc.original_name}</h1>
          <div className="flex flex-wrap gap-4 text-xs text-white/60 pt-1">
            <div className="flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-teal-400" />
              <span>{doc.page_count} {t('pagesLabel')} ({doc.chunk_count} {t('chunks')})</span>
            </div>
            <div className="flex items-center gap-1.5">
              <HardDrive className="w-4 h-4 text-teal-400" />
              <span>{formatBytes(doc.file_size)}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe className="w-4 h-4 text-teal-400" />
              <span>{t('languagePrefix')}: {doc.language.toUpperCase()}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-teal-400" />
              <span>{t('uploadedPrefix')} {new Date(doc.upload_date).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-col sm:flex-row md:flex-col gap-3 shrink-0">
          <Link
            to="/chat"
            className="btn-primary flex items-center justify-center gap-2 text-xs"
          >
            <MessageSquare className="w-4 h-4" /> {t('askQuestionsChat')}
          </Link>
          <button
            onClick={handleFetchSummary}
            disabled={loadingSummary}
            className="btn-secondary flex items-center justify-center gap-2 text-xs"
          >
            {loadingSummary ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileSearch className="w-4 h-4" />}
            <span>{summary ? t('refreshSummaryBtn') : t('generateSummaryBtnLabel')}</span>
          </button>
        </div>
      </div>

      {/* Summary View if generated */}
      {summary && <SummaryCard summary={summary} />}
    </div>
  );
}
