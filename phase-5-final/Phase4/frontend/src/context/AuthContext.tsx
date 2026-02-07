import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, type LoginResponse } from '../services/api';

interface User {
  id: number;
  email: string;
  firstName?: string;
  lastName?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, firstName?: string, lastName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check if user is logged in on initial load
    const token = localStorage.getItem('token');
    if (token) {
      // Try to fetch user profile to verify token
      const fetchUserProfile = async () => {
        try {
          const profile = await authService.getProfile();
          const userData: User = {
            id: profile.id,
            email: profile.email,
            firstName: profile.firstName,
            lastName: profile.lastName,
          };
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error: any) {
          // Token is invalid, remove it
          localStorage.removeItem('token');
          setUser(null);
          setIsAuthenticated(false);
        } finally {
          setIsLoading(false);
        }
      };

      fetchUserProfile();
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response: LoginResponse = await authService.login({ email, password });

      // Save token and user data
      localStorage.setItem('token', response.token);
      const userData: User = {
        id: response.user.id,
        email: response.user.email,
        firstName: response.user.firstName,
        lastName: response.user.lastName,
      };
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error: any) {
      throw error;
    }
  };

  const register = async (email: string, password: string, firstName?: string, lastName?: string) => {
    try {
      const response: LoginResponse = await authService.register({ email, password, firstName, lastName });

      // Save token and user data
      localStorage.setItem('token', response.token);
      const userData: User = {
        id: response.user.id,
        email: response.user.email,
        firstName: response.user.firstName,
        lastName: response.user.lastName,
      };
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error: any) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};