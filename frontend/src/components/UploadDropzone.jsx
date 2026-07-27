import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '../api/client';
import { useLanguage } from '../context/LanguageContext';

export default function UploadDropzone({ onUploadSuccess }) {
  const { t } = useLanguage();
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [successFile, setSuccessFile] = useState(null);

  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setUploading(true);
      setProgress(0);
      setError(null);
      setSuccessFile(null);

      try {
        const res = await uploadDocument(file, (percent) => {
          setProgress(percent);
        });
        setSuccessFile(res.original_name);
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
    [onUploadSuccess, t]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
    disabled: uploading,
  });

  return (
    <div className="w-full">
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

      {/* Feedback Messages */}
      {successFile && (
        <div className="mt-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3 text-emerald-300 text-sm animate-fade-in">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>
            {(() => {
              const msg = t('uploadSuccess');
              if (msg.includes('{file}')) {
                const parts = msg.split('{file}');
                return (
                  <>
                    {parts[0]}
                    <strong>{successFile}</strong>
                    {parts[1]}
                  </>
                );
              }
              return (
                <>
                  {msg} <strong>{successFile}</strong>
                </>
              );
            })()}
          </span>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm animate-fade-in">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
