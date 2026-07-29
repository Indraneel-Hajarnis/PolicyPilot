import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { getDocuments as fetchDocs } from '../api/client';

const AppContext = createContext(null);

// ── sessionStorage helpers ────────────────────────────────────────────────────
const SS_CHAT_KEY = 'policypilot_chat_messages';
const SS_DOC_KEY  = 'policypilot_chat_doc_id';

function loadMessages() {
  try {
    const raw = sessionStorage.getItem(SS_CHAT_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    // Restore Date objects (JSON serializes them as strings)
    return parsed.map((m) => ({ ...m, timestamp: m.timestamp ? new Date(m.timestamp) : new Date() }));
  } catch {
    return [];
  }
}

function saveMessages(msgs) {
  try {
    sessionStorage.setItem(SS_CHAT_KEY, JSON.stringify(msgs));
  } catch { /* quota exceeded — silently ignore */ }
}

function loadDocId() {
  try {
    return sessionStorage.getItem(SS_DOC_KEY) || '';
  } catch {
    return '';
  }
}

function saveDocId(id) {
  try {
    sessionStorage.setItem(SS_DOC_KEY, id);
  } catch { /* ignore */ }
}

// ─────────────────────────────────────────────────────────────────────────────

export function AppContextProvider({ children }) {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Persistent chat state — survives route navigation
  const [chatMessages, _setChatMessages] = useState(loadMessages);
  const [chatSelectedDocId, _setChatSelectedDocId] = useState(loadDocId);

  // Wrap setters to also persist to sessionStorage
  const setChatMessages = useCallback((updater) => {
    _setChatMessages((prev) => {
      const next = typeof updater === 'function' ? updater(prev) : updater;
      saveMessages(next);
      return next;
    });
  }, []);

  const setChatSelectedDocId = useCallback((id) => {
    _setChatSelectedDocId(id);
    saveDocId(id);
  }, []);

  const clearChatHistory = useCallback(() => {
    _setChatMessages([]);
    sessionStorage.removeItem(SS_CHAT_KEY);
  }, []);

  const refreshDocuments = useCallback(async () => {
    try {
      setIsLoading(true);
      const docs = await fetchDocs();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = {
    documents,
    setDocuments,
    selectedDocument,
    setSelectedDocument,
    isLoading,
    setIsLoading,
    refreshDocuments,
    // Chat persistence
    chatMessages,
    setChatMessages,
    chatSelectedDocId,
    setChatSelectedDocId,
    clearChatHistory,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppContext must be used within AppContextProvider');
  return ctx;
}

export default AppContext;
