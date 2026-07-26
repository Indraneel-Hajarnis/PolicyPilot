import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const TRANSLATIONS = {
  en: {
    // Navigation
    navBrand: 'PolicyPilot',
    navUpload: 'Upload Document',
    navChat: 'Q&A Assistant',
    navSummary: 'Policy Summaries',
    navDocuments: 'Document Library',
    navAnalytics: 'Analytics',
    serverOnline: 'API Online',
    serverOffline: 'API Offline',

    // Language Selector
    langLabel: 'Target Language',
    english: 'English (EN)',
    hindi: 'Hindi - हिन्दी (HI)',
    marathi: 'Marathi - मराठी (MR)',

    // Upload Page
    uploadTitle: 'Policy Document Ingestion',
    uploadSubtitle: 'Upload PDF policy documents to extract, chunk, embed, and index for tri-lingual AI analysis.',
    dropzoneText: 'Drag & drop your policy PDF here, or click to browse',
    uploading: 'Ingesting & Indexing Document...',
    uploadSuccess: 'Document successfully indexed into vector store!',
    uploadError: 'Failed to upload document. Please check the file.',
    detectedLang: 'Detected Language:',
    chunksCreated: 'Text Chunks Created:',

    // Chat Page
    chatTitle: 'AI Policy Q&A Assistant',
    chatSubtitle: 'Ask detailed questions about your uploaded policies in English, Hindi, or Marathi.',
    inputPlaceholder: 'Ask a question about your policies (e.g. What is the claim window?)...',
    askButton: 'Ask Question',
    clearChat: 'Clear Conversation',
    confidenceScore: 'Confidence Score:',
    sourcesHeading: 'Retrieved Source Passages',
    relatedDocsHeading: 'Related Documents',
    readAloud: 'Read Answer Aloud',
    stopSpeech: 'Stop Speaking',
    copyAnswer: 'Copy Answer',
    suggestedQuestions: 'Suggested Questions:',
    sampleQ1: 'What are the main coverage limits and claim procedures?',
    sampleQ2: 'What is the policy cancellation and refund process?',
    sampleQ3: 'What exclusion rules apply to pre-existing conditions?',

    // Summary Page
    summaryTitle: 'Structured Policy Summaries',
    summarySubtitle: 'Generate executive briefings, key policy points, and action items in English, Hindi, or Marathi.',
    selectDoc: 'Select Document to Summarize:',
    generateSummary: 'Generate Summary',
    exportPdf: 'Export Summary PDF',
    exportJson: 'Export JSON Data',
    keyPoints: 'Key Policy Takeaways',
    importantDates: 'Important Dates & Deadlines',
    actionItems: 'Action Items & Compliance Steps',
    executiveSummary: 'Full Executive Summary',
    sections: 'Policy Sections',

    // Documents Page
    docsTitle: 'Policy Document Library',
    docsSubtitle: 'Manage uploaded policies, inspect extracted text chunks, and filter by language.',
    searchPlaceholder: 'Search documents by title or keyword...',
    filterAll: 'All Languages',
    noDocs: 'No policy documents uploaded yet.',
    deleteDoc: 'Delete Document',
    viewChunks: 'Inspect Chunks',
    chunkCount: 'Chunks',

    // Analytics Page
    analyticsTitle: 'Platform Intelligence & Audit',
    analyticsSubtitle: 'Real-time overview of document volume, vector index capacity, query counts, and language distribution.',
    statTotalDocs: 'Total Policies',
    statTotalChunks: 'Indexed Chunks',
    statTotalQueries: 'Queries Answered',
    statAvgConfidence: 'Average Confidence',
    statVectorSize: 'Vector Index Size',
    recentQueries: 'Recent Q&A Activity Logs',
    langDistribution: 'Tri-Lingual Document Distribution',

    // Common
    loading: 'Loading...',
    close: 'Close',
    back: 'Back',
  },

  hi: {
    // Navigation
    navBrand: 'पॉलिसीपायलट (PolicyPilot)',
    navUpload: 'दस्तावेज़ अपलोड करें',
    navChat: 'प्रश्नोत्तर सहायक (Q&A)',
    navSummary: 'पॉलिसी सारांश',
    navDocuments: 'दस्तावेज़ लाइब्रेरी',
    navAnalytics: 'विश्लेषण (Analytics)',
    serverOnline: 'एपीआई सक्रिय',
    serverOffline: 'एपीआई बंद',

    // Language Selector
    langLabel: 'लक्ष्य भाषा:',
    english: 'अंग्रेज़ी (English)',
    hindi: 'हिन्दी (Hindi)',
    marathi: 'मराठी (Marathi)',

    // Upload Page
    uploadTitle: 'पॉलिसी दस्तावेज़ अपलोड और प्रोसेसिंग',
    uploadSubtitle: 'त्रिभाषी एआई विश्लेषण के लिए पीडीएफ पॉलिसी दस्तावेज़ अपलोड करें।',
    dropzoneText: 'अपनी पॉलिसी पीडीएफ फाइल यहाँ खींचें और छोड़ें, या ब्राउज़ करने के लिए क्लिक करें',
    uploading: 'दस्तावेज़ को इंडेक्स किया जा रहा है...',
    uploadSuccess: 'दस्तावेज़ सफलतापूर्वक वेक्टर स्टोर में इंडेक्स हो गया!',
    uploadError: 'दस्तावेज़ अपलोड विफल रहा। कृपया फ़ाइल जांचें।',
    detectedLang: 'पहचानी गई भाषा:',
    chunksCreated: 'बनाए गए टेक्स्ट चंक्स:',

    // Chat Page
    chatTitle: 'एआई पॉलिसी प्रश्नोत्तर सहायक',
    chatSubtitle: 'अपनी अपलोड की गई नीतियों के बारे में अंग्रेज़ी, हिन्दी या मराठी में सवाल पूछें।',
    inputPlaceholder: 'अपनी पॉलिसी के बारे में प्रश्न पूछें (उदा. दावा अवधि क्या है?)...',
    askButton: 'प्रश्न पूछें',
    clearChat: 'बातचीत साफ़ करें',
    confidenceScore: 'विश्वसनीयता स्कोर:',
    sourcesHeading: 'प्राप्त स्रोत संदर्भ',
    relatedDocsHeading: 'संबंधित दस्तावेज़',
    readAloud: 'उत्तर सुनकर पढ़ें (बोलें)',
    stopSpeech: 'आवाज बंद करें',
    copyAnswer: 'उत्तर कॉपी करें',
    suggestedQuestions: 'सुझाए गए प्रश्न:',
    sampleQ1: 'मुख्य कवरेज सीमाएं और दावा प्रक्रियाएं क्या हैं?',
    sampleQ2: 'पॉलिसी रद्द करने और रिफंड की प्रक्रिया क्या है?',
    sampleQ3: 'पहले से मौजूद बीमारियों के लिए क्या नियम लागू होते हैं?',

    // Summary Page
    summaryTitle: 'संरचित नीति सारांश',
    summarySubtitle: 'अंग्रेज़ी, हिन्दी या मराठी में कार्यकारी ब्रीफिंग और मुख्य बिंदु तैयार करें।',
    selectDoc: 'सारांश के लिए दस्तावेज़ चुनें:',
    generateSummary: 'सारांश तैयार करें',
    exportPdf: 'पीडीएफ डाउनलोड करें',
    exportJson: 'जेसन डेटा निर्यात करें',
    keyPoints: 'मुख्य नीति बिंदु',
    importantDates: 'महत्वपूर्ण तिथियां और समय सीमाएं',
    actionItems: 'कार्रवाई योग्य कदम और अनुपालन',
    executiveSummary: 'पूर्ण कार्यकारी सारांश',
    sections: 'नीति अनुभाग',

    // Documents Page
    docsTitle: 'पॉलिसी दस्तावेज़ लाइब्रेरी',
    docsSubtitle: 'अपलोड की गई नीतियों का प्रबंधन करें, टेक्स्ट चंक्स देखें और भाषा के आधार पर फ़िल्टर करें।',
    searchPlaceholder: 'शीर्षक या कीवर्ड खोजें...',
    filterAll: 'सभी भाषाएँ',
    noDocs: 'अभी तक कोई पॉलिसी दस्तावेज़ अपलोड नहीं किया गया है।',
    deleteDoc: 'दस्तावेज़ हटाएं',
    viewChunks: 'चंक्स देखें',
    chunkCount: 'चंक्स',

    // Analytics Page
    analyticsTitle: 'प्लेटफॉर्म इंटेलिजेंस और ऑडिट',
    analyticsSubtitle: 'दस्तावेज़ की मात्रा, वेक्टर इंडेक्स क्षमता और भाषाओं के वितरण का वास्तविक समय अवलोकन।',
    statTotalDocs: 'कुल नीतियां',
    statTotalChunks: 'इंडेक्स किए गए चंक्स',
    statTotalQueries: 'उत्तर दिए गए प्रश्न',
    statAvgConfidence: 'औसत विश्वसनीयता',
    statVectorSize: 'वेक्टर इंडेक्स आकार',
    recentQueries: 'हालिया प्रश्नोत्तर गतिविधियां',
    langDistribution: 'त्रिभाषी दस्तावेज़ वितरण',

    // Common
    loading: 'लोड हो रहा है...',
    close: 'बंद करें',
    back: 'वापस जाएं',
  },

  mr: {
    // Navigation
    navBrand: 'पॉलिसीपायलट (PolicyPilot)',
    navUpload: 'दस्तऐवज अपलोड करा',
    navChat: 'प्रश्नोत्तर सहाय्यक (Q&A)',
    navSummary: 'पॉलिसी सारांश',
    navDocuments: 'दस्तऐवज लायब्ररी',
    navAnalytics: 'विश्लेषण (Analytics)',
    serverOnline: 'एपीआय सक्रिय',
    serverOffline: 'एपीआय बंद',

    // Language Selector
    langLabel: 'लक्ष्य भाषा:',
    english: 'इंग्रजी (English)',
    hindi: 'हिंदी (Hindi)',
    marathi: 'मराठी (Marathi)',

    // Upload Page
    uploadTitle: 'पॉलिसी दस्तऐवज अपलोड आणि प्रक्रिया',
    uploadSubtitle: 'त्रिभाषिक एआय विश्लेषणासाठी पीडीएफ पॉलिसी दस्तऐवज अपलोड करा.',
    dropzoneText: 'तुमची पॉलिसी पीडीएफ फाईल येथे ड्रॅग आणि ड्रॉप करा, किंवा ब्राउझ करण्यासाठी क्लिक करा',
    uploading: 'दस्तऐवज इंडेक्स केला जात आहे...',
    uploadSuccess: 'दस्तऐवज यशस्वीरित्या व्हेक्टर स्टोअरमध्ये इंडेक्स झाला!',
    uploadError: 'दस्तऐवज अपलोड अयशस्वी. कृपया फाईल तपासा.',
    detectedLang: 'ओळखलेली भाषा:',
    chunksCreated: 'तयार केलेले मजकूर चंक्स:',

    // Chat Page
    chatTitle: 'एआय पॉलिसी प्रश्नोत्तर सहाय्यक',
    chatSubtitle: 'तुमच्या अपलोड केलेल्या पॉलिसींबद्दल इंग्रजी, हिंदी किंवा मराठीत प्रश्न विचारा.',
    inputPlaceholder: 'तुमच्या पॉलिसीबद्दल प्रश्न विचारा (उदा. क्लेम कालावधी काय आहे?)...',
    askButton: 'प्रश्न विचारा',
    clearChat: 'संभाषण साफ करा',
    confidenceScore: 'विश्वासार्हता स्कोर:',
    sourcesHeading: 'संदर्भ स्रोत',
    relatedDocsHeading: 'संबंधित दस्तऐवज',
    readAloud: 'उत्तर ऐका (बोलून दाखवा)',
    stopSpeech: 'आवाज थांबवा',
    copyAnswer: 'उत्तर कॉपी करा',
    suggestedQuestions: 'सुचवलेले प्रश्न:',
    sampleQ1: 'मुख्य कव्हरेज मर्यादा आणि क्लेम प्रक्रिया काय आहेत?',
    sampleQ2: 'पॉलिसी रद्द करणे आणि परतावा प्रक्रिया काय आहे?',
    sampleQ3: 'आधीपासून असलेल्या आजारांसाठी कोणते नियम लागू होतात?',

    // Summary Page
    summaryTitle: 'संरचित धोरण सारांश',
    summarySubtitle: 'इंग्रजी, हिंदी किंवा मराठीत कार्यकारी ब्रीफिंग आणि महत्वाचे मुद्दे तयार करा.',
    selectDoc: 'सारांशासाठी दस्तऐवज निवडा:',
    generateSummary: 'सारांश तयार करा',
    exportPdf: 'पीडीएफ डाउनलोड करा',
    exportJson: 'JSON डेटा निर्यातीत करा',
    keyPoints: 'मुख्य धोरण मुद्दे',
    importantDates: 'महत्वाच्या तारखा आणि मुदती',
    actionItems: 'कारवाईचे मुद्दे आणि अनुपालन',
    executiveSummary: 'पूर्ण कार्यकारी सारांश',
    sections: 'धोरण विभाग',

    // Documents Page
    docsTitle: 'पॉलिसी दस्तऐवज लायब्ररी',
    docsSubtitle: 'अपलोड केलेल्या पॉलिसींचे व्यवस्थापन करा, मजकूर चंक्स तपासा आणि भाषेनुसार फिल्टर करा.',
    searchPlaceholder: 'शीर्षक किंवा कीवर्ड शोधा...',
    filterAll: 'सर्व भाषा',
    noDocs: 'अजून कोणताही पॉलिसी दस्तऐवज अपलोड केलेला नाही.',
    deleteDoc: 'दस्तऐवज हटवा',
    viewChunks: 'चंक्स पहा',
    chunkCount: 'चंक्स',

    // Analytics Page
    analyticsTitle: 'प्लॅटफॉर्म इंटेलिजन्स आणि ऑडिट',
    analyticsSubtitle: 'दस्तऐवजांची संख्या, व्हेक्टर निर्देशांक क्षमता आणि भाषांच्या वितरणाचा रिअल-टाइम आढावा.',
    statTotalDocs: 'एकूण पॉलिसी',
    statTotalChunks: 'इंडेक्स केलेले चंक्स',
    statTotalQueries: 'उत्तरे दिलेले प्रश्न',
    statAvgConfidence: 'सरासरी विश्वासार्हता',
    statVectorSize: 'व्हेक्टर निर्देशांक आकार',
    recentQueries: 'अलीकडील प्रश्नोत्तर नोंदी',
    langDistribution: 'त्रिभाषिक दस्तऐवज वितरण',

    // Common
    loading: 'लोड होत आहे...',
    close: 'बंद करा',
    back: 'मागे जा',
  },
};

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('policypilot_lang') || 'en';
  });

  useEffect(() => {
    localStorage.setItem('policypilot_lang', language);
  }, [language]);

  const t = (key) => {
    const langDict = TRANSLATIONS[language] || TRANSLATIONS.en;
    return langDict[key] || TRANSLATIONS.en[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
