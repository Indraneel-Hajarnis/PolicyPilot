import React, { useEffect, useState } from 'react';
import {
  BarChart3, FileText, Layers, HardDrive, MessageSquare,
  Globe, Shield, Activity, Zap, TrendingUp, Database,
  RefreshCw, AlertCircle, CheckCircle2, Clock
} from 'lucide-react';
import { getAnalyticsStats, getRecentQueries } from '../api/client';
import { useLanguage } from '../context/LanguageContext';

// ── Helpers ────────────────────────────────────────────────────────────

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// ── Mini Components ────────────────────────────────────────────────────

function StatCard({ icon: Icon, label, value, sub, color = 'teal', loading }) {
  const colorMap = {
    teal:   { bg: 'bg-teal-500/10',   border: 'border-teal-500/30',   text: 'text-teal-400'   },
    emerald:{ bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400' },
    indigo: { bg: 'bg-indigo-500/10', border: 'border-indigo-500/30', text: 'text-indigo-400' },
    amber:  { bg: 'bg-amber-500/10',  border: 'border-amber-500/30',  text: 'text-amber-400'  },
  };
  const c = colorMap[color] || colorMap.teal;

  return (
    <div className="bg-slate-900/90 border border-slate-800 hover:border-slate-600 rounded-2xl p-6 flex flex-col gap-4 shadow-xl backdrop-blur-xl transition-all duration-300 group">
      <div className="flex items-center justify-between">
        <div className={`w-11 h-11 rounded-xl ${c.bg} border ${c.border} flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${c.text}`} />
        </div>
        {!loading && (
          <TrendingUp className="w-4 h-4 text-slate-600 group-hover:text-teal-400 transition-colors" />
        )}
      </div>
      {loading ? (
        <div className="space-y-2 animate-pulse">
          <div className="h-8 bg-slate-800 rounded-lg w-2/3" />
          <div className="h-4 bg-slate-800 rounded w-full" />
        </div>
      ) : (
        <div>
          <div className={`text-3xl font-extrabold tracking-tight ${c.text}`}>{value}</div>
          <div className="text-sm font-semibold text-white mt-0.5">{label}</div>
          {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
        </div>
      )}
    </div>
  );
}

function LangBar({ label, count, total, color }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  const barColor = {
    teal: 'bg-gradient-to-r from-teal-500 to-emerald-500',
    amber: 'bg-gradient-to-r from-amber-400 to-orange-500',
    indigo: 'bg-gradient-to-r from-indigo-500 to-violet-500',
  }[color] || 'bg-teal-500';

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs font-medium">
        <span className="text-slate-200">{label}</span>
        <span className="text-slate-400">{count} docs · {pct}%</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${barColor} transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function StatusPill({ label, status, t }) {
  const ok = status === 'ok';
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-800 last:border-0">
      <span className="text-sm text-slate-300">{label}</span>
      <span className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border ${
        ok
          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
          : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
      }`}>
        {ok
          ? <CheckCircle2 className="w-3 h-3" />
          : <AlertCircle className="w-3 h-3" />
        }
        {ok ? t('operational') : t('degraded')}
      </span>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────

export default function AnalyticsPage() {
  const { t } = useLanguage();
  const [stats, setStats] = useState(null);
  const [queries, setQueries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, q] = await Promise.all([getAnalyticsStats(), getRecentQueries()]);
      setStats(s);
      setQueries(q);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Analytics load error:', err);
      setError(t('analyticsLoadError'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const totalLang = stats
    ? (stats.languages.en || 0) + (stats.languages.hi || 0) + (stats.languages.mr || 0)
    : 0;

  return (
    <div className="page-container space-y-8 animate-fade-in pb-12">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-teal-500/10 border border-teal-500/30 text-xs font-bold text-teal-300">
            <BarChart3 className="w-4 h-4" />
            {t('analyticsInsights')}
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            {t('analyticsTitle')}
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl">{t('analyticsSubtitle')}</p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shrink-0 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {t('refreshBtn')}
        </button>
      </div>

      {/* ── Error state ── */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-5 flex items-center gap-3 text-rose-300 text-sm max-w-2xl">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* ── Stats Grid ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={FileText}
          label={t('totalDocs')}
          value={stats?.document_count ?? '—'}
          sub={t('docsInSystem')}
          color="teal"
          loading={loading}
        />
        <StatCard
          icon={Layers}
          label={t('totalPages')}
          value={stats?.page_count ?? '—'}
          sub={t('pagesProcessed')}
          color="emerald"
          loading={loading}
        />
        <StatCard
          icon={MessageSquare}
          label={t('queryCount')}
          value={stats?.query_count ?? '—'}
          sub={t('queriesAnswered')}
          color="indigo"
          loading={loading}
        />
        <StatCard
          icon={HardDrive}
          label={t('totalSize')}
          value={stats ? formatBytes(stats.total_size_bytes) : '—'}
          sub={t('storageConsumed')}
          color="amber"
          loading={loading}
        />
      </div>

      {/* ── Middle Row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Language Breakdown */}
        <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl space-y-5">
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-teal-400" />
            <h2 className="text-base font-bold text-white">{t('langBreakdown')}</h2>
          </div>

          {loading ? (
            <div className="space-y-4 animate-pulse">
              {[1,2,3].map(i => (
                <div key={i} className="space-y-1.5">
                  <div className="h-3 bg-slate-800 rounded w-full" />
                  <div className="h-2 bg-slate-800 rounded-full w-full" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              <LangBar
                label="🇬🇧 English (EN)"
                count={stats?.languages.en || 0}
                total={totalLang}
                color="teal"
              />
              <LangBar
                label="🇮🇳 Hindi (हिन्दी)"
                count={stats?.languages.hi || 0}
                total={totalLang}
                color="amber"
              />
              <LangBar
                label="🇮🇳 Marathi (मराठी)"
                count={stats?.languages.mr || 0}
                total={totalLang}
                color="indigo"
              />
            </div>
          )}

          {!loading && totalLang === 0 && (
            <p className="text-xs text-slate-500 text-center pt-2">
              {t('noDocsUploaded')}
            </p>
          )}
        </div>

        {/* System Status */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl space-y-1">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-bold text-white">{t('systemStatus')}</h2>
          </div>
          <StatusPill label={t('apiServer')} status="ok" t={t} />
          <StatusPill label={t('dbStorage')} status="ok" t={t} />
          <StatusPill label={t('searchIndexTitle')} status="ok" t={t} />
          <StatusPill label={t('multiLangEngineStatus')} status="ok" t={t} />
          <StatusPill label={t('docParser')} status="ok" t={t} />
          <div className="flex items-center gap-1.5 text-[10px] text-slate-600 pt-3 border-t border-slate-800 mt-2">
            <Clock className="w-3 h-3" />
            {t('lastUpdated')}: {lastRefresh.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* ── System Architecture ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl hover:border-teal-500/30 transition-all">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <Zap className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">{t('smartSearchIdx')}</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {t('smartSearchDesc')}
          </p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl hover:border-emerald-500/30 transition-all">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">{t('multiLangEngine')}</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {t('multiLangDesc')}
          </p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl hover:border-indigo-500/30 transition-all">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <MessageSquare className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">{t('aiAnalysis')}</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {t('aiAnalysisDesc')}
          </p>
        </div>
      </div>

      {/* ── Recent Activity ── */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-5">
          <Clock className="w-5 h-5 text-teal-400" />
          <h2 className="text-base font-bold text-white">{t('recentActivity')}</h2>
        </div>

        {loading ? (
          <div className="space-y-3 animate-pulse">
            {[1,2,3].map(i => (
              <div key={i} className="h-12 bg-slate-800 rounded-xl" />
            ))}
          </div>
        ) : queries.length === 0 ? (
          <div className="text-center py-10 space-y-3">
            <MessageSquare className="w-10 h-10 text-slate-700 mx-auto" />
            <p className="text-sm text-slate-500">{t('noActivity')}</p>
            <p className="text-xs text-slate-600">
              {t('askViaChat')}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {queries.map((q, i) => (
              <div
                key={i}
                className="flex items-center gap-4 p-4 bg-slate-950/50 rounded-xl border border-slate-800 text-sm"
              >
                <MessageSquare className="w-4 h-4 text-teal-400 shrink-0" />
                <span className="text-slate-200 flex-1 line-clamp-1">{q.question || q}</span>
                {q.confidence && (
                  <span className="text-xs font-bold text-teal-300 bg-teal-500/10 border border-teal-500/30 px-2 py-0.5 rounded-full">
                    {Math.round(q.confidence * 100)}%
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}