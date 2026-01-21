"use client";

import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on initial load
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      // Verify token and get user info
      fetchUserInfo(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async (token) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setCurrentUser({
          id: userData.id,
          email: userData.email,
          name: userData.first_name || userData.email.split('@')[0],
          firstName: userData.first_name,
          lastName: userData.last_name
        });
      } else {
        // Token invalid/expired, clear it
        localStorage.removeItem('authToken');
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
      localStorage.removeItem('authToken');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const token = data.token;

        // Store token in localStorage
        localStorage.setItem('authToken', token);

        // Set current user
        setCurrentUser({
          id: data.user.id,
          email: data.user.email,
          name: data.user.first_name || email.split('@')[0],
          firstName: data.user.first_name,
          lastName: data.user.last_name
        });

        return true;
      } else {
        const errorData = await response.json();
        console.error('Login error:', errorData.detail || 'Login failed');
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (name, email, password) => {
    try {
      // Split name into first and last name
      const nameParts = name.split(' ');
      const firstName = nameParts[0];
      const lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : null;

      const response = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const token = data.token;

        // Store token in localStorage
        localStorage.setItem('authToken', token);

        // Set current user
        setCurrentUser({
          id: data.user.id,
          email: data.user.email,
          name: data.user.first_name || email.split('@')[0],
          firstName: data.user.first_name,
          lastName: data.user.last_name
        });

        return true;
      } else {
        const errorData = await response.json();
        console.error('Registration error:', errorData.detail || 'Registration failed');
        return false;
      }
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('authToken');
  };

  const value = {
    currentUser,
    login,
    register,
    logout,
    loading
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div></div>;
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}