"use client";

import { useState, useRef, useEffect } from 'react';
import { useAuth } from './AuthContext';

export default function Chatbot() {
  const { currentUser, login, register, logout, loading } = useAuth();

  // If user is not authenticated, show welcome message prompting login
  const initialMessages = currentUser
    ? [
        {
          id: 1,
          text: `${currentUser.name}! ${(currentUser.email && currentUser.email.includes('urdu'))
            ? 'خوش آمدید! کیسے مدد کروں؟'
            : 'Welcome! How can I help you today?'}`,
          sender: 'ai'
        }
      ]
    : [
        {
          id: 1,
          text: 'Welcome! Please log in to start chatting with your Todo AI Assistant.',
          sender: 'ai'
        }
      ];

  const [messages, setMessages] = useState(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [nextId, setNextId] = useState(2);
  const [showAuthForm, setShowAuthForm] = useState(false);
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'signup'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (inputValue.trim() === '' || isLoading) return;

    // If user is not authenticated, prompt them to login before chatting
    if (!currentUser) {
      // Show login prompt and don't process the message
      setShowAuthForm(true);
      setAuthMode('login');

      // Add a message to inform the user
      const authPromptMessage = {
        id: nextId,
        text: 'Please log in first to start chatting with the Todo AI Assistant.',
        sender: 'ai'
      };

      setMessages(prev => [...prev, authPromptMessage]);
      setNextId(prev => prev + 1);
      setInputValue('');
      return;
    }

    const userMessage = {
      id: nextId,
      text: inputValue,
      sender: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setNextId(prev => prev + 1);
    setInputValue('');
    setIsLoading(true);

    try {
      // Simulate API delay for realistic feel
      await new Promise(resolve => setTimeout(resolve, 500));

      // Handle auth commands
      let aiResponse = 'How can I assist you with your todos today?';
      if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
        aiResponse = 'آج میں آپ کے کاموں میں کیسے مدد کر سکتا ہوں؟';
      }

      const lowerInput = inputValue.toLowerCase().trim();

      if (lowerInput.includes('login') || lowerInput.includes('signin')) {
        if (currentUser) {
          aiResponse = currentUser.email.includes('urdu') ? 'آپ پہلے سے لاگ ان ہیں!' : 'You are already logged in!';
        } else {
          setShowAuthForm(true);
          setAuthMode('login');
          aiResponse = lowerInput.includes('urdu') ? 'لاگ ان کریں:' : 'Please login:';
        }
      } else if (lowerInput.includes('signup') || lowerInput.includes('register')) {
        if (currentUser) {
          aiResponse = currentUser.email.includes('urdu') ? 'آپ پہلے سے رجسٹر ہیں!' : 'You are already registered!';
        } else {
          setShowAuthForm(true);
          setAuthMode('signup');
          aiResponse = lowerInput.includes('urdu') ? 'رجسٹر کریں:' : 'Please register:';
        }
      } else if (lowerInput.includes('logout') || lowerInput.includes('signout')) {
        if (currentUser) {
          logout();
          setMessages([{ id: 1, text: (lowerInput.includes('urdu') ? 'آپ لاگ آوٹ ہو چکے ہیں!' : 'You have been logged out!'), sender: 'ai' }]);
          aiResponse = lowerInput.includes('urdu') ? 'دوبارہ لاگ ان کریں؟' : 'Log in again?';
        } else {
          aiResponse = lowerInput.includes('urdu') ? 'پہلے سے لاگ آوٹ ہیں!' : 'Already logged out!';
        }
      } else if (showAuthForm) {
        // Handle auth form submission
        if (authMode === 'login') {
          if (email && password) {
            if (await login(email, password)) {
              setShowAuthForm(false);
              setEmail('');
              setPassword('');
              if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
                aiResponse = `خوش آمدید، ${currentUser.name}!`;
              } else {
                aiResponse = `Welcome back, ${currentUser.name}!`;
              }
            } else {
              aiResponse = 'Login failed! Please check your credentials.';
              if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
                aiResponse = 'لاگ ان ناکام ہوا! براہ کرم اپنی تفصیلات چیک کریں۔';
              }
            }
          }
        } else if (authMode === 'signup') {
          if (name && email && password) {
            if (await register(name, email, password)) {
              setShowAuthForm(false);
              setName('');
              setEmail('');
              setPassword('');
              if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
                aiResponse = `خوش آمدید، ${currentUser.name}!`;
              } else {
                aiResponse = `Welcome, ${currentUser.name}!`;
              }
            } else {
              aiResponse = 'Registration failed! Please try again.';
              if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
                aiResponse = 'رجسٹریشن ناکام ہوئی! براہ کرم دوبارہ کوشش کریں۔';
              }
            }
          }
        }
      } else {
        // Rule-based responses
        if (lowerInput.includes('add task') || lowerInput.includes('add karo')) {
          if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
            aiResponse = 'کام شامل کیا گیا ✅';
          } else {
            aiResponse = 'Task added successfully ✅';
          }
        } else if (lowerInput.includes('milk') || lowerInput.includes('meat') || lowerInput.includes('oil') || lowerInput.includes('laptop')) {
          if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
            aiResponse = 'آئٹمز آپ کی فہرست میں شامل کر دیئے گئے 🛒';
          } else {
            aiResponse = 'Items added to your grocery list 🛒';
          }
        } else if (lowerInput.includes('hello') || lowerInput.includes('hi') || lowerInput.includes('hey') || lowerInput.includes('assalam')) {
          if (currentUser) {
            if (currentUser.email && currentUser.email.includes('urdu')) {
              aiResponse = `ہیلو، ${currentUser.name}! کیسے مدد کر سکتا ہوں؟`;
            } else {
              aiResponse = `Hello, ${currentUser.name}! How can I help?`;
            }
          } else {
            aiResponse = lowerInput.includes('urdu') ? 'ہیلو! میں آپ کی کیسے مدد کر سکتا ہوں؟' : 'Hello! How can I help you?';
          }
        } else if (lowerInput.includes('show list') || lowerInput.includes('list dikhao') || lowerInput.includes('list dekhna') || lowerInput.includes('show task') || lowerInput.includes('mujhe list dikhao') || lowerInput.includes('mujhe fehrist dikhao') || lowerInput.includes('list dikhao urdu me') || lowerInput.includes('urdu me list dikhao')) {
          if (lowerInput.includes('urdu') || (currentUser && currentUser.email && currentUser.email.includes('urdu'))) {
            aiResponse = 'آپ کی فہرست: دودھ، لیپ ٹاپ، گوشت۔ کیا آپ کچھ شامل کرنا چاہتے ہیں یا کوئی کام مکمل کرنا چاہتے ہیں؟';
          } else {
            aiResponse = 'Your current tasks: Buy milk, Buy laptop, Buy meat. Would you like to add something or complete a task?';
          }
        } else if (lowerInput.includes('buy') || lowerInput.includes('khareedna')) {
          if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
            aiResponse = 'چیزیں خرید لی گئیں! کیا آپ کو مزید کچھ چاہیے؟';
          } else {
            aiResponse = 'Items purchased successfully! Would you like anything else?';
          }
        } else if (lowerInput.includes('delete') || lowerInput.includes('remove') || lowerInput.includes('hatana')) {
          if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
            aiResponse = 'کام کامیابی سے حذف کر دیا گیا! کیا آپ کو مزید کچھ حذف کرنا ہے؟';
          } else {
            aiResponse = 'Task successfully removed! Would you like to remove anything else?';
          }
        } else if (lowerInput.includes('urdu')) {
          aiResponse = 'آپ اردو میں بات کر سکتے ہیں! کیسے مدد کروں؟';
        } else if (lowerInput.includes('help') || lowerInput.includes('madad')) {
          if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
            aiResponse = 'میں آپ کے کام شامل کر سکتا ہوں، حذف کر سکتا ہوں، مکمل کر سکتا ہوں، یا آپ کی فہرست دکھا سکتا ہوں۔ مجھے بتائیں کیا کرنا ہے؟';
          } else {
            aiResponse = 'I can help you add tasks, remove tasks, complete tasks, or show your list. Tell me what to do!';
          }
        } else if (lowerInput.includes('complete') || lowerInput.includes('done') || lowerInput.includes('mukammal')) {
          if (currentUser && currentUser.email && currentUser.email.includes('urdu')) {
            aiResponse = 'کام کامیابی سے مکمل کر دیا گیا! کیا آپ کو مزید کچھ مکمل کرنا ہے؟';
          } else {
            aiResponse = 'Task successfully completed! Would you like to complete anything else?';
          }
        } else {
          // Default response - check if user wants Urdu
          if (lowerInput.includes('urdu') || (currentUser && currentUser.email && currentUser.email.includes('urdu'))) {
            aiResponse = 'میں آپ کے کاموں میں مدد کے لیے تیار ہوں! کیا کرنا ہے؟';
          } else {
            aiResponse = 'I\'m ready to help with your tasks! What would you like to do?';
          }
        }
      }

      const aiMessage = {
        id: nextId + 1,
        text: aiResponse,
        sender: 'ai'
      };

      setMessages(prev => [...prev, aiMessage]);
      setNextId(prev => prev + 1);
    } catch (error) {
      console.error('Error processing message:', error);
      const errorMessage = {
        id: nextId + 1,
        text: currentUser && currentUser.email && currentUser.email.includes('urdu')
          ? 'معاف کریں، کچھ غلط ہو گیا۔ براہ کرم دوبارہ کوشش کریں۔'
          : 'Sorry, something went wrong. Please try again.',
        sender: 'ai'
      };
      setMessages(prev => [...prev, errorMessage]);
      setNextId(prev => prev + 1);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleAuthSubmit = (e) => {
    e.preventDefault();
    handleSend();
  };

  const TypingIndicator = () => (
    <div className="flex items-center space-x-2 p-4">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
      </div>
      <span className="text-purple-600 text-sm font-medium">AI is typing...</span>
    </div>
  );

  return (
    <div className="flex flex-col w-full max-w-4xl h-[80vh] md:h-[85vh] bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-2xl shadow-2xl overflow-hidden border border-transparent flex-grow max-w-3xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-5 text-white">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl md:text-3xl font-bold flex items-center">
            <span className="mr-3 text-3xl">🎯</span> Todo AI Assistant
            <span className="ml-2 text-yellow-300 text-lg">✨ Smart Tasks</span>
          </h1>
          <div className="flex items-center space-x-3">
            {!currentUser ? (
              <>
                <button
                  onClick={() => { setShowAuthForm(true); setAuthMode('login'); }}
                  className="px-4 py-2 bg-white bg-opacity-20 backdrop-blur-sm text-white rounded-xl text-sm font-semibold hover:bg-opacity-30 transition-all duration-300 border border-white border-opacity-30 shadow-lg"
                >
                  {((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'لاگ ان' : 'Login')}
                </button>
                <button
                  onClick={() => { setShowAuthForm(true); setAuthMode('signup'); }}
                  className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-purple-900 rounded-xl text-sm font-semibold hover:from-yellow-300 hover:to-orange-400 transition-all duration-300 shadow-lg"
                >
                  {((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'سائن اپ' : 'Sign Up')}
                </button>
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <div className="flex items-center bg-white bg-opacity-20 backdrop-blur-sm rounded-full px-3 py-1 border border-white border-opacity-30">
                  <span className="text-sm font-medium mr-2">👋</span>
                  <span className="text-sm font-medium">{currentUser.name}</span>
                </div>
                <button
                  onClick={() => {
                    logout();
                    setMessages([{
                      id: 1,
                      text: ((currentUser && currentUser.email && currentUser.email.includes('urdu'))
                        ? 'آپ لاگ آوٹ ہو چکے ہیں!'
                        : 'You have been logged out!'),
                      sender: 'ai'
                    }]);
                  }}
                  className="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-xl text-sm font-semibold hover:from-red-600 hover:to-pink-700 transition-all duration-300 shadow-lg"
                >
                  {((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'لاگ آوٹ' : 'Logout')}
                </button>
              </div>
            )}
          </div>
        </div>
        {currentUser && (
          <p className="text-purple-200 text-xs mt-2 text-center md:text-left flex items-center justify-center md:justify-start">
            <span className="inline-block w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
            {(currentUser.email && currentUser.email.includes('urdu')) ? 'لاگ ان شدہ' : 'Logged In'} • Secure Session
          </p>
        )}
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-5 bg-gradient-to-b from-indigo-50 via-purple-25 to-pink-25">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`mb-5 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.sender === 'ai' && (
              <div className="flex-shrink-0 mr-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg border-2 border-white">
                  <span className="text-white text-base">🤖</span>
                </div>
              </div>
            )}
            <div
              className={`max-w-[85%] md:max-w-[75%] px-5 py-4 rounded-3xl ${
                message.sender === 'user'
                  ? 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white rounded-br-none shadow-lg'
                  : 'bg-white text-gray-800 border border-purple-100 rounded-bl-none shadow-lg bg-opacity-80 backdrop-blur-sm'
              }`}
            >
              <p className="whitespace-pre-wrap font-medium">{message.text}</p>
            </div>
            {message.sender === 'user' && (
              <div className="flex-shrink-0 ml-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-600 flex items-center justify-center shadow-lg border-2 border-white">
                  <span className="text-white text-base">👤</span>
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="mb-5 flex justify-start">
            <div className="flex-shrink-0 mr-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg border-2 border-white">
                <span className="text-white text-base">🤖</span>
              </div>
            </div>
            <div className="bg-white text-gray-800 border border-purple-100 rounded-3xl rounded-bl-none shadow-lg px-5 py-4 bg-opacity-80 backdrop-blur-sm">
              <TypingIndicator />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Auth Form Overlay */}
      {showAuthForm && (
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-indigo-900 to-pink-900 bg-opacity-90 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-7 w-full max-w-md shadow-2xl border border-purple-200 transform transition-all duration-300 scale-100">
            <div className="flex justify-between items-center mb-5 border-b border-purple-100 pb-3">
              <h3 className="text-2xl font-bold text-gray-800 flex items-center">
                <span className="mr-2">
                  {authMode === 'login' ? '🔐' : '📝'}
                </span>
                {authMode === 'login'
                  ? ((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'لاگ ان' : 'Login')
                  : ((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'سائن اپ' : 'Sign Up')}
              </h3>
              <button
                onClick={() => setShowAuthForm(false)}
                className="text-gray-500 hover:text-red-500 text-2xl transition-colors"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAuthSubmit}>
              {authMode === 'signup' && (
                <div className="mb-5">
                  <label className="block text-gray-700 text-sm font-semibold mb-2 flex items-center" htmlFor="name">
                    <span className="mr-2">👤</span>
                    {((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'نام' : 'Name')}
                  </label>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={(currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'نام درج کریں' : 'Enter your name'}
                    className="w-full px-4 py-3 border-2 border-purple-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-purple-50"
                    required
                  />
                </div>
              )}

              <div className="mb-5">
                <label className="block text-gray-700 text-sm font-semibold mb-2 flex items-center" htmlFor="email">
                  <span className="mr-2">📧</span>
                  {((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'ای میل' : 'Email')}
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={(currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'ای میل درج کریں' : 'Enter your email'}
                  className="w-full px-4 py-3 border-2 border-purple-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-purple-50"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-semibold mb-2 flex items-center" htmlFor="password">
                  <span className="mr-2">🔒</span>
                  {((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'پاس ورڈ' : 'Password')}
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={(currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'پاس ورڈ درج کریں' : 'Enter your password'}
                  className="w-full px-4 py-3 border-2 border-purple-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-purple-50"
                  required
                />
              </div>

              <div className="flex space-x-4 pt-3">
                <button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white py-3 px-4 rounded-xl font-bold hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 transition-all duration-300 transform hover:scale-105 shadow-lg"
                >
                  {authMode === 'login'
                    ? ((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'لاگ ان' : 'Login')
                    : ((currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'رجسٹر' : 'Sign Up')}
                </button>
                <button
                  type="button"
                  onClick={() => setShowAuthForm(false)}
                  className="flex-1 bg-gradient-to-r from-gray-400 to-gray-500 text-white py-3 px-4 rounded-xl font-bold hover:from-gray-500 hover:to-gray-600 transition-all duration-300 transform hover:scale-105 shadow-lg"
                >
                  {(currentUser && currentUser.email && currentUser.email.includes('urdu')) ? 'منسوخ' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-purple-200 bg-white bg-opacity-80 backdrop-blur-sm p-5">
        <div className="flex items-end space-x-3">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={currentUser
              ? ((currentUser.email && currentUser.email.includes('urdu'))
                  ? "پیغام لکھیں... (مثال: کام شامل کریں)"
                  : "Type your message here... (e.g., add task)")
              : "Please log in to start chatting"}
            className={`flex-1 border-2 rounded-2xl px-5 py-4 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none max-h-40 transition-all duration-200 shadow-inner ${
              currentUser
                ? 'border-purple-300 bg-white bg-opacity-70'
                : 'border-gray-300 bg-gray-100 text-gray-400'
            }`}
            rows="1"
            disabled={isLoading || !currentUser}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || inputValue.trim() === '' || !currentUser}
            className={`h-14 w-14 flex items-center justify-center rounded-full flex-shrink-0 ${
              inputValue.trim() === '' || isLoading || !currentUser
                ? 'bg-gray-300 cursor-not-allowed opacity-50'
                : 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 transform hover:scale-110 transition-all duration-300 shadow-lg'
            } text-white shadow-lg flex items-center justify-center`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          </button>
        </div>
        {currentUser ? (
          <div className="flex flex-wrap gap-2 mt-3 justify-center">
            <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">💡 Tip:</span>
            <span className="text-xs text-purple-600">{currentUser.email && currentUser.email.includes('urdu') ? 'کام شامل کریں' : 'Add task:'} "add buy milk"</span>
            <span className="text-xs text-purple-600">{currentUser.email && currentUser.email.includes('urdu') ? 'کام دیکھیں' : 'Show tasks:'} "show list"</span>
            <span className="text-xs text-purple-600">{currentUser.email && currentUser.email.includes('urdu') ? 'اردو میں' : 'In Urdu:'} "urdu"</span>
          </div>
        ) : (
          <div className="text-center text-sm text-purple-600 mt-3">
            🔐 Please log in to start chatting with your Todo AI Assistant
          </div>
        )}
      </div>
    </div>
  );
}