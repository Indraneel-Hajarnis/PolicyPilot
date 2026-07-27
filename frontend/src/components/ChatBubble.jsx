import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, BookOpen, Volume2, VolumeX, Copy, Check, ThumbsUp, ThumbsDown } from 'lucide-react';
import ConfidenceBadge from './ConfidenceBadge';
import SourceCitation from './SourceCitation';
import { useLanguage } from '../context/LanguageContext';

export default function ChatBubble({ message }) {
  const isUser = message.role === 'user';
  const { language, t } = useLanguage();
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null); // 'up' | 'down' | null

  const handleSpeech = () => {
    if (!('speechSynthesis' in window)) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const cleanText = message.content.replace(/[*#_`[\]()]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);

    if (language === 'hi') {
      utterance.lang = 'hi-IN';
    } else if (language === 'mr') {
      utterance.lang = 'mr-IN';
    } else {
      utterance.lang = 'en-US';
    }

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-6 animate-slide-up`}>
      {/* Avatar */}
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-lg ${
          isUser
            ? 'bg-gradient-to-tr from-teal-500 to-emerald-400 text-white'
            : 'bg-gradient-to-tr from-slate-800 to-slate-900 text-teal-300 border border-teal-500/40 shadow-teal-500/10'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Content Container */}
      <div className={`max-w-3xl space-y-3 ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Bubble */}
        <div
          className={`p-4 sm:p-5 rounded-2xl text-sm sm:text-base leading-relaxed backdrop-blur-xl shadow-xl transition-all ${
            isUser
              ? 'bg-gradient-to-r from-teal-600/90 to-emerald-600/90 text-white rounded-tr-none border border-teal-400/30'
              : 'bg-slate-900/90 text-slate-100 border border-slate-700/80 rounded-tl-none shadow-2xl'
          }`}
        >
          {/* Header info & action buttons for assistant */}
          {!isUser && (
            <div className="flex items-center justify-between pb-2.5 mb-2.5 border-b border-slate-700/60">
              <span className="text-xs font-bold uppercase tracking-wider text-teal-400 flex items-center gap-1.5">
                <Bot className="w-3.5 h-3.5" /> {t('policyAssistant')}
              </span>
              <div className="flex items-center gap-2">
                {message.confidence !== undefined && (
                  <ConfidenceBadge confidence={message.confidence} />
                )}
                
                {/* Speech Button */}
                <button
                  onClick={handleSpeech}
                  title={isSpeaking ? t('stopSpeech') : t('readAloud')}
                  className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-teal-300 transition-colors"
                >
                  {isSpeaking ? (
                    <VolumeX className="w-4 h-4 text-rose-400 animate-bounce" />
                  ) : (
                    <Volume2 className="w-4 h-4 text-teal-400" />
                  )}
                </button>

                {/* Copy Button */}
                <button
                  onClick={handleCopy}
                  title={t('copyAnswer')}
                  className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-teal-300 transition-colors"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>

                {/* Thumbs Feedback */}
                <div className="flex items-center gap-1 pl-1 border-l border-slate-700/60">
                  <button
                    onClick={() => setFeedback(feedback === 'up' ? null : 'up')}
                    className={`p-1 rounded-lg transition-colors ${
                      feedback === 'up' ? 'text-emerald-400 bg-emerald-500/10' : 'text-slate-500 hover:text-slate-300'
                    }`}
                    title={t('helpfulResponse')}
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setFeedback(feedback === 'down' ? null : 'down')}
                    className={`p-1 rounded-lg transition-colors ${
                      feedback === 'down' ? 'text-rose-400 bg-rose-500/10' : 'text-slate-500 hover:text-slate-300'
                    }`}
                    title={t('needsImprovement')}
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Markdown Content */}
          <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        {/* Sources section if present */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="space-y-2 pt-1 pl-1">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400">
              <BookOpen className="w-3.5 h-3.5 text-teal-400" />
              <span>{t('sourcesHeading')} ({message.sources.length})</span>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {message.sources.map((src, i) => (
                <SourceCitation key={i} source={src} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
