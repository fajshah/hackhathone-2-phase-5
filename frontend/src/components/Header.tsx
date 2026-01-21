import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../App.css';

export const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();

  const handleLogout = () => {
    logout();
  };

  if (!isAuthenticated) {
    return null; // Don't show header on auth pages
  }

  return (
    <header className="header">
      <nav className="navbar">
        <div className="nav-brand">
          <Link to="/chat">Todo AI Assistant</Link>
        </div>

        <ul className="nav-links">
          <li>
            <Link
              to="/chat"
              className={location.pathname === '/chat' ? 'active' : ''}
            >
              Chat
            </Link>
          </li>
          <li>
            <Link
              to="/tasks"
              className={location.pathname === '/tasks' ? 'active' : ''}
            >
              Tasks
            </Link>
          </li>
          <li className="dropdown">
            <span className="dropdown-label">
              {user?.firstName ? `${user.firstName} ${user?.lastName || ''}` : user?.email}
            </span>
            <ul className="dropdown-menu">
              <li><button onClick={handleLogout}>Logout</button></li>
            </ul>
          </li>
        </ul>
      </nav>
    </header>
  );
};