import React, { useEffect, useState } from 'react';
import { Database, Globe, FolderGit2, Download, Loader2, ArrowLeft, FolderOpen, FileText, ExternalLink, CheckCircle2 } from 'lucide-react';
import { getRepositorySources, browseGitHubRepo, importFromRepository, seedRepository } from '../api/client';

import { useToast } from '../context/ToastContext';

const TAB_ICONS = { github: FolderGit2, portal: Globe };

export default function RepositoryPage() {
  const toast = useToast();
  const [sources, setSources] = useState([]);
  const [activeTab, setActiveTab] = useState('github_mahgrs');
  const [ghItems, setGhItems] = useState([]);
  const [ghPath, setGhPath] = useState('');
  const [ghLoading, setGhLoading] = useState(false);
  const [importing, setImporting] = useState(null);
  const [imported, setImported] = useState(new Set());

  useEffect(() => {
    getRepositorySources().then(setSources).catch(() => {});
  }, []);

  useEffect(() => {
    if (activeTab === 'github_mahgrs') {
      browseGitHub('');
    }
  }, [activeTab]);

  const browseGitHub = async (path) => {
    setGhLoading(true);
    setGhPath(path);
    try {
      const data = await browseGitHubRepo(path);
      setGhItems(data.items || []);
    } catch (err) {
      toast.error('Failed to browse GitHub repository');
    } finally {
      setGhLoading(false);
    }
  };

  const handleImport = async (item) => {
    if (!item.download_url) {
      toast.error('No download URL available for this item');
      return;
    }
    setImporting(item.path);
    try {
      await importFromRepository(item.download_url, 'github_mahgrs', item.name);
      setImported((prev) => new Set([...prev, item.path]));
      toast.success(`${item.name} imported successfully!`);
    } catch (err) {
      toast.error(`Import failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setImporting(null);
    }
  };

  const navigateUp = () => {
    const parts = ghPath.split('/').filter(Boolean);
    parts.pop();
    browseGitHub(parts.join('/'));
  };

  const formatSize = (bytes) => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  const handleSeedRepository = async () => {
    try {
      toast.info('Seeding Maharashtra policy corpus...');
      const res = await seedRepository();
      toast.success(res.message || 'Central repository seeded successfully!');
    } catch (err) {
      toast.error(`Seeding failed: ${err.message}`);
    }
  };

  return (
    <div className="page-container space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-xs font-bold text-purple-300 shadow-sm">
            <Database className="w-4 h-4 text-purple-400" /> Centralized Repository
          </div>
          <h1 className="section-title text-3xl sm:text-4xl font-extrabold text-white">Open Datasets</h1>
          <p className="section-subtitle text-slate-400 max-w-3xl">
            Browse and import documents from official Maharashtra Government sources and open datasets.
          </p>
        </div>
        <button
          onClick={handleSeedRepository}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-xs shadow-lg shadow-purple-500/20 hover:from-purple-500 hover:to-indigo-500 transition-all shrink-0"
        >
          <Database className="w-4 h-4" /> Seed Central Corpus
        </button>
      </div>


      {/* Source Tabs */}
      <div className="flex flex-wrap gap-2">
        {sources.map((source) => {
          const Icon = TAB_ICONS[source.type] || Globe;
          const isActive = activeTab === source.id;
          return (
            <button
              key={source.id}
              onClick={() => setActiveTab(source.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all border ${
                isActive
                  ? 'bg-purple-500/20 border-purple-500/40 text-purple-300 shadow-lg shadow-purple-500/10'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {source.name}
            </button>
          );
        })}
      </div>

      {/* Active Tab Content */}
      {activeTab === 'github_mahgrs' ? (
        <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl overflow-hidden shadow-2xl">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 px-5 py-3 border-b border-slate-800 bg-slate-800/40">
            <FolderGit2 className="w-4 h-4 text-slate-400" />
            <button onClick={() => browseGitHub('')} className="text-xs text-teal-400 hover:text-teal-300 font-medium">
              orgpedia/mahGRs
            </button>
            {ghPath && ghPath.split('/').filter(Boolean).map((part, i, arr) => (
              <span key={i} className="flex items-center gap-1">
                <span className="text-slate-600">/</span>
                <button
                  onClick={() => browseGitHub(arr.slice(0, i + 1).join('/'))}
                  className="text-xs text-slate-300 hover:text-teal-400 font-medium"
                >
                  {part}
                </button>
              </span>
            ))}
            {ghPath && (
              <button onClick={navigateUp} className="ml-auto text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1">
                <ArrowLeft className="w-3 h-3" /> Back
              </button>
            )}
          </div>

          {/* File List */}
          {ghLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
            </div>
          ) : ghItems.length === 0 ? (
            <div className="text-center py-16 text-slate-500 text-sm">
              No files found at this path
            </div>
          ) : (
            <div className="divide-y divide-slate-800">
              {ghItems.map((item) => (
                <div
                  key={item.path}
                  className="flex items-center justify-between px-5 py-3 hover:bg-slate-800/40 transition-colors group"
                >
                  <div
                    className="flex items-center gap-3 min-w-0 flex-1 cursor-pointer"
                    onClick={() => item.type === 'dir' ? browseGitHub(item.path) : null}
                  >
                    {item.type === 'dir' ? (
                      <FolderOpen className="w-4 h-4 text-amber-400 shrink-0" />
                    ) : (
                      <FileText className="w-4 h-4 text-teal-400 shrink-0" />
                    )}
                    <span className={`text-sm truncate ${item.type === 'dir' ? 'text-white font-medium' : 'text-slate-300'}`}>
                      {item.name}
                    </span>
                    {item.size > 0 && (
                      <span className="text-[10px] text-slate-500 shrink-0">{formatSize(item.size)}</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {item.html_url && (
                      <a
                        href={item.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 transition-colors"
                        title="View on GitHub"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    )}
                    {item.type === 'file' && item.download_url && (
                      imported.has(item.path) ? (
                        <span className="flex items-center gap-1 text-emerald-400 text-[10px] font-bold">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Imported
                        </span>
                      ) : (
                        <button
                          onClick={() => handleImport(item)}
                          disabled={importing === item.path}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-300 text-[11px] font-semibold hover:bg-purple-500/20 transition-all disabled:opacity-50"
                        >
                          {importing === item.path ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <Download className="w-3 h-3" />
                          )}
                          Import
                        </button>
                      )
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* Portal tabs show external links */
        <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-8 text-center space-y-4 max-w-lg mx-auto">
          {sources.filter((s) => s.id === activeTab).map((source) => (
            <div key={source.id} className="space-y-4">
              <Globe className="w-12 h-12 text-slate-600 mx-auto" />
              <h3 className="text-lg font-bold text-white">{source.name}</h3>
              <p className="text-xs text-slate-400">{source.description}</p>
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-500 text-white font-bold text-sm shadow-lg shadow-purple-500/20 hover:from-purple-400 hover:to-indigo-400 transition-all"
              >
                <ExternalLink className="w-4 h-4" /> Visit Portal
              </a>
              <p className="text-[10px] text-slate-500 italic">
                Documents can be downloaded from the portal and uploaded to PolicyPilot manually
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
