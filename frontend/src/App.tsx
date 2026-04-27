import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Layouts
import Layout from './components/layout/Layout.tsx';

// Pages
import Login from './pages/Login.tsx';
import Register from './pages/Register.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Jobs from './pages/Jobs.tsx';
import ResumeBuilder from './pages/ResumeBuilder.tsx';
import CoverLetter from './pages/CoverLetter.tsx';
import Skills from './pages/Skills.tsx';

function App() {
  const { checkAuth, isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
        <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />

        {/* Protected Routes */}
        <Route path="/" element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}>
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="jobs" element={<Jobs />} />
          <Route path="resumes" element={<ResumeBuilder />} />
          <Route path="cover-letter" element={<CoverLetter />} />
          <Route path="skills" element={<Skills />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
