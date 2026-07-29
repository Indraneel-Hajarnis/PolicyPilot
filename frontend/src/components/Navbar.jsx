import React, { useState } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, UploadCloud, MessageSquareText, FileText, Library, BarChart3, Menu, X, GitCompareArrows, Database, LogOut } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import LanguageSelector from './LanguageSelector';

const ROLE_COLORS = {
  desk_officer: 'bg-teal-500/10 border-teal-500/30 text-teal-300',
  legal_translator: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300',
  it_admin: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
};

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useLanguage();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    { key: 'navUpload', path: '/', icon: UploadCloud },
    { key: 'navChat', path: '/chat', icon: MessageSquareText },
    { key: 'navSummary', path: '/summary', icon: FileText },
    { key: 'navDocuments', path: '/documents', icon: Library },
    { key: 'Compare', path: '/compare', icon: GitCompareArrows },
    { key: 'navAnalytics', path: '/analytics', icon: BarChart3 },
    { key: 'Repository', path: '/repository', icon: Database },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const roleBadgeClass = ROLE_COLORS[user?.role] || ROLE_COLORS.desk_officer;

  return (
    <nav className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-2xl border-b border-slate-700/60 shadow-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-400 via-emerald-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-teal-500/25 group-hover:scale-105 transition-transform duration-300">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight text-white group-hover:text-teal-300 transition-colors">
                  Policy<span className="text-teal-400">Pilot</span>
                </span>
                <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-teal-300 bg-teal-500/10 border border-teal-500/30 rounded-full">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-ping" />
                  {t('multiLanguage')}
                </span>
              </div>
            </div>
          </Link>

          {/* Desktop Nav Items */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-200 ${
                      isActive
                        ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40 shadow-lg shadow-teal-500/10'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`
                  }
                >
                  <Icon className="w-3.5 h-3.5" />
                  {t(item.key) || item.key}
                </NavLink>
              );
            })}
          </div>

          {/* Controls: Role Badge + Language + Logout */}
          <div className="hidden md:flex items-center gap-2">
            {user && (
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold border ${roleBadgeClass}`}>
                {user.label || user.role}
              </span>
            )}
            <LanguageSelector />
            {user && (
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-2">
            <LanguageSelector />
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden border-b border-slate-700/60 bg-slate-900/95 backdrop-blur-2xl px-4 pt-2 pb-4 space-y-1">
          {/* Role badge in mobile */}
          {user && (
            <div className="flex items-center justify-between px-4 py-2 mb-2">
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold border ${roleBadgeClass}`}>
                {user.name || user.label}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-xs text-rose-400 font-semibold"
              >
                <LogOut className="w-3.5 h-3.5" /> Sign Out
              </button>
            </div>
          )}
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-base font-medium transition-all ${
                    isActive
                      ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                {t(item.key) || item.key}
              </NavLink>
            );
          })}
        </div>
      )}
    </nav>
  );
}
