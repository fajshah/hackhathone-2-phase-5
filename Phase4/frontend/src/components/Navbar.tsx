import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Bot, LogOut, User } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/chat" className="flex-shrink-0 flex items-center">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-2 rounded-lg">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <span className="ml-2 text-xl font-bold text-gray-900">Todo AI</span>
            </Link>
          </div>
          
          <div className="flex items-center">
            <div className="ml-3 relative">
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-700 hidden md:block">
                  <div>{user?.firstName} {user?.lastName}</div>
                </div>
                
                <div className="relative">
                  <div className="flex items-center space-x-2">
                    <div className="bg-gray-200 border-2 border-dashed rounded-xl w-8 h-8" />
                    
                    <div className="relative">
                      <button
                        onClick={logout}
                        className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        aria-label="Logout"
                      >
                        <LogOut className="h-5 w-5 text-gray-500 hover:text-indigo-600" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};