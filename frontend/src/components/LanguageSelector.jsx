import React from 'react';
import { Globe } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const LANGUAGES = [
  { code: 'en', flag: '🇬🇧', label: 'English (EN)' },
  { code: 'hi', flag: '🇮🇳', label: 'Hindi — हिन्दी (HI)' },
  { code: 'mr', flag: '🇮🇳', label: 'Marathi — मराठी (MR)' },
];

export default function LanguageSelector({ selectedLanguage, onChange, label }) {
  const { language, setLanguage, t } = useLanguage();
  const currentLang = selectedLanguage || language;

  const handleChange = (e) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    if (onChange) {
      onChange(newLang);
    }
  };

  return (
    <div className="flex items-center gap-2 bg-slate-800/80 border border-teal-500/30 hover:border-teal-400/60 transition-all rounded-xl px-3 py-1.5 text-xs text-slate-200 shadow-sm backdrop-blur-md">
      <Globe className="w-4 h-4 text-teal-400 shrink-0 animate-pulse" />
      <span className="hidden sm:inline text-slate-400 font-medium">{label || t('langLabel')}:</span>
      <select
        value={currentLang}
        onChange={handleChange}
        className="bg-slate-900 text-teal-300 focus:outline-none cursor-pointer font-semibold py-0.5 rounded"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code} className="bg-slate-900 text-slate-100 py-1">
            {lang.flag} {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
}
