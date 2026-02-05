import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, HardDrive } from 'lucide-react';

const Header: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <HardDrive size={28} />
        <h1>NAS Cloud</h1>
      </div>
      {user && (
        <div className="header-user">
          {user.avatar_url && (
            <img src={user.avatar_url} alt={user.username} />
          )}
          <span>{user.email}</span>
          <button className="btn btn-outline" onClick={logout} style={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}>
            <LogOut size={16} />
            Logout
          </button>
        </div>
      )}
    </header>
  );
};

export default Header;
