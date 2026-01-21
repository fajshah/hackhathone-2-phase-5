"use client";

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Bot, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function PremiumChatbot() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [messages, setMessages] = useState<{ sender: 'user' | 'ai'; text: string; id: number }[]>([
    { sender: 'ai', text: 'Hello! I\'m your premium AI assistant. How can I help you manage your tasks today?', id: 1 }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000'); // Can be configured via environment
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // Initialize backend URL from environment or use default
    const url = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
    setBackendUrl(url);

    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || authLoading) return;

    const userMessage = { sender: 'user', text: input, id: Date.now() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      // Check if user is authenticated before making API call
      if (!isAuthenticated) {
        const errorMessage = {
          sender: 'ai',
          text: 'You need to be logged in to use the chat. Please log in first.',
          id: Date.now() + 1
        };
        setMessages(prev => [...prev, errorMessage]);
        setIsTyping(false);
        return;
      }

      // Get the token from the auth context instead of localStorage directly
      const token = localStorage.getItem('token');
      if (!token) {
        const errorMessage = {
          sender: 'ai',
          text: 'Authentication token is missing. Please log in again.',
          id: Date.now() + 1
        };
        setMessages(prev => [...prev, errorMessage]);
        setIsTyping(false);
        return;
      }

      const response = await fetch(`${backendUrl}/api/v1/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: input,
          conversation_id: null
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Simple version without typing animation for now
        const aiMessage = {
          sender: 'ai',
          text: data.response || "I received your message.",
          id: Date.now() + 1
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        // Handle different error statuses
        let errorMessageText = 'I\'m sorry, I encountered an error processing your request. Please try again.';

        if (response.status === 401) {
          errorMessageText = 'Unauthorized. Please log in again.';
        } else if (response.status === 403) {
          errorMessageText = 'Access forbidden. Please check your permissions.';
        } else if (response.status === 500) {
          errorMessageText = 'Server error. Please try again later.';
        } else if (data.detail) {
          errorMessageText = data.detail;
        }

        const errorMessage = {
          sender: 'ai',
          text: errorMessageText,
          id: Date.now() + 1
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error: any) {
      console.error('Chat error:', error);

      let errorMessageText = 'I\'m sorry, I\'m having trouble connecting to my AI services. Please check your connection and try again.';

      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessageText = 'Unable to connect to the server. Please check your internet connection.';
      } else if (error.message) {
        errorMessageText = `Error: ${error.message}`;
      }

      const errorMessage = {
        sender: 'ai',
        text: errorMessageText,
        id: Date.now() + 1
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  // Simplified return for debugging
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">

          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-5 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center justify-center">
                    <Bot size={20} className="text-white" />
                  </div>
                  <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
                </div>
                <div>
                  <h1 className="text-lg font-semibold">AI Task Assistant</h1>
                  <p className="text-blue-100 text-sm">Online • Ready to help</p>
                </div>
              </div>
            </div>
          </div>

          {/* Messages Container */}
          <div className="h-[50vh] overflow-y-auto p-4 space-y-4 bg-gray-50">
            <AnimatePresence>
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-4 ${
                      msg.sender === 'user'
                        ? 'bg-blue-500 text-white rounded-br-none'
                        : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {msg.sender === 'ai' ? (
                        <div className="flex-shrink-0 mt-0.5">
                          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center justify-center">
                            <Bot size={14} className="text-white" />
                          </div>
                        </div>
                      ) : null}

                      <div className="flex-1">
                        {msg.text}
                      </div>

                      {msg.sender === 'user' ? (
                        <div className="flex-shrink-0 mt-0.5">
                          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                            <User size={14} className="text-white" />
                          </div>
                        </div>
                      ) : null}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start"
              >
                <div className="max-w-[85%] rounded-2xl p-4 bg-white rounded-bl-none border border-gray-200">
                  <div className="flex items-center space-x-2">
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center justify-center">
                        <Bot size={14} className="text-white" />
                      </div>
                    </div>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce delay-75"></div>
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce delay-150"></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-gray-200 bg-white">
            <div className="flex items-end space-x-2">
              <div className="flex-1 relative">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Describe your task or ask for help..."
                  className="w-full bg-gray-100 border border-gray-300 rounded-xl py-3 pl-4 pr-12 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="absolute left-3 top-3 text-gray-400">
                  <Sparkles size={16} />
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSend}
                disabled={!input.trim() || isTyping}
                className={`p-3 rounded-xl ${
                  input.trim() && !isTyping
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <Send size={18} />
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}