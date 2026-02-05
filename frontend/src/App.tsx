import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/Header';
import FileBrowser from './components/FileBrowser';
import LoginPage from './components/LoginPage';
import './styles/App.css';

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="app">
        <div className="loading" style={{ minHeight: '100vh' }}>
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <FileBrowser />
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
