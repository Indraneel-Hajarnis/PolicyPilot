import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck, MessageSquare, Sparkles, FileSearch,
  Globe, Database, CheckCircle2, Zap, ArrowRight,
} from 'lucide-react';
import UploadDropzone from '../components/UploadDropzone';
import { useAppContext } from '../context/AppContext';
import { useLanguage } from '../context/LanguageContext';
import { useToast } from '../context/ToastContext';

export default function UploadPage() {
  const navigate = useNavigate();
  const { documents, refreshDocuments } = useAppContext();
  const { t } = useLanguage();
  const toast = useToast();
  const [uploadedDoc, setUploadedDoc] = useState(null);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  const handleUploadSuccess = (doc) => {
    refreshDocuments();
    setUploadedDoc(doc);
    toast.success(
      `"${doc.original_name || doc.filename}" processed successfully! ${doc.page_count ? `(${doc.page_count} pages)` : ''}`,
      { duration: 5000 }
    );
  };

  const features = [
    {
      icon: Globe,
      color: 'teal',
      title: 'Tri-Lingual Support',
      desc: 'Full support for English, Hindi (हिन्दी), and Marathi (मराठी) for document ingestion, Q&A, and structured summaries.',
    },
    {
      icon: ShieldCheck,
      color: 'emerald',
      title: 'Verifiable Citations',
      desc: 'Every answer includes exact page-level citations, similarity scores, and verifiable confidence ratings.',
    },
    {
      icon: Database,
      color: 'indigo',
      title: 'Instant Search Engine',
      desc: 'High-speed semantic search for instant answers across long policy documents.',
    },
  ];

  const colorMap = {
    teal:   { bg: 'bg-teal-500/10',   border: 'border-teal-500/20',   icon: 'text-teal-400',   hover: 'hover:border-teal-500/40'   },
    emerald:{ bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: 'text-emerald-400', hover: 'hover:border-emerald-500/40' },
    indigo: { bg: 'bg-indigo-500/10', border: 'border-indigo-500/20', icon: 'text-indigo-400', hover: 'hover:border-indigo-500/40' },
  };

  return (
    <div className="page-container space-y-14 animate-fade-in pb-16">
      {/* ── Hero ── */}
      <div className="text-center space-y-5 max-w-4xl mx-auto pt-6">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/30 text-xs font-bold text-teal-300 shadow-sm">
          <Sparkles className="w-4 h-4 text-teal-400 animate-pulse" />
          <span>Smart Multi-Language Policy Intelligence (EN / HI / MR)</span>
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
          {t('uploadTitle')}
        </h1>
        <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-3xl mx-auto">
          {t('uploadSubtitle')}
        </p>
      </div>

      {/* ── Upload Zone ── */}
      <div className="max-w-4xl mx-auto">
        <UploadDropzone onUploadSuccess={handleUploadSuccess} />
      </div>

      {/* ── Post-upload CTA ── */}
      {documents.length > 0 && (
        <div className="max-w-4xl mx-auto bg-slate-900/90 border border-teal-500/30 rounded-2xl p-6 shadow-2xl backdrop-blur-xl">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-5">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-teal-500/20 flex items-center justify-center text-teal-300 shrink-0">
                <CheckCircle2 className="w-7 h-7" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">
                  {documents.length} Policy {documents.length === 1 ? 'Document' : 'Documents'} Ready
                </h3>
                <p className="text-xs text-slate-400">
                  Policy documents processed — ready for multi-language Q&amp;A and AI summaries.
                </p>
              </div>
            </div>
            <div className="flex gap-3 w-full sm:w-auto shrink-0">
              <button
                onClick={() => navigate('/chat')}
                className="flex-1 sm:flex-none bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white font-bold px-5 py-2.5 rounded-xl flex items-center justify-center gap-2 text-xs transition-all shadow-lg shadow-teal-500/20"
              >
                <MessageSquare className="w-4 h-4" /> {t('navChat')}
                <ArrowRight className="w-3.5 h-3.5 ml-0.5" />
              </button>
              <button
                onClick={() => navigate('/summary')}
                className="flex-1 sm:flex-none bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold px-5 py-2.5 rounded-xl flex items-center justify-center gap-2 text-xs border border-slate-700 transition-all"
              >
                <FileSearch className="w-4 h-4" /> {t('navSummary')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Pipeline Steps ── */}
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-8 space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-bold text-slate-300">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            How PolicyPilot Works
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { step: '01', title: 'Upload & Read', desc: 'Document text is analyzed and language is auto-detected (EN/HI/MR).' },
            { step: '02', title: 'Smart Indexing', desc: 'Text content is structured into search segments for instant retrieval.' },
            { step: '03', title: 'Instant Q&A', desc: 'Ask questions and receive precise answers with verified document citations.' },
          ].map(({ step, title, desc }) => (
            <div key={step} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-2 hover:border-slate-700 transition-all">
              <span className="text-2xl font-black text-teal-500/40 font-mono">{step}</span>
              <h3 className="text-sm font-bold text-white">{title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Feature Cards ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {features.map(({ icon: Icon, color, title, desc }) => {
          const c = colorMap[color];
          return (
            <div
              key={title}
              className={`bg-slate-900/80 border ${c.border} rounded-2xl p-6 space-y-3 shadow-xl backdrop-blur-xl ${c.hover} transition-all`}
            >
              <div className={`w-10 h-10 rounded-xl ${c.bg} border ${c.border} flex items-center justify-center ${c.icon}`}>
                <Icon className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">{title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
