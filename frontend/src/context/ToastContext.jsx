import { createContext, useCallback, useContext, useState } from 'react';

const ToastContext = createContext(null);

let _id = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ message, type = 'info', duration = 4000 }) => {
    const id = ++_id;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = {
    success: (msg, opts) => addToast({ message: msg, type: 'success', ...opts }),
    error: (msg, opts) => addToast({ message: msg, type: 'error', ...opts }),
    info: (msg, opts) => addToast({ message: msg, type: 'info', ...opts }),
    warning: (msg, opts) => addToast({ message: msg, type: 'warning', ...opts }),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within a ToastProvider');
  return ctx;
}

// ── Toast Container + Item ────────────────────────────────────────────────────

function ToastContainer({ toasts, onRemove }) {
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3 items-end pointer-events-none">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onRemove={onRemove} />
      ))}
    </div>
  );
}

const typeStyles = {
  success: {
    border: 'border-emerald-500/40',
    bg: 'bg-emerald-500/10',
    bar: 'bg-emerald-400',
    icon: '✓',
    iconClass: 'text-emerald-400 bg-emerald-500/20',
    text: 'text-emerald-300',
  },
  error: {
    border: 'border-rose-500/40',
    bg: 'bg-rose-500/10',
    bar: 'bg-rose-400',
    icon: '✕',
    iconClass: 'text-rose-400 bg-rose-500/20',
    text: 'text-rose-300',
  },
  warning: {
    border: 'border-amber-500/40',
    bg: 'bg-amber-500/10',
    bar: 'bg-amber-400',
    icon: '⚠',
    iconClass: 'text-amber-400 bg-amber-500/20',
    text: 'text-amber-300',
  },
  info: {
    border: 'border-teal-500/40',
    bg: 'bg-teal-500/10',
    bar: 'bg-teal-400',
    icon: 'ℹ',
    iconClass: 'text-teal-400 bg-teal-500/20',
    text: 'text-teal-300',
  },
};

function ToastItem({ toast, onRemove }) {
  const s = typeStyles[toast.type] || typeStyles.info;
  return (
    <div
      className={`pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-2xl border ${s.border} ${s.bg} backdrop-blur-2xl shadow-2xl max-w-sm w-full animate-slide-in-right`}
      style={{ animation: 'slideInRight 0.25s ease-out' }}
    >
      <span className={`w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 ${s.iconClass}`}>
        {s.icon}
      </span>
      <p className={`text-sm font-medium leading-snug flex-1 ${s.text}`}>{toast.message}</p>
      <button
        onClick={() => onRemove(toast.id)}
        className="text-slate-500 hover:text-slate-300 transition-colors text-lg leading-none mt-0.5 shrink-0"
      >
        ×
      </button>
    </div>
  );
}

export default ToastContext;
