import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Monitoring from './pages/Monitoring';
import BettingVisualExtractor from './pages/BettingVisualExtractor';
import Sessions from './pages/Sessions';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';
import VirtualSports from './pages/VirtualSports';
import ProtectedRoute from './components/ProtectedRoute';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="App">
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/" 
          element={user ? <Navigate to="/dashboard" /> : <LandingPage />} 
        />
        <Route 
          path="/login" 
          element={user ? <Navigate to="/dashboard" /> : <Login />} 
        />
        <Route 
          path="/register" 
          element={user ? <Navigate to="/dashboard" /> : <Register />} 
        />

        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        <Route path="/monitoring" element={
          <ProtectedRoute>
            <Monitoring />
          </ProtectedRoute>
        } />
        
        <Route path="/betting-visual-extractor" element={
          <ProtectedRoute>
            <BettingVisualExtractor />
          </ProtectedRoute>
        } />
        
        <Route path="/sessions" element={
          <ProtectedRoute>
            <Sessions />
          </ProtectedRoute>
        } />
        
        <Route path="/analytics" element={
          <ProtectedRoute>
            <Analytics />
          </ProtectedRoute>
        } />
        
        <Route path="/profile" element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        } />

        <Route path="/virtual-sports" element={
          <ProtectedRoute>
            <VirtualSports />
          </ProtectedRoute>
        } />

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

export default App;