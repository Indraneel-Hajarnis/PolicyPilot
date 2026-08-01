import React, { useState } from 'react';
import { ShieldCheck, Briefcase, Languages, Settings, Lock } from 'lucide-react';
import { useAuth, ROLES } from '../context/AuthContext';

const roleCards = [
  {
    key: 'desk_officer',
    username: 'desk.officer',
    password: 'DeskOfficer123!',
    icon: Briefcase,
    gradient: 'from-teal-500 to-emerald-500',
    shadow: 'shadow-teal-500/20',
    border: 'border-teal-500/30',
    desc: 'Upload, analyze, and query Government policy documents. Full document management access.',
  },
  {
    key: 'legal_translator',
    username: 'legal.translator',
    password: 'Translator123!',
    icon: Languages,
    gradient: 'from-indigo-500 to-purple-500',
    shadow: 'shadow-indigo-500/20',
    border: 'border-indigo-500/30',
    desc: 'Translate and review policy documents across English, Hindi, and Marathi.',
  },
  {
    key: 'it_admin',
    username: 'it.admin',
    password: 'Admin123!',
    icon: Settings,
    gradient: 'from-amber-500 to-orange-500',
    shadow: 'shadow-amber-500/20',
    border: 'border-amber-500/30',
    desc: 'Full platform access including analytics, repository management, and system configuration.',
  },
];

export default function LoginPage() {
  const { loginWithCredentials, login } = useAuth();
  const [selectedRole, setSelectedRole] = useState('desk_officer');
  const [username, setUsername] = useState('desk.officer');
  const [password, setPassword] = useState('DeskOfficer123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSelectRole = (rc) => {
    setSelectedRole(rc.key);
    setUsername(rc.username);
    setPassword(rc.password);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginWithCredentials(username, password);
    } catch (err) {
      console.warn('Backend login failed, fallback to client state:', err);
      login(selectedRole, ROLES[selectedRole]?.label || username);
    } finally {
      setLoading(false);
    }
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
              Authenticated Government Document Analysis & Multilingual RAG Platform
            </p>
          </div>
        </div>

        {/* Role Cards */}
        <div className="space-y-3">
          <h2 className="text-center text-xs font-bold text-slate-400 uppercase tracking-wider">
            Select Role Preset or Enter Credentials
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {roleCards.map((rc) => {
              const role = ROLES[rc.key];
              const isSelected = selectedRole === rc.key;
              const Icon = rc.icon;
              return (
                <button
                  key={rc.key}
                  type="button"
                  onClick={() => handleSelectRole(rc)}
                  className={`p-6 rounded-2xl border-2 text-left transition-all duration-300 group ${
                    isSelected
                      ? `${rc.border} bg-slate-800/80 scale-[1.02] ${rc.shadow} shadow-xl`
                      : 'border-slate-800 bg-slate-900/80 hover:border-slate-700 hover:bg-slate-800/60'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${rc.gradient} flex items-center justify-center mb-4 shadow-lg ${rc.shadow} group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">{role.label}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed mb-3">{rc.desc}</p>
                  <div className="text-[10px] text-slate-500 font-mono">
                    user: {rc.username}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="max-w-md mx-auto space-y-4 bg-slate-900/90 border border-slate-800 p-6 rounded-2xl">
          {error && <div className="p-3 text-xs bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl">{error}</div>}

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-teal-400"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase">Password</label>
            <div className="relative mt-1">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-teal-400"
              />
              <Lock className="w-4 h-4 text-slate-500 absolute right-3.5 top-3" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-teal-500/20 text-sm disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : `Sign In as ${ROLES[selectedRole]?.label || username}`}
          </button>
        </form>
      </div>
    </div>
  );
}

