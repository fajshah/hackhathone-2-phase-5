# Authentication System Documentation

## Overview
The Todo AI Chatbot implements a comprehensive authentication system with secure user registration, login, and session management.

## Features
- JWT-based authentication with secure token handling
- Bcrypt password hashing for secure password storage
- User registration with email and password
- Login/logout functionality
- Protected API endpoints with authentication middleware
- Frontend authentication context for state management
- User data isolation between different users

## Architecture

### Backend (FastAPI)
- **Authentication Module**: `/backend/src/auth.py`
  - JWT token generation and validation
  - Password hashing with bcrypt
  - User lookup from database
  - Authentication middleware

- **API Endpoints**: `/backend/src/api/auth.py`
  - `POST /api/auth/signup` - User registration
  - `POST /api/auth/login` - User login
  - `GET /api/auth/me` - Get current user info

- **User Model**: `/backend/src/models/user.py`
  - Email, password, profile information
  - Role-based access control
  - Data relationships with tasks, conversations, etc.

### Frontend (React)
- **Authentication Context**: `/frontend/src/context/AuthContext.tsx`
  - Global authentication state management
  - Token persistence in localStorage
  - Protected and public routing

- **UI Components**: `/frontend/src/pages/`
  - `Login.tsx` - Login form
  - `Register.tsx` - Registration form

## Security Measures
1. Passwords are hashed using bcrypt with salt
2. JWT tokens with configurable expiration (default 15 minutes)
3. Authentication middleware for protected endpoints
4. Proper user data isolation to prevent unauthorized access
5. Secure token storage and transmission

## Configuration
The authentication system is configured through environment variables in `.env`:
```
BETTER_AUTH_SECRET=supersecretkeyforauthenticationthatshouldbe32charactersormore
BETTER_AUTH_URL=http://localhost:8000
```

## API Usage

### Register a new user
```
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response:
```
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "success": true
}
```

### Access protected resources
```
GET /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Data Isolation
Each user's data (tasks, conversations, messages) is properly isolated through:
- Foreign key relationships to user ID
- Authentication middleware that verifies user ownership
- Service layer functions that enforce user access controls