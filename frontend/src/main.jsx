import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AppContextProvider } from './context/AppContext';
import { LanguageProvider } from './context/LanguageContext';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <LanguageProvider>
        <AppContextProvider>
          <App />
        </AppContextProvider>
      </LanguageProvider>
    </BrowserRouter>
  </React.StrictMode>
);
