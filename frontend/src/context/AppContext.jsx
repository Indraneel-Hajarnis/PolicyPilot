import { createContext, useContext, useState, useCallback } from 'react';
import { getDocuments as fetchDocs } from '../api/client';

const AppContext = createContext(null);

export function AppContextProvider({ children }) {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

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
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppContext must be used within AppContextProvider');
  return ctx;
}

export default AppContext;
