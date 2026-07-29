import React, { useEffect, useState } from 'react';
import { GitCompareArrows, Loader2, AlertTriangle, CheckCircle2, XCircle, ArrowRight } from 'lucide-react';
import { compareDocuments } from '../api/client';
import { useAppContext } from '../context/AppContext';
import { useLanguage } from '../context/LanguageContext';
import LanguageSelector from '../components/LanguageSelector';

export default function ComparePage() {
  const { documents, refreshDocuments } = useAppContext();
  const { language, setLanguage, t } = useLanguage();
  const [docIdA, setDocIdA] = useState('');
  const [docIdB, setDocIdB] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  const handleCompare = async () => {
    if (!docIdA || !docIdB) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await compareDocuments(parseInt(docIdA), parseInt(docIdB), language);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Comparison failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-xs font-bold text-indigo-300 shadow-sm">
          <GitCompareArrows className="w-4 h-4 text-indigo-400" /> Document Comparison
        </div>
        <h1 className="section-title text-3xl sm:text-4xl font-extrabold text-white">Compare Documents</h1>
        <p className="section-subtitle text-slate-400 max-w-3xl">
          Select two policy documents to compare their content, identify differences, and detect conflicting provisions.
        </p>
      </div>

      {/* Controls */}
      <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 shadow-2xl backdrop-blur-xl max-w-4xl space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-end">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Document A</label>
            <select
              value={docIdA}
              onChange={(e) => setDocIdA(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-teal-400 transition-all"
            >
              <option value="">Select document...</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>{doc.original_name || doc.filename}</option>
              ))}
            </select>
          </div>

          <div className="hidden md:flex items-center justify-center pb-1">
            <ArrowRight className="w-5 h-5 text-slate-600" />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Document B</label>
            <select
              value={docIdB}
              onChange={(e) => setDocIdB(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-teal-400 transition-all"
            >
              <option value="">Select document...</option>
              {documents.filter((d) => String(d.id) !== docIdA).map((doc) => (
                <option key={doc.id} value={doc.id}>{doc.original_name || doc.filename}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Language</label>
            <LanguageSelector selectedLanguage={language} onChange={setLanguage} />
          </div>
          <button
            onClick={handleCompare}
            disabled={!docIdA || !docIdB || loading || docIdA === docIdB}
            className="bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 disabled:opacity-40 text-white font-bold px-6 py-3 rounded-xl flex items-center gap-2 transition-all shadow-lg shadow-indigo-500/20 mt-auto"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <GitCompareArrows className="w-5 h-5" />}
            Compare
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm max-w-4xl flex items-center gap-2">
          <XCircle className="w-5 h-5 shrink-0" /> {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="bg-slate-900/80 border border-indigo-500/30 rounded-2xl p-12 text-center space-y-4 animate-pulse shadow-2xl max-w-4xl">
          <Loader2 className="w-10 h-10 animate-spin text-indigo-400 mx-auto" />
          <h3 className="text-lg font-bold text-white">Analyzing Documents...</h3>
          <p className="text-xs text-slate-400">Comparing content and identifying differences</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 max-w-4xl animate-fade-in">
          {/* Header */}
          <div className="flex items-center gap-4 text-sm font-semibold text-slate-300 bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="px-3 py-1 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs">{result.doc_a?.name}</span>
            <ArrowRight className="w-4 h-4 text-slate-600" />
            <span className="px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs">{result.doc_b?.name}</span>
          </div>

          {/* Similarities */}
          {result.similarities?.length > 0 && (
            <div className="bg-slate-900/90 border border-emerald-500/20 rounded-2xl p-6 space-y-3">
              <h3 className="text-sm font-bold text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> Similarities ({result.similarities.length})
              </h3>
              <ul className="space-y-2">
                {result.similarities.map((s, i) => (
                  <li key={i} className="text-xs text-slate-300 pl-4 border-l-2 border-emerald-500/30 py-1">{s}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Differences */}
          {result.differences?.length > 0 && (
            <div className="bg-slate-900/90 border border-amber-500/20 rounded-2xl p-6 space-y-3">
              <h3 className="text-sm font-bold text-amber-300 flex items-center gap-2">
                <GitCompareArrows className="w-4 h-4" /> Differences ({result.differences.length})
              </h3>
              <div className="space-y-3">
                {result.differences.map((d, i) => (
                  <div key={i} className="bg-slate-800/60 rounded-xl p-4 space-y-2 border border-slate-700/50">
                    <h4 className="text-xs font-bold text-white">{d.aspect}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div className="p-2.5 rounded-lg bg-teal-500/5 border border-teal-500/20">
                        <span className="text-teal-400 font-semibold text-[10px] uppercase">Doc A:</span>
                        <p className="text-slate-300 mt-1">{d.doc_a}</p>
                      </div>
                      <div className="p-2.5 rounded-lg bg-indigo-500/5 border border-indigo-500/20">
                        <span className="text-indigo-400 font-semibold text-[10px] uppercase">Doc B:</span>
                        <p className="text-slate-300 mt-1">{d.doc_b}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Changes */}
          {result.key_changes?.length > 0 && (
            <div className="bg-slate-900/90 border border-rose-500/20 rounded-2xl p-6 space-y-3">
              <h3 className="text-sm font-bold text-rose-300 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" /> Key Changes ({result.key_changes.length})
              </h3>
              <ul className="space-y-2">
                {result.key_changes.map((c, i) => (
                  <li key={i} className="text-xs text-slate-300 pl-4 border-l-2 border-rose-500/30 py-1">{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Conflict Areas */}
          {result.conflict_areas?.length > 0 && (
            <div className="bg-rose-500/5 border border-rose-500/30 rounded-2xl p-6 space-y-3">
              <h3 className="text-sm font-bold text-rose-400 flex items-center gap-2">
                <XCircle className="w-4 h-4" /> ⚠️ Conflicting Provisions ({result.conflict_areas.length})
              </h3>
              <ul className="space-y-2">
                {result.conflict_areas.map((c, i) => (
                  <li key={i} className="text-xs text-rose-200 pl-4 border-l-2 border-rose-500/50 py-1 font-medium">{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendation */}
          {result.recommendation && (
            <div className="bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
              <h3 className="text-sm font-bold text-slate-200 mb-2">💡 Recommendation</h3>
              <p className="text-xs text-slate-300 leading-relaxed">{result.recommendation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
