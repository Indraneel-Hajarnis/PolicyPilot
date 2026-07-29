import React, { useState } from 'react';
import { ShieldCheck, UserCircle, Briefcase, Languages, Settings } from 'lucide-react';
import { useAuth, ROLES } from '../context/AuthContext';

const roleCards = [
  {
    key: 'desk_officer',
    icon: Briefcase,
    gradient: 'from-teal-500 to-emerald-500',
    shadow: 'shadow-teal-500/20',
    border: 'border-teal-500/30',
    desc: 'Upload, analyze, and query Government policy documents. Full document management access.',
  },
  {
    key: 'legal_translator',
    icon: Languages,
    gradient: 'from-indigo-500 to-purple-500',
    shadow: 'shadow-indigo-500/20',
    border: 'border-indigo-500/30',
    desc: 'Translate and review policy documents across English, Hindi, and Marathi.',
  },
  {
    key: 'it_admin',
    icon: Settings,
    gradient: 'from-amber-500 to-orange-500',
    shadow: 'shadow-amber-500/20',
    border: 'border-amber-500/30',
    desc: 'Full platform access including analytics, repository management, and system configuration.',
  },
];

export default function LoginPage() {
  const { login } = useAuth();
  const [name, setName] = useState('');
  const [selectedRole, setSelectedRole] = useState(null);

  const handleLogin = () => {
    if (!selectedRole) return;
    login(selectedRole, name || ROLES[selectedRole].label);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl space-y-8 animate-fade-in">
        {/* Logo & Title */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-tr from-teal-400 via-emerald-500 to-indigo-600 shadow-2xl shadow-teal-500/25">
            <ShieldCheck className="w-10 h-10 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-extrabold text-white tracking-tight">
              Policy<span className="text-teal-400">Pilot</span>
            </h1>
            <p className="text-sm text-slate-400 mt-2">
              Secure Government Document Analysis Platform
            </p>
          </div>
        </div>

        {/* Name Input */}
        <div className="max-w-md mx-auto">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Your Name (optional)</label>
          <div className="relative mt-1.5">
            <UserCircle className="w-5 h-5 text-slate-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your name"
              className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-11 pr-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-400 transition-all"
            />
          </div>
        </div>

        {/* Role Selection */}
        <div className="space-y-3">
          <h2 className="text-center text-xs font-bold text-slate-400 uppercase tracking-wider">
            Select Your Role
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {roleCards.map(({ key, icon: Icon, gradient, shadow, border, desc }) => {
              const role = ROLES[key];
              const isSelected = selectedRole === key;
              return (
                <button
                  key={key}
                  onClick={() => setSelectedRole(key)}
                  className={`p-6 rounded-2xl border-2 text-left transition-all duration-300 group ${
                    isSelected
                      ? `${border} bg-slate-800/80 scale-[1.02] ${shadow} shadow-xl`
                      : 'border-slate-800 bg-slate-900/80 hover:border-slate-700 hover:bg-slate-800/60'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${gradient} flex items-center justify-center mb-4 shadow-lg ${shadow} group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">{role.label}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
                  {isSelected && (
                    <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-teal-500/20 border border-teal-500/30 text-[10px] font-bold text-teal-300">
                      ✓ Selected
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Login Button */}
        <div className="text-center">
          <button
            onClick={handleLogin}
            disabled={!selectedRole}
            className="bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold px-10 py-3.5 rounded-xl transition-all shadow-lg shadow-teal-500/20 text-sm"
          >
            Sign In as {selectedRole ? ROLES[selectedRole].label : '...'}
          </button>
        </div>
      </div>
    </div>
  );
}
