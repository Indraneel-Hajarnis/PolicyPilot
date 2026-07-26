import { createContext, useContext, useMemo, useState } from 'react';

const translations = {
  en: {
    langLabel: 'Language',
    navUpload: 'Upload',
    navChat: 'Chat',
    navSummary: 'Summary',
    navDocuments: 'Documents',
    navAnalytics: 'Analytics',
    serverOnline: 'Server online',
    sampleQ1: 'What are the key obligations in this policy?',
    sampleQ2: 'Summarize the main risks and exceptions.',
    sampleQ3: 'Show me the clauses related to compliance.',
    clearChat: 'Clear',
    chatTitle: 'Ask about your policy documents',
    chatSubtitle: 'Upload a policy and ask questions in natural language.',
    suggestedQuestions: 'Suggested questions',
    inputPlaceholder: 'Ask a question about the policy...',
    docsTitle: 'Documents',
    docsSubtitle: 'Manage uploaded policy PDFs and review their content.',
    uploadTitle: 'Upload a policy',
    uploadSubtitle: 'Drop a PDF to index it for search and summarization.',
    searchPlaceholder: 'Search documents...',
    filterAll: 'All',
    noDocs: 'No documents yet',
    deleteDoc: 'Delete',
    selectDoc: 'Select a document',
    generateSummary: 'Generate summary',
    summaryTitle: 'Policy summary',
    summarySubtitle: 'Generate structured summaries for your policies.',
    exportJson: 'Export JSON',
    copyAnswer: 'Copy answer',
    stopSpeech: 'Stop speech',
    readAloud: 'Read aloud',
    sourcesHeading: 'Sources',
    keyPoints: 'Key points',
    sections: 'Sections',
    importantDates: 'Important dates',
    actionItems: 'Action items',
    executiveSummary: 'Executive summary',
  },
  hi: {
    langLabel: 'भाषा',
    navUpload: 'अपलोड',
    navChat: 'चैट',
    navSummary: 'सारांश',
    navDocuments: 'दस्तावेज़',
    navAnalytics: 'विश्लेषण',
    serverOnline: 'सर्वर ऑनलाइन',
    sampleQ1: 'इस नीति में मुख्य दायित्व क्या हैं?',
    sampleQ2: 'मुख्य जोखिम और अपवादों का सारांश बताइए।',
    sampleQ3: 'Compliance से संबंधित धाराओं को दिखाइए।',
    clearChat: 'साफ करें',
    chatTitle: 'अपने नीति दस्तावेजों के बारे में पूछें',
    chatSubtitle: 'एक नीति अपलोड करें और प्राकृतिक भाषा में प्रश्न पूछें।',
    suggestedQuestions: 'सुझाए गए प्रश्न',
    inputPlaceholder: 'नीति के बारे में कोई प्रश्न पूछें...',
    docsTitle: 'दस्तावेज़',
    docsSubtitle: 'अपलोड किए गए PDF प्रबंधित करें और उनकी सामग्री देखें।',
    uploadTitle: 'नीति अपलोड करें',
    uploadSubtitle: 'खोज और सारांश के लिए PDF डालें।',
    searchPlaceholder: 'दस्तावेज़ खोजें...',
    filterAll: 'सभी',
    noDocs: 'अभी कोई दस्तावेज़ नहीं',
    deleteDoc: 'हटाएं',
    selectDoc: 'एक दस्तावेज़ चुनें',
    generateSummary: 'सारांश बनाएं',
    summaryTitle: 'नीति सारांश',
    summarySubtitle: 'अपनी नीतियों के लिए संरचित सारांश बनाएँ।',
    exportJson: 'JSON निर्यात करें',
    copyAnswer: 'उत्तर कॉपी करें',
    stopSpeech: 'भाषण रोकें',
    readAloud: 'जोर से पढ़ें',
    sourcesHeading: 'स्रोत',
    keyPoints: 'मुख्य बिंदु',
    sections: 'अनुभाग',
    importantDates: 'महत्वपूर्ण तिथियाँ',
    actionItems: 'कार्रवाई की वस्तुएँ',
    executiveSummary: 'कार्यकारी सारांश',
  },
  mr: {
    langLabel: 'भाषा',
    navUpload: 'अपलोड',
    navChat: 'चॅट',
    navSummary: 'सारांश',
    navDocuments: 'दस्तऐवज',
    navAnalytics: 'विश्लेषण',
    serverOnline: 'सर्वर ऑनलाइन',
    sampleQ1: 'या धोरणात मुख्य जबाबदाऱ्या काय आहेत?',
    sampleQ2: 'मुख्य जोखीम आणि अपवादांचा सारांश सांगा.',
    sampleQ3: 'Compliance संबंधित तरतुदी दाखवा.',
    clearChat: 'स्वच्छ करा',
    chatTitle: 'तुमच्या धोरण दस्तऐवजांबद्दल विचारा',
    chatSubtitle: 'धोरण अपलोड करा आणि नैसर्गिक भाषेत प्रश्न विचारा.',
    suggestedQuestions: 'सूचित केलेले प्रश्न',
    inputPlaceholder: 'धोरणाबद्दल प्रश्न विचारा...',
    docsTitle: 'दस्तऐवज',
    docsSubtitle: 'अपलोड केलेले PDF व्यवस्थापित करा आणि त्यांची Inhalte पहा.',
    uploadTitle: 'धोरण अपलोड करा',
    uploadSubtitle: 'शोध आणि सारांशासाठी PDF टाका.',
    searchPlaceholder: 'दस्तऐवज शोधा...',
    filterAll: 'सर्व',
    noDocs: 'अद्याप कोणतेही दस्तऐवज नाहीत',
    deleteDoc: 'हटवा',
    selectDoc: 'एक दस्तऐवज निवडा',
    generateSummary: 'सारांश तयार करा',
    summaryTitle: 'धोरण सारांश',
    summarySubtitle: 'तुमच्या धोरणांसाठी संरचित सारांश तयार करा.',
    exportJson: 'JSON निर्यात करा',
    copyAnswer: 'उत्तर कॉपी करा',
    stopSpeech: 'भाषण थांबवा',
    readAloud: 'जोरात वाचा',
    sourcesHeading: 'स्रोत',
    keyPoints: 'मुख्य मुद्दे',
    sections: 'विभाग',
    importantDates: 'महत्वाच्या तारखा',
    actionItems: 'कृती आयटम',
    executiveSummary: 'कार्यकारी सारांश',
  },
};

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('en');

  const value = useMemo(() => {
    const dict = translations[language] || translations.en;
    return {
      language,
      setLanguage,
      t: (key) => dict[key] || translations.en[key] || key,
    };
  }, [language]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return ctx;
}

export default LanguageContext;