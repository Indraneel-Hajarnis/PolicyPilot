import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Trash2, Eye, Calendar, HardDrive, Layers, Globe, Plus, Search, Filter, CheckCircle2 } from 'lucide-react';
import { deleteDocument } from '../api/client';
import { useAppContext } from '../context/AppContext';
import { useLanguage } from '../context/LanguageContext';
import { useToast } from '../context/ToastContext';

export default function DocumentsPage() {
  const { documents, refreshDocuments } = useAppContext();
  const { t } = useLanguage();
  const toast = useToast();
  const [deletingId, setDeletingId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [languageFilter, setLanguageFilter] = useState('all');

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  const handleDelete = async (id, name, e) => {
    e.preventDefault();
    e.stopPropagation();

    // Custom confirmation via toast — show a temporary warning
    const confirmed = window.confirm(t('deleteConfirm').replace('{name}', name));
    if (!confirmed) return;

    setDeletingId(id);
    try {
      await deleteDocument(id);
      refreshDocuments();
      toast.success(t('deleteSuccessText').replace('{name}', name));
    } catch (err) {
      console.error('Delete error:', err);
      toast.error(t('deleteFailed'));
    } finally {
      setDeletingId(null);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Filter logic
  const filteredDocuments = documents.filter((doc) => {
    const name = doc.original_name || doc.filename || '';
    const matchesSearch = name.toLowerCase().includes(searchQuery.toLowerCase());
    const docLang = (doc.language || 'en').toLowerCase();
    const matchesLang = languageFilter === 'all' || docLang === languageFilter;
    return matchesSearch && matchesLang;
  });

  const getLangBadge = (lang) => {
    const code = (lang || 'en').toLowerCase();
    if (code === 'hi') return { label: 'Hindi (हिन्दी)', bg: 'bg-amber-500/10 border-amber-500/30 text-amber-300' };
    if (code === 'mr') return { label: 'Marathi (मराठी)', bg: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300' };
    return { label: 'English (EN)', bg: 'bg-teal-500/10 border-teal-500/30 text-teal-300' };
  };

  return (
    <div className="page-container space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="section-title text-3xl font-extrabold text-white">{t('docsTitle')}</h1>
          <p className="section-subtitle text-slate-400">
            {t('docsSubtitle')}
          </p>
        </div>
        <Link
          to="/"
          className="bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white font-bold px-4 py-2.5 rounded-xl inline-flex items-center justify-center gap-2 text-xs transition-all shadow-lg shadow-teal-500/20 shrink-0"
        >
          <Plus className="w-4 h-4" /> {t('uploadTitle')}
        </Link>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-4 shadow-xl backdrop-blur-xl flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('searchPlaceholder')}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-400 transition-all"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto shrink-0">
          <Filter className="w-4 h-4 text-teal-400 shrink-0" />
          <select
            value={languageFilter}
            onChange={(e) => setLanguageFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
          >
            <option value="all">{t('filterAll')} ({documents.length})</option>
            <option value="en">English ({documents.filter(d => (d.language||'en') === 'en').length})</option>
            <option value="hi">Hindi ({documents.filter(d => d.language === 'hi').length})</option>
            <option value="mr">Marathi ({documents.filter(d => d.language === 'mr').length})</option>
          </select>
        </div>
      </div>

      {/* Grid */}
      {filteredDocuments.length === 0 ? (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-12 text-center space-y-4 shadow-xl backdrop-blur-xl max-w-md mx-auto">
          <FileText className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">{t('noDocs')}</h3>
          <p className="text-xs text-slate-400">
            {t('uploadPdfPrompt')}
          </p>
          <Link
            to="/"
            className="bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 border border-teal-500/40 px-4 py-2 rounded-xl inline-flex items-center gap-2 text-xs font-bold transition-all"
          >
            <Plus className="w-4 h-4" /> {t('uploadTitle')}
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDocuments.map((doc) => {
            const langBadge = getLangBadge(doc.language);
            return (
              <div
                key={doc.id}
                className="bg-slate-900/90 border border-slate-800 hover:border-teal-500/40 rounded-2xl p-6 flex flex-col justify-between space-y-4 transition-all duration-300 shadow-xl backdrop-blur-xl group relative"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 shrink-0">
                      <FileText className="w-5 h-5" />
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border ${langBadge.bg}`}>
                      {langBadge.label}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-white group-hover:text-teal-300 transition-colors line-clamp-2">
                      {doc.original_name || doc.filename}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 font-mono">{(doc.filename || '').substring(0, 24)}{(doc.filename||'').length > 24 ? '...' : ''}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 pt-3 border-t border-slate-800">
                    <div className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-teal-400" />
                      <span>{doc.page_count} {t('pagesLabel')}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <HardDrive className="w-3.5 h-3.5 text-teal-400" />
                      <span>{formatBytes(doc.file_size)}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Globe className="w-3.5 h-3.5 text-teal-400" />
                      <span>{(doc.language || 'en').toUpperCase()}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-teal-400" />
                      <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                {/* Footer Actions */}
                <div className="flex items-center gap-2 pt-3 border-t border-slate-800">
                  <Link
                    to={`/documents/${doc.id}`}
                    className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 py-2.5 rounded-xl text-xs font-semibold text-center flex items-center justify-center gap-1.5 border border-slate-700 transition-all"
                  >
                    <Eye className="w-3.5 h-3.5" /> {t('viewDetailsBtn')}
                  </Link>
                  <button
                    onClick={(e) => handleDelete(doc.id, doc.original_name || doc.filename, e)}
                    disabled={deletingId === doc.id}
                    className="p-2.5 rounded-xl border border-slate-800 text-slate-500 hover:text-rose-400 hover:border-rose-500/40 hover:bg-rose-500/10 transition-all"
                    title={t('deleteDoc')}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
