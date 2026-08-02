import React, { useEffect, useState } from 'react';
import { MessageSquarePlus, Trash2, Clock, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { getChatSessions, deleteChatSession, getSessionMessages, createChatSession } from '../api/client';
import { useLanguage } from '../context/LanguageContext';

export default function ChatHistorySidebar({ onLoadSession, onNewChat, refreshTrigger, activeSessionId: activeSessId }) {
  const { t } = useLanguage();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(true);
  const [deletingId, setDeletingId] = useState(null);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const data = await getChatSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  // Re-fetch whenever the parent signals new messages were saved
  useEffect(() => {
    if (refreshTrigger) fetchSessions();
  }, [refreshTrigger]);

  const handleLoad = async (sessionId) => {
    try {
      const data = await getSessionMessages(sessionId);
      if (onLoadSession) {
        onLoadSession(sessionId, data.messages, data.session);
      }
      // Refresh counts after loading so the sidebar stays accurate
      fetchSessions();
    } catch (err) {
      console.error('Failed to load session messages:', err);
    }
  };

  const handleDelete = async (sessionId, e) => {
    e.stopPropagation();
    setDeletingId(sessionId);
    try {
      await deleteChatSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (err) {
      console.error('Failed to delete session:', err);
    } finally {
      setDeletingId(null);
    }
  };

  const handleNewChat = async () => {
    if (onNewChat) onNewChat();
    // Refresh after new session might be created
    setTimeout(fetchSessions, 500);
  };

  const formatDate = (iso) => {
    if (!iso) return '';
    const normalized = iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z';
    const d = new Date(normalized);
    const now = new Date();
    const diff = now - d;
    if (diff < 60000) return t('justNow');
    if (diff < 3600000) return `${Math.floor(diff / 60000)}${t('minsAgo')}`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}${t('hrsAgo')}`;
    return d.toLocaleDateString();
  };

  return (
    <div className="space-y-2">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between text-xs font-bold text-slate-300 uppercase tracking-wider hover:text-white transition-colors"
      >
        <span className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-teal-400" />
          {t('chatHistory')}
        </span>
        {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>

      {expanded && (
        <div className="space-y-1.5">
          {/* New Chat button */}
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs font-semibold hover:bg-teal-500/20 transition-all"
          >
            <MessageSquarePlus className="w-3.5 h-3.5" />
            {t('newChat')}
          </button>

          {/* Sessions list */}
          {loading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-4 h-4 animate-spin text-slate-500" />
            </div>
          ) : sessions.length === 0 ? (
            <p className="text-[10px] text-slate-500 text-center py-3 italic">
              {t('noPreviousChats')}
            </p>
          ) : (
            <div className="space-y-1 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`group flex items-center justify-between px-3 py-2 rounded-lg border transition-all ${
                    activeSessId === session.id
                      ? 'bg-teal-500/10 border-teal-500/30'
                      : 'bg-slate-800/50 hover:bg-slate-800 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <button
                    onClick={() => handleLoad(session.id)}
                    className="min-w-0 flex-1 text-left cursor-pointer"
                  >
                    <p className="text-[11px] text-slate-200 font-medium truncate">
                      {session.title || t('untitledChat')}
                    </p>
                    <p className="text-[9px] text-slate-500 flex items-center gap-1">
                      {session.message_count > 0 ? `${session.message_count} msgs · ` : ''}{formatDate(session.updated_at)}
                    </p>
                  </button>
                  <button
                    onClick={(e) => handleDelete(session.id, e)}
                    disabled={deletingId === session.id}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded text-slate-500 hover:text-rose-400 transition-all shrink-0"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
