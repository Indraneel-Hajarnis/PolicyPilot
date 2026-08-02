import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, ChevronDown, ChevronUp, Tag, Building2, Hash } from 'lucide-react';
import { uploadDocument } from '../api/client';
import { useLanguage } from '../context/LanguageContext';

// ── Lightweight client-side PDF text extractor (first 3KB of readable text) ──
async function extractPdfHeaderText(file) {
  try {
    const buffer = await file.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    // Decode a chunk of the binary as latin-1 to find readable text patterns
    const chunk = new TextDecoder('latin1').decode(bytes.slice(0, 8000));
    return chunk;
  } catch {
    return '';
  }
}

// ── Heuristic parsers ─────────────────────────────────────────────────────────
function guessGrNumber(text) {
  // Matches patterns like: GR-2024/CR-102, No.GR/2024/102, शासन निर्णय क्र.
  const patterns = [
    /(?:GR[\/\-\s]?(?:No\.?)?\s*)([A-Z0-9\/\-]+)/i,
    /(?:Government Resolution No\.?\s*)([A-Z0-9\/\-]+)/i,
    /(?:G\.R\. No\.?\s*)([A-Z0-9\/\-]+)/i,
    /(?:शासन निर्णय क्र[.:]\s*)([A-Z0-9\/\-]+)/i,
    /(?:शासन परिपत्रक क्र[.:]\s*)([A-Z0-9\/\-]+)/i,
    /(?:GR\/|CR\/)([A-Z0-9\/\-]+)/i,
  ];
  for (const re of patterns) {
    const m = text.match(re);
    if (m && m[1] && m[1].length > 2 && m[1].length < 30) {
      return m[1].trim().replace(/\s+/g, '');
    }
  }
  return '';
}

function guessDepartment(text) {
  const patterns = [
    /(?:Department of|Department:)\s*([A-Za-z &]+)/i,
    /(?:विभाग[:\s]+)([^\n,।]+)/,
    /(?:खाते[:\s]+)([^\n,।]+)/,
    /(?:Ministry of)\s*([A-Za-z &]+)/i,
  ];
  for (const re of patterns) {
    const m = text.match(re);
    if (m && m[1] && m[1].trim().length > 3) {
      return m[1].trim().slice(0, 60);
    }
  }
  return '';
}

function guessCategory(text) {
  const lower = text.toLowerCase();
  if (/government resolution|शासन निर्णय|शासकीय ठराव/.test(lower)) return 'Resolution';
  if (/circular|परिपत्र/.test(lower)) return 'Circular';
  if (/notification|अधिसूचना/.test(lower)) return 'Notification';
  if (/amendment|संशोधन|दुरुस्ती/.test(lower)) return 'Amendment';
  if (/guideline|मार्गदर्शक/.test(lower)) return 'Guidelines';
  if (/policy|नीति|धोरण/.test(lower)) return 'Policy';
  return '';
}

// ─────────────────────────────────────────────────────────────────────────────

