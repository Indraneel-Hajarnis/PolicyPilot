import { createContext, useContext, useState, useCallback } from 'react';

const AuthContext = createContext(null);

const ROLES = {
  desk_officer: { label: 'Desk Officer', color: 'teal', permissions: ['upload', 'chat', 'summary', 'documents', 'compare'] },
  legal_translator: { label: 'Legal Translator', color: 'indigo', permissions: ['chat', 'summary', 'documents', 'compare'] },
  it_admin: { label: 'IT Administrator', color: 'amber', permissions: ['upload', 'chat', 'summary', 'documents', 'analytics', 'compare', 'repository'] },
};

function loadUser() {
  try {
    const raw = sessionStorage.getItem('policypilot_user');
    if (raw) return JSON.parse(raw);
  } catch {
    // fallthrough
  }
  // Default user so the app loads out-of-the-box
  return {
    role: 'desk_officer',
    name: 'Desk Officer',
    label: 'Desk Officer',
    color: 'teal',
    permissions: ['upload', 'chat', 'summary', 'documents', 'compare'],
    loginAt: new Date().toISOString(),
  };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(loadUser);

  const login = useCallback((role, name = '') => {
    const roleInfo = ROLES[role] || ROLES.desk_officer;
    const userData = {
      role,
      name: name || roleInfo.label,
      label: roleInfo.label,
      color: roleInfo.color,
      permissions: roleInfo.permissions,
      loginAt: new Date().toISOString(),
    };
    setUser(userData);
    sessionStorage.setItem('policypilot_user', JSON.stringify(userData));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    sessionStorage.removeItem('policypilot_user');
  }, []);

  const hasPermission = useCallback((permission) => {
    if (!user) return false;
    return user.permissions?.includes(permission) ?? false;
  }, [user]);

  return (
    <AuthContext.Provider value={{ user, login, logout, hasPermission, ROLES }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export { ROLES };
export default AuthContext;
