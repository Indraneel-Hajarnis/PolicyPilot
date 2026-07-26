import { useState, useCallback, useRef, useEffect } from 'react';
import { queryDocuments } from '../api/client';

/**
 * Custom hook for managing chat state and interactions.
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
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

      // Add user message
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: question,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await queryDocuments(question, documentId, language);

        // Add AI message
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: response.answer,
          confidence: response.confidence,
          sources: response.sources || [],
          relatedDocs: response.related_documents || [],
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      } catch (err) {
        const errorMsg = err.response?.data?.error || 'Failed to get a response. Please try again.';
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
    []
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
    messagesEndRef,
  };
}

export default useChat;
