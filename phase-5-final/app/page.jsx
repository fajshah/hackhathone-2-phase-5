"use client";

import { useState } from 'react';
import { AuthProvider } from "../components/AuthContext";
import { useAuth } from "../components/AuthContext";
import Chatbot from "../components/Chatbot";

// Sidebar component
function Sidebar() {
  const { currentUser, login, register, logout } = useAuth();
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (authMode === 'login') {
        const success = await login(email, password);
        if (!success) {
          setError('Invalid email or password');
        }
      } else {
        const success = await register(name, email, password);
        if (!success) {
          setError('Registration failed');
        }
      }
    } catch (err) {
      setError('An error occurred');
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div style={{
      width: '260px',
      backgroundColor: '#ede9fe', // light purple sidebar
      height: '100vh',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      borderRight: '1px solid #ddd6fe',
    }}>
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{
          color: '#7c3aed', // purple color
          fontSize: '18px',
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          🤖 Todo AI Assistant
        </h1>
        <p style={{ color: '#7c3aed', fontSize: '14px', marginTop: '4px' }}>Smart Tasks</p>
      </div>

      {!currentUser ? (
        <div>
          <div style={{ marginBottom: '15px' }}>
            <button
              onClick={() => setAuthMode('login')}
              style={{
                width: '100%',
                backgroundColor: authMode === 'login' ? '#7c3aed' : '#ffffff',
                color: authMode === 'login' ? '#ffffff' : '#7c3aed',
                border: '1px solid #ddd6fe',
                padding: '10px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '500',
                marginBottom: '8px'
              }}
            >
              Login
            </button>
            <button
              onClick={() => setAuthMode('register')}
              style={{
                width: '100%',
                backgroundColor: authMode === 'register' ? '#7c3aed' : '#ffffff',
                color: authMode === 'register' ? '#ffffff' : '#7c3aed',
                border: '1px solid #ddd6fe',
                padding: '10px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
            {authMode === 'register' && (
              <div style={{ marginBottom: '10px' }}>
                <input
                  type="text"
                  placeholder="Full Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd6fe',
                    borderRadius: '6px',
                    marginBottom: '10px',
                    backgroundColor: '#f5f3ff'
                  }}
                />
              </div>
            )}
            <div style={{ marginBottom: '10px' }}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #ddd6fe',
                  borderRadius: '6px',
                  marginBottom: '10px',
                  backgroundColor: '#f5f3ff'
                }}
              />
            </div>
            <div style={{ marginBottom: '10px' }}>
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #ddd6fe',
                  borderRadius: '6px',
                  marginBottom: '10px',
                  backgroundColor: '#f5f3ff'
                }}
              />
            </div>
            {error && <p style={{ color: 'red', fontSize: '14px', marginBottom: '10px' }}>{error}</p>}
            <button
              type="submit"
              style={{
                width: '100%',
                backgroundColor: '#7c3aed',
                color: 'white',
                border: 'none',
                padding: '10px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              {authMode === 'login' ? 'Login' : 'Sign Up'}
            </button>
          </form>
        </div>
      ) : (
        <div>
          <div style={{
            backgroundColor: 'white',
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid #ddd6fe',
            marginBottom: '15px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '24px',
                height: '24px',
                backgroundColor: '#7c3aed',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '12px'
              }}>
                👤
              </div>
              <span style={{ color: '#7c3aed', fontSize: '14px' }}>{currentUser.name}</span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              width: '100%',
              backgroundColor: '#a78bfa',
              color: 'white',
              border: 'none',
              padding: '10px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
}

// Main page component
export default function Page() {
  return (
    <AuthProvider>
      <div style={{
        display: 'flex',
        height: '100vh',
        backgroundColor: '#f3e8ff', // light purple background
      }}>
        <Sidebar />
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
        }}>
          <div style={{
            width: '100%',
            maxWidth: '800px',
            backgroundColor: 'white',
            borderRadius: '10px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            height: '90vh',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <div style={{
              backgroundColor: '#f5f3ff',
              padding: '15px',
              borderTopLeftRadius: '10px',
              borderTopRightRadius: '10px',
              borderBottom: '1px solid #ddd6fe',
              display: 'flex',
              alignItems: 'center'
            }}>
              <h1 style={{
                color: '#7c3aed',
                fontSize: '18px',
                fontWeight: 'bold',
                margin: 0
              }}>
                ✨ Smart Tasks
              </h1>
            </div>
            <div style={{ flex: 1, padding: '20px' }}>
              <Chatbot />
            </div>
          </div>
        </div>
      </div>
    </AuthProvider>
  );
}