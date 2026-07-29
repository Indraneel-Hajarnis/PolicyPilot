import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { FileText, ArrowLeft, MessageSquare, FileSearch, Layers, HardDrive, Globe, Calendar, Loader2, AlertCircle, Download, Building2, Tag, Hash, ShieldAlert, CheckCircle2, Clock } from 'lucide-react';
import { getDocument, getSummary, downloadDocument, updateDocumentStatus } from '../api/client';
import SummaryCard from '../components/SummaryCard';
import { useLanguage } from '../context/LanguageContext';
import { useToast } from '../context/ToastContext';

export default function DocumentViewerPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const toast = useToast();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);

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
      toast.error('Failed to generate summary');
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleDownload = async () => {
    if (!doc) return;
    setDownloading(true);
    try {
      const response = await downloadDocument(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.original_name || doc.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success(`Downloaded ${doc.original_name || doc.filename}`);
    } catch (err) {
      console.error('Download error:', err);
      toast.error('Failed to download document');
    } finally {
      setDownloading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      await updateDocumentStatus(id, newStatus);
      setDoc((prev) => ({ ...prev, status: newStatus }));
      toast.success(`Status updated to ${newStatus}`);
    } catch (err) {
      console.error('Status update error:', err);
      toast.error('Failed to update status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getStatusBadgeStyle = (status) => {
    const st = (status || 'active').toLowerCase();
    if (st === 'superseded') return 'bg-rose-500/20 border-rose-500/40 text-rose-300';
    if (st === 'amended') return 'bg-amber-500/20 border-amber-500/40 text-amber-300';
    if (st === 'draft') return 'bg-slate-500/20 border-slate-500/40 text-slate-300';
    return 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300';
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
    <div className="page-container space-y-8 animate-fade-in pb-12">
      {/* Back Button */}
      <button onClick={() => navigate('/documents')} className="btn-ghost inline-flex items-center gap-2 text-xs">
        <ArrowLeft className="w-4 h-4" /> {t('backToDocsList')}
      </button>

      {/* Header Info */}
      <div className="glass-card p-6 sm:p-8 border-teal-500/20 flex flex-col md:flex-row md:items-start justify-between gap-6">
        <div className="space-y-4 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-xs font-semibold text-teal-300">
              <FileText className="w-3.5 h-3.5" /> Document #{doc.id}
            </span>

            {/* Legal Status Selector */}
            <div className="flex items-center gap-1.5">
              <span className={`px-3 py-1 rounded-full text-xs font-bold border capitalize ${getStatusBadgeStyle(doc.status)}`}>
                {doc.status || 'active'}
              </span>
              <select
                value={doc.status || 'active'}
                onChange={(e) => handleStatusChange(e.target.value)}
                disabled={updatingStatus}
                className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-0.5 text-[11px] text-slate-300 focus:outline-none focus:border-teal-400"
              >
                <option value="active">Active</option>
                <option value="amended">Amended</option>
                <option value="superseded">Superseded</option>
                <option value="draft">Draft</option>
              </select>
            </div>
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">{doc.original_name || doc.filename}</h1>
            {doc.document_number && (
              <p className="text-xs font-mono text-teal-400 mt-1 flex items-center gap-1">
                <Hash className="w-3.5 h-3.5" /> Document Number: {doc.document_number}
              </p>
            )}
            {doc.department && (
              <p className="text-sm text-slate-300 mt-1 flex items-center gap-1.5">
                <Building2 className="w-4 h-4 text-teal-400" /> Department: {doc.department}
              </p>
            )}
          </div>

          <div className="flex flex-wrap gap-4 text-xs text-white/60 pt-2 border-t border-slate-800">
            <div className="flex items-center gap-1.5">
              <Tag className="w-4 h-4 text-teal-400" />
              <span>Category: {doc.category || 'Policy'}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-teal-400" />
              <span>{doc.page_count || 0} Pages</span>
            </div>
            <div className="flex items-center gap-1.5">
              <HardDrive className="w-4 h-4 text-teal-400" />
              <span>{formatBytes(doc.file_size)}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe className="w-4 h-4 text-teal-400" />
              <span>Language: {(doc.language || 'en').toUpperCase()}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-teal-400" />
              <span>Uploaded: {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleString() : 'N/A'}</span>
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
            onClick={handleDownload}
            disabled={downloading}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold px-4 py-2.5 rounded-xl flex items-center justify-center gap-2 text-xs border border-slate-700 transition-all"
          >
            {downloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4 text-teal-400" />}
            <span>Download Original File</span>
          </button>
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

      {/* Text Preview Section if available */}
      {doc.text_preview && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-3 shadow-xl">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <FileText className="w-4 h-4 text-teal-400" /> Document Text Preview
          </h3>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs font-mono text-slate-300 max-h-60 overflow-y-auto whitespace-pre-wrap leading-relaxed">
            {doc.text_preview.slice(0, 3000)}...
          </div>
        </div>
      )}

      {/* Summary View if generated */}
      {summary && <SummaryCard summary={summary} />}
    </div>
  );
}
