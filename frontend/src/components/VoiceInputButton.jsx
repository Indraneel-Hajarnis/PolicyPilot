import React, { useState, useEffect } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function VoiceInputButton({ onSpeechInput, disabled }) {
  const { language, t } = useLanguage();
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;

      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript && onSpeechInput) {
          onSpeechInput(transcript);
        }
        setIsListening(false);
      };

      rec.onerror = (err) => {
        console.warn('Speech recognition error:', err);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      setRecognition(rec);
    }
  }, [onSpeechInput]);

  const toggleListening = () => {
    if (!recognition) {
      alert(t('speechNotSupported'));
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      if (language === 'hi') {
        recognition.lang = 'hi-IN';
      } else if (language === 'mr') {
        recognition.lang = 'mr-IN';
      } else {
        recognition.lang = 'en-US';
      }

      try {
        recognition.start();
        setIsListening(true);
      } catch (err) {
        console.error('Speech recognition start failed:', err);
      }
    }
  };

  return (
    <button
      type="button"
      onClick={toggleListening}
      disabled={disabled}
      title={isListening ? t('listeningStop') : t('clickToSpeak')}
      className={`p-3 rounded-xl flex items-center justify-center transition-all shadow-md ${
        isListening
          ? 'bg-rose-500 text-white animate-pulse shadow-rose-500/30'
          : 'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-teal-300 border border-slate-700'
      }`}
    >
      {isListening ? <MicOff className="w-5 h-5 text-white" /> : <Mic className="w-5 h-5" />}
    </button>
  );
}
