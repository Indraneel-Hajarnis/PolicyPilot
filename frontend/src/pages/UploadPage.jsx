import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, MessageSquare, Sparkles, FileSearch, Globe, Database, CheckCircle2 } from 'lucide-react';
import UploadDropzone from '../components/UploadDropzone';
import { useAppContext } from '../context/AppContext';
import { useLanguage } from '../context/LanguageContext';

export default function UploadPage() {
  const navigate = useNavigate();
  const { documents, refreshDocuments } = useAppContext();
  const { t } = useLanguage();

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  const handleUploadSuccess = () => {
    refreshDocuments();
  };

  return (
    <div className="page-container space-y-12 animate-fade-in pb-12">
      {/* Hero Section */}
      <div className="text-center space-y-4 max-w-4xl mx-auto pt-6">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/30 text-xs font-bold text-teal-300 shadow-sm">
          <Sparkles className="w-4 h-4 text-teal-400 animate-pulse" />
          <span>Next-Gen Tri-Lingual Policy Intelligence (EN / HI / MR)</span>
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
          {t('uploadTitle')}
        </h1>
        <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-3xl mx-auto">
          {t('uploadSubtitle')}
        </p>
      </div>

      {/* Main Upload Dropzone */}
      <div className="max-w-4xl mx-auto">
        <UploadDropzone onUploadSuccess={handleUploadSuccess} />
      </div>

      {/* Quick Action CTA if documents exist */}
      {documents.length > 0 && (
        <div className="max-w-4xl mx-auto bg-slate-900/90 border border-teal-500/30 rounded-2xl p-6 shadow-2xl backdrop-blur-xl flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-500/20 flex items-center justify-center text-teal-300 shrink-0">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                {documents.length} Policy {documents.length === 1 ? 'Document' : 'Documents'} Indexed
              </h3>
              <p className="text-xs text-slate-400">FAISS vector store populated and ready for English, Hindi, & Marathi Q&A.</p>
            </div>
          </div>
          <div className="flex gap-3 w-full sm:w-auto">
            <button
              onClick={() => navigate('/chat')}
              className="bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white font-bold px-4 py-2.5 rounded-xl flex items-center justify-center gap-2 text-xs transition-all shadow-lg shadow-teal-500/20"
            >
              <MessageSquare className="w-4 h-4" /> {t('navChat')}
            </button>
            <button
              onClick={() => navigate('/summary')}
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold px-4 py-2.5 rounded-xl flex items-center justify-center gap-2 text-xs border border-slate-700 transition-all"
            >
              <FileSearch className="w-4 h-4" /> {t('navSummary')}
            </button>
          </div>
        </div>
      )}

      {/* Tri-Lingual Feature Highlights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 max-w-5xl mx-auto">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-3 shadow-xl backdrop-blur-xl hover:border-teal-500/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
            <Globe className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Tri-Lingual Support</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Full support for English, Hindi (हिन्दी), and Marathi (मराठी) for document ingestion, Q&A, and summaries.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-3 shadow-xl backdrop-blur-xl hover:border-teal-500/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Verifiable Citations</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Every answer includes exact page-level citations, similarity scores, and verifiable confidence ratings.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-3 shadow-xl backdrop-blur-xl hover:border-teal-500/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Database className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">FAISS Vector Index</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            High-speed SentenceTransformer embeddings with FAISS vector indexing for instant top-K retrieval.
          </p>
        </div>
      </div>
    </div>
  );
}
