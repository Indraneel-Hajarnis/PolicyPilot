import React, { useEffect, useState } from 'react';
import { BarChart3, Database, MessageSquare, Layers, ShieldCheck, Clock, Loader2, Sparkles, Globe } from 'lucide-react';
import { getAnalyticsStats, getRecentQueries } from '../api/client';
import ConfidenceBadge from '../components/ConfidenceBadge';
import { useLanguage } from '../context/LanguageContext';

export default function AnalyticsPage() {
  const { t } = useLanguage();
  const [stats, setStats] = useState(null);
  const [queries, setQueries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [s, q] = await Promise.all([getAnalyticsStats(), getRecentQueries()]);
        setStats(s);
        setQueries(q);
      } catch (err) {
        console.error('Analytics fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-10 h-10 animate-spin text-teal-400" />
      </div>
    );
  }

  const languages = stats?.languages || { en: 0, hi: 0, mr: 0 };
  const totalLangDocs = (languages.en || 0) + (languages.hi || 0) + (languages.mr || 0) || 1;

  return (
    <div className="page-container space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-teal-500/10 border border-teal-500/30 text-xs font-bold text-teal-300 shadow-sm">
          <Sparkles className="w-4 h-4 text-teal-400 animate-pulse" /> {t('analyticsTitle')}
        </div>
        <h1 className="section-title text-3xl font-extrabold text-white">{t('analyticsTitle')}</h1>
        <p className="section-subtitle text-slate-400 max-w-3xl">
          {t('analyticsSubtitle')}
        </p>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 space-y-2 shadow-2xl backdrop-blur-xl hover:border-teal-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">{t('statTotalDocs')}</span>
            <Database className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">{stats?.document_count || 0}</p>
          <p className="text-[11px] text-teal-300 font-medium">{stats?.chunk_count || 0} Total Text Chunks</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 space-y-2 shadow-2xl backdrop-blur-xl hover:border-teal-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">{t('statVectorSize')}</span>
            <Layers className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">{stats?.vector_store_size || 0}</p>
          <p className="text-[11px] text-teal-300 font-medium">384-dim Dense Vectors</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 space-y-2 shadow-2xl backdrop-blur-xl hover:border-teal-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">{t('statTotalQueries')}</span>
            <MessageSquare className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">{stats?.query_count || 0}</p>
          <p className="text-[11px] text-teal-300 font-medium">RAG Grounded Q&A Logs</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 space-y-2 shadow-2xl backdrop-blur-xl hover:border-teal-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">{t('statAvgConfidence')}</span>
            <ShieldCheck className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">
            {((stats?.avg_confidence || 0) * 100).toFixed(0)}%
          </p>
          <p className="text-[11px] text-emerald-400 font-medium">Contextual Accuracy</p>
        </div>
      </div>

      {/* Tri-Lingual Document Breakdown Card */}
      <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 shadow-2xl backdrop-blur-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Globe className="w-5 h-5 text-teal-400" /> {t('langDistribution')}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-950/80 border border-teal-500/20 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-300 font-bold">
              <span>🇬🇧 English (EN)</span>
              <span className="text-teal-400">{languages.en || 0} Docs</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div
                className="bg-teal-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.round(((languages.en || 0) / totalLangDocs) * 100)}%` }}
              />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-amber-500/20 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-300 font-bold">
              <span>🇮🇳 Hindi (हिन्दी)</span>
              <span className="text-amber-400">{languages.hi || 0} Docs</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div
                className="bg-amber-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.round(((languages.hi || 0) / totalLangDocs) * 100)}%` }}
              />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-indigo-500/20 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-300 font-bold">
              <span>🇮🇳 Marathi (मराठी)</span>
              <span className="text-indigo-400">{languages.mr || 0} Docs</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div
                className="bg-indigo-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.round(((languages.mr || 0) / totalLangDocs) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Query Audit Trail Table */}
      <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 shadow-2xl backdrop-blur-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-teal-400" /> {t('recentQueries')}
        </h3>

        {queries.length === 0 ? (
          <p className="text-xs text-slate-400">No Q&A queries recorded yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-3">ID</th>
                  <th className="p-3">Question</th>
                  <th className="p-3">Confidence</th>
                  <th className="p-3">Date & Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {queries.map((q) => (
                  <tr key={q.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="p-3 font-mono text-teal-400">#{q.id}</td>
                    <td className="p-3 font-medium text-white max-w-md truncate">{q.question}</td>
                    <td className="p-3">
                      <ConfidenceBadge confidence={q.confidence} />
                    </td>
                    <td className="p-3 text-slate-400">{new Date(q.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
