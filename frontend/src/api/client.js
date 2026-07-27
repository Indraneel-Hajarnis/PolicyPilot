import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Upload ──────────────────────────────────────────────────────────────────

export const uploadDocument = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

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

export const queryDocuments = async (question, documentId = null, language = null) => {
  const payload = { question };
  if (documentId) payload.document_id = documentId;
  if (language) payload.language = language;

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
