import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Chat } from './pages/Chat';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';
import './App.css';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <>
      {isAuthenticated && <Navbar />}
      <Routes>
        <Route path="/" element={
          !isAuthenticated ? (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
              <div className="text-center max-w-2xl">
                <h1 className="text-4xl md:text-6xl font-bold text-gray-800 mb-6">
                  Welcome to <span className="text-indigo-600">Todo AI</span>
                </h1>
                <p className="text-lg md:text-xl text-gray-600 mb-8">
                  Your intelligent assistant for managing tasks with natural language
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <a 
                    href="/login" 
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-300 shadow-lg hover:shadow-xl"
                  >
                    Login
                  </a>
                  <a 
                    href="/register" 
                    className="bg-white hover:bg-gray-100 text-indigo-600 font-semibold py-3 px-6 rounded-lg transition duration-300 shadow-lg hover:shadow-xl border border-indigo-200"
                  >
                    Register
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
              <div className="text-center max-w-2xl">
                <h1 className="text-4xl md:text-6xl font-bold text-gray-800 mb-6">
                  Welcome Back!
                </h1>
                <p className="text-lg md:text-xl text-gray-600 mb-8">
                  Continue your journey with AI-powered task management
                </p>
                <a 
                  href="/chat" 
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-300 shadow-lg hover:shadow-xl inline-block"
                >
                  Go to Chat
                </a>
              </div>
            </div>
          )
        } />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route 
          path="/chat" 
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;