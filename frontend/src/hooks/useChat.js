import { useState, useCallback, useRef, useEffect } from 'react';
import { queryDocuments, createChatSession, addSessionMessage } from '../api/client';
import { useAppContext } from '../context/AppContext';

/**
 * Custom hook for managing chat state and interactions.
 * Non-blocking fast execution for sub-second responses.
 */
export function useChat() {
  const { chatMessages: messages, setChatMessages: setMessages, clearChatHistory } = useAppContext();
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(
    async (question, documentId = null, language = null) => {
      if (!question.trim()) return;

      // Add user message to UI immediately
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: question,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      // Async background session creation if needed (non-blocking)
      let currentSessionId = activeSessionId;
      const initSessionPromise = (async () => {
        if (!currentSessionId) {
          try {
            const newSession = await createChatSession(question.slice(0, 50), documentId);
            currentSessionId = newSession.id;
            setActiveSessionId(currentSessionId);
          } catch (e) {}
        }
        if (currentSessionId) {
          addSessionMessage(currentSessionId, 'user', question).catch(() => {});
        }
        return currentSessionId;
      })();

      try {
        // Build conversation history from prior messages (exclude latest user message we just added)
        const history = messages
          .filter((m) => m.role === 'user' || m.role === 'assistant')
          .filter((m) => !m.isError)
          .slice(-10) // Keep last 10 messages max
          .map((m) => ({ role: m.role, content: m.content }));

        // Fire main Q&A query immediately
        const response = await queryDocuments(question, documentId, language, history);

        // Add AI message to UI immediately
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: response.answer,
          confidence: response.confidence,
          sources: response.sources || [],
          conflicts: response.conflicts || [],
          relatedDocs: response.related_documents || [],
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);

        // Background save to DB session
        initSessionPromise.then((sessId) => {
          if (sessId) {
            addSessionMessage(
              sessId,
              'assistant',
              response.answer,
              response.confidence,
              JSON.stringify(response.sources || [])
            ).catch(() => {});
          }
        });
      } catch (err) {
        const errorMsg = err.response?.data?.detail || err.response?.data?.error || err.message || 'Failed to get a response. Please try again.';
        setError(errorMsg);
        const errorMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: `⚠️ ${errorMsg}`,
          isError: true,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [messages, setMessages, activeSessionId]
  );

  const loadSessionMessages = useCallback((sessionId, loadedMsgs, sessionInfo) => {
    setActiveSessionId(sessionId);
    const formatted = loadedMsgs.map((m) => ({
      id: m.id,
      role: m.role,
      content: m.content,
      confidence: m.confidence,
      sources: m.sources || [],
      timestamp: m.created_at ? new Date(m.created_at) : new Date(),
    }));
    setMessages(formatted);
  }, [setMessages]);

  const clearChat = useCallback(() => {
    clearChatHistory();
    setActiveSessionId(null);
    setError(null);
  }, [clearChatHistory]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
    loadSessionMessages,
    activeSessionId,
    messagesEndRef,
  };
}

export default useChat;
