import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Upload ──────────────────────────────────────────────────────────────────

export const uploadDocument = async (file, onProgress, metadata = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  if (metadata.department) formData.append('department', metadata.department);
  if (metadata.document_number) formData.append('document_number', metadata.document_number);
  if (metadata.category) formData.append('category', metadata.category);

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });
  return response.data;
};

// ── Query ───────────────────────────────────────────────────────────────────

export const queryDocuments = async (question, documentId = null, language = null, conversationHistory = null) => {
  const payload = { question };
  if (documentId) payload.document_id = documentId;
  if (language) payload.language = language;
  if (conversationHistory && conversationHistory.length > 0) {
    payload.conversation_history = conversationHistory;
  }

  const response = await api.post('/query', payload);
  return response.data;
};

// ── Summary ─────────────────────────────────────────────────────────────────

export const getSummary = async (documentId, language = 'en') => {
  const response = await api.get(`/summary/${documentId}`, {
    params: { language },
  });
  return response.data;
};

// ── Documents ───────────────────────────────────────────────────────────────

export const getDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const getDocument = async (documentId) => {
  const response = await api.get(`/documents/${documentId}`);
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
};

export const downloadDocument = async (documentId) => {
  const response = await api.get(`/documents/${documentId}/download`, {
    responseType: 'blob',
  });
  return response;
};

export const updateDocumentStatus = async (documentId, status) => {
  const response = await api.patch(`/documents/${documentId}/status`, { status });
  return response.data;
};

// ── Chat Sessions ───────────────────────────────────────────────────────────

export const getChatSessions = async () => {
  const response = await api.get('/chat/sessions');
  return response.data;
};

export const createChatSession = async (title = 'New Chat', documentId = null) => {
  const response = await api.post('/chat/sessions', { title, document_id: documentId });
  return response.data;
};

export const getSessionMessages = async (sessionId) => {
  const response = await api.get(`/chat/sessions/${sessionId}/messages`);
  return response.data;
};

export const addSessionMessage = async (sessionId, role, content, confidence = null, sourcesJson = null) => {
  const response = await api.post(`/chat/sessions/${sessionId}/messages`, {
    role,
    content,
    confidence,
    sources_json: sourcesJson,
  });
  return response.data;
};

export const deleteChatSession = async (sessionId) => {
  const response = await api.delete(`/chat/sessions/${sessionId}`);
  return response.data;
};

// ── Document Comparison ─────────────────────────────────────────────────────

export const compareDocuments = async (docIdA, docIdB, language = 'en') => {
  const response = await api.post('/compare', { doc_id_a: docIdA, doc_id_b: docIdB, language });
  return response.data;
};

// ── Repository / Open Datasets ──────────────────────────────────────────────

export const getRepositorySources = async () => {
  const response = await api.get('/repository/sources');
  return response.data;
};

export const browseGitHubRepo = async (path = '') => {
  const response = await api.get('/repository/github', { params: { path } });
  return response.data;
};

export const importFromRepository = async (url, source, filename = null) => {
  const response = await api.post('/repository/import', { url, source, filename });
  return response.data;
};

// ── Analytics ───────────────────────────────────────────────────────────────

export const getAnalyticsStats = async () => {
  const response = await api.get('/analytics/stats');
  return response.data;
};

export const getRecentQueries = async () => {
  const response = await api.get('/analytics/queries');
  return response.data;
};

// ── Health ───────────────────────────────────────────────────────────────────

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