export default function UploadDropzone({ onUploadSuccess }) {
  const { t } = useLanguage();
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [successFile, setSuccessFile] = useState(null);

  // Optional Metadata state
  const [showMetadata, setShowMetadata] = useState(false);
  const [department, setDepartment] = useState('');
  const [documentNumber, setDocumentNumber] = useState('');
  const [category, setCategory] = useState('');
  const [autoFilling, setAutoFilling] = useState(false);

  // ── Auto-fill metadata from PDF on drop ──────────────────────────────────
  const autoFillFromFile = async (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) return {};
    setAutoFilling(true);
    try {
      const text = await extractPdfHeaderText(file);
      const grNum = guessGrNumber(text);
      const dept = guessDepartment(text);
      const cat = guessCategory(text);
      if (grNum || dept || cat) {
        setShowMetadata(true); // expand so user can see what was filled
        if (grNum) setDocumentNumber(grNum);
        if (dept) setDepartment(dept);
        if (cat) setCategory(cat);
      }
      // Return the extracted values directly so onDrop can use them
      // immediately without waiting for React state to re-render
      return { grNum, dept, cat };
    } catch {
      return {};
    } finally {
      setAutoFilling(false);
    }
  };

  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];

      // Auto-fill metadata before upload starts
      // Use returned values directly to avoid React stale-closure issue
      const extracted = await autoFillFromFile(file);

      // Merge: prefer any existing user-typed value, fall back to auto-extracted
      const finalDept = department.trim() || extracted.dept || '';
      const finalGr = documentNumber.trim() || extracted.grNum || '';
      const finalCat = category.trim() || extracted.cat || '';

      setUploading(true);
      setProgress(0);
      setError(null);
      setSuccessFile(null);

      try {
        const metadata = {
          department: finalDept || null,
          document_number: finalGr || null,
          category: finalCat || null,
        };

        const res = await uploadDocument(
          file,
          (percent) => { setProgress(percent); },
          metadata
        );
        setSuccessFile(res.filename);
        if (onUploadSuccess) onUploadSuccess(res);
      } catch (err) {
        console.error('Upload error:', err);
        const data = err.response?.data;
        let msg = null;
        if (typeof data?.detail === 'string') {
          msg = data.detail;
        } else if (Array.isArray(data?.detail) && data.detail[0]?.msg) {
          msg = data.detail[0].msg;
        } else if (typeof data?.error === 'string') {
          msg = data.error;
        } else if (err.message) {
          msg = err.message;
        }
        setError(msg || t('uploadProcessError'));
      } finally {
        setUploading(false);
      }
    },
    [onUploadSuccess, t, department, documentNumber, category]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: false,
    disabled: uploading,
  });

  return (
    <div className="w-full space-y-4">
      {/* Dropzone area */}
      <div
        {...getRootProps()}
        className={`glass-card p-8 sm:p-12 text-center border-2 border-dashed rounded-3xl cursor-pointer transition-all duration-300 ${
          isDragActive
            ? 'border-teal-400 bg-teal-500/10 scale-[1.01]'
            : 'border-white/15 hover:border-teal-400/40 hover:bg-white/[0.07]'
        } ${uploading ? 'pointer-events-none opacity-80' : ''}`}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center justify-center space-y-4">
          {/* Icon */}
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-teal-500/20 to-navy-600/30 border border-teal-500/30 flex items-center justify-center text-teal-400 shadow-xl group-hover:scale-110 transition-transform">
            {uploading ? (
              <Loader2 className="w-10 h-10 animate-spin text-teal-400" />
            ) : (
              <UploadCloud className="w-10 h-10" />
            )}
          </div>

          {/* Text */}
          <div className="space-y-1">
            <h3 className="text-xl font-bold text-white">
              {isDragActive ? t('uploadDropzoneDropHere') : t('uploadDropzoneTitle')}
            </h3>
            <p className="text-sm text-white/50 max-w-sm mx-auto">
              {t('uploadDropzoneInstructions')}
            </p>
          </div>

          {/* File format indicator */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-white/60">
            <FileText className="w-3.5 h-3.5 text-teal-400" />
            <span>{t('uploadDropzonePdfSupported')}</span>
          </div>

          {/* Progress bar */}
          {uploading && (
            <div className="w-full max-w-md space-y-2 pt-2">
              <div className="h-2 w-full bg-surface-800 rounded-full overflow-hidden border border-white/10">
                <div
                  className="h-full bg-gradient-to-r from-teal-500 to-teal-300 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-teal-300 font-medium">
                {t('uploadAnalyzing').replace('{progress}', String(progress))}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Collapsible Optional Metadata Form */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 transition-all">
        <button
          type="button"
          onClick={() => setShowMetadata(!showMetadata)}
          className="w-full flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-teal-300 transition-colors"
        >
          <span className="flex items-center gap-2">
            <Tag className="w-4 h-4 text-teal-400" />
            {t('addMetadata')}
            {autoFilling && <Loader2 className="w-3 h-3 animate-spin text-teal-400" />}
          </span>
          {showMetadata ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showMetadata && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 border-t border-slate-800/80 mt-3">
            <div className="space-y-1">
              <label className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                <Building2 className="w-3 h-3 text-teal-400" /> {t('departmentLabel')}
              </label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder={t('departmentPlaceholder')}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                <Hash className="w-3 h-3 text-teal-400" /> {t('grNumberLabel')}
              </label>
              <input
                type="text"
                value={documentNumber}
                onChange={(e) => setDocumentNumber(e.target.value)}
                placeholder={t('grNumberPlaceholder')}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                <Tag className="w-3 h-3 text-teal-400" /> {t('categoryLabel')}
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
              >
                <option value="">{t('categoryAutoDetect')}</option>
                <option value="Resolution">{t('catResolution')}</option>
                <option value="Circular">{t('catCircular')}</option>
                <option value="Policy">{t('catPolicy')}</option>
                <option value="Notification">{t('catNotification')}</option>
                <option value="Amendment">{t('catAmendment')}</option>
                <option value="Guidelines">{t('catGuidelines')}</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Feedback Messages */}
      {successFile && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3 text-emerald-300 text-sm animate-fade-in">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>
            <strong>{successFile}</strong> {t('uploadedSuccessMsg')}
          </span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm animate-fade-in">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
