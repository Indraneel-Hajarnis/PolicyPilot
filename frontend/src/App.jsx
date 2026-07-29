import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import UploadPage from './pages/UploadPage';
import ChatPage from './pages/ChatPage';
import SummaryPage from './pages/SummaryPage';
import DocumentsPage from './pages/DocumentsPage';
import DocumentViewerPage from './pages/DocumentViewerPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ComparePage from './pages/ComparePage';
import RepositoryPage from './pages/RepositoryPage';
import { ToastProvider } from './context/ToastContext';

function AuthenticatedApp() {
  return (
    <div className="min-h-screen bg-surface-950 text-white flex flex-col font-sans">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/summary" element={<SummaryPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/documents/:id" element={<DocumentViewerPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/repository" element={<RepositoryPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AuthenticatedApp />
            </ProtectedRoute>
          }
        />
      </Routes>
    </ToastProvider>
  );
}
