import React, { useEffect, useState } from 'react';
import { Send, Bot, Trash2, Filter, Loader2 } from 'lucide-react';
import useChat from '../hooks/useChat';
import ChatBubble from '../components/ChatBubble';
import LanguageSelector from '../components/LanguageSelector';
import RelatedDocsList from '../components/RelatedDocsList';
import VoiceInputButton from '../components/VoiceInputButton';
import ChatHistorySidebar from '../components/ChatHistorySidebar';
import { useAppContext } from '../context/AppContext';
import { useLanguage } from '../context/LanguageContext';

export default function ChatPage() {
  const { messages, isLoading, sendMessage, clearChat, loadSessionMessages, messagesEndRef } = useChat();
  const { documents, refreshDocuments, chatSelectedDocId, setChatSelectedDocId } = useAppContext();
  const { language, setLanguage, t } = useLanguage();
  const [inputQuestion, setInputQuestion] = useState('');

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputQuestion.trim() || isLoading) return;
    const docId = chatSelectedDocId ? parseInt(chatSelectedDocId) : null;
    sendMessage(inputQuestion, docId, language);
    setInputQuestion('');
  };

  const handleSpeechInput = (transcript) => {
    setInputQuestion(transcript);
  };

  const handleLoadSession = (sessionId, loadedMsgs, sessionInfo) => {
    loadSessionMessages(sessionId, loadedMsgs, sessionInfo);
    if (sessionInfo && sessionInfo.document_id) {
      setChatSelectedDocId(String(sessionInfo.document_id));
    }
  };

  const latestAiMessage = [...messages].reverse().find((m) => m.role === 'assistant');

  const samplePrompts = [
    t('sampleQ1'),
    t('sampleQ2'),
    t('sampleQ3'),
  ];

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col md:flex-row overflow-hidden bg-slate-950">
      {/* Sidebar - Scope, History & Settings */}
      <div className="w-full md:w-80 bg-slate-900/80 border-b md:border-b-0 md:border-r border-slate-800 p-4 space-y-5 flex shrink-0 flex-col overflow-y-auto backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Filter className="w-4 h-4 text-teal-400" /> {t('policyScope')}
          </h2>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="text-xs text-rose-400 hover:text-rose-300 transition-colors flex items-center gap-1 font-semibold"
            >
              <Trash2 className="w-3.5 h-3.5" /> {t('clearChat')}
            </button>
          )}
        </div>

        {/* Target Document Scope */}
        <div className="space-y-1.5">
          <label className="text-xs text-slate-400 font-medium">{t('policySelection')}</label>
          <select
            value={chatSelectedDocId}
            onChange={(e) => setChatSelectedDocId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
          >
            <option value="" className="bg-slate-900 text-white">
              {t('allPolicyDocs')} ({documents.length})
            </option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id} className="bg-slate-900 text-white">
                {doc.original_name || doc.filename}
              </option>
            ))}
          </select>
        </div>

        {/* Target Response Language */}
        <div className="space-y-1.5 pt-1">
          <label className="text-xs text-slate-400 font-medium">{t('langLabel')}</label>
          <LanguageSelector selectedLanguage={language} onChange={setLanguage} />
        </div>

        {/* Chat Sessions History Sidebar Component (SRS Section 3.7 FR3) */}
        <div className="pt-2 border-t border-slate-800">
          <ChatHistorySidebar onLoadSession={handleLoadSession} onNewChat={clearChat} />
        </div>

        {/* Related documents sidebar widget */}
        {latestAiMessage && latestAiMessage.relatedDocs && (
          <div className="pt-2 border-t border-slate-800">
            <RelatedDocsList docs={latestAiMessage.relatedDocs} />
          </div>
        )}
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 overflow-hidden relative">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto space-y-6 text-slate-400 animate-fade-in">
              <div className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 shadow-xl shadow-teal-500/10">
                <Bot className="w-8 h-8 animate-pulse" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white tracking-tight">{t('chatTitle')}</h3>
                <p className="text-xs sm:text-sm text-slate-400 mt-2 leading-relaxed">
                  {t('chatSubtitle')}
                </p>
              </div>
              <div className="grid grid-cols-1 gap-2.5 w-full pt-2">
                <span className="text-xs font-semibold text-teal-400/80 uppercase tracking-wider text-left">
                  {t('suggestedQuestions')}
                </span>
                {samplePrompts.map((sample, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setInputQuestion(sample);
                    }}
                    className="text-left text-xs sm:text-sm p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-teal-500/50 hover:bg-slate-800/80 text-slate-200 transition-all shadow-md group"
                  >
                    <span className="group-hover:text-teal-300 font-medium">"{sample}"</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto">
              {messages.map((msg) => (
                <ChatBubble key={msg.id} message={msg} />
              ))}
              {isLoading && (
                <div className="flex gap-3 items-center text-teal-300 text-xs p-4 rounded-xl bg-slate-900 border border-teal-500/40 max-w-xs animate-pulse shadow-xl">
                  <Loader2 className="w-4 h-4 animate-spin text-teal-400 shrink-0" />
                  <span>{t('analyzingDocs')}</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Bar with Voice Button */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/95 backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex items-center gap-2 sm:gap-3">
            <VoiceInputButton onSpeechInput={handleSpeechInput} disabled={isLoading} />
            
            <input
              type="text"
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              placeholder={t('inputPlaceholder')}
              disabled={isLoading}
              className="flex-1 bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-400 transition-all shadow-inner"
            />
            <button
              type="submit"
              disabled={isLoading || !inputQuestion.trim()}
              className="bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 disabled:opacity-50 text-white font-semibold px-5 py-3 rounded-xl flex items-center justify-center transition-all shadow-lg shadow-teal-500/20"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
