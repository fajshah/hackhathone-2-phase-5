'use client'


import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { RobotAvatar } from './RobotAvatar';
import { Sparkles } from 'lucide-react';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const mockMessages: Message[] = [
  {
    id: 1,
    role: 'assistant',
    content: 'Hello! I\'m your AI assistant. How can I help you manage your tasks today?',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  },
  {
    id: 2,
    role: 'assistant',
    content: 'You can ask me to create, list, update, or manage your tasks using natural language.',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
];

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [typingText, setTypingText] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        // Only load messages from the last 24 hours to keep it fresh
        const twentyFourHoursAgo = Date.now() - (24 * 60 * 60 * 1000);
        const recentMessages = parsedMessages.filter(
          (msg: Message) => new Date(msg.timestamp).getTime() > twentyFourHoursAgo
        );
        if (recentMessages.length > 0) {
          setMessages(recentMessages);
        }
      } catch (error) {
        console.error('Failed to load messages from localStorage:', error);
      }
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages));
  }, [messages]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, typingText]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Simulate AI response after delay
      const response = await fetch('http://localhost:8000/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        },
        body: JSON.stringify({
          message: message,
          conversation_id: null // Will be handled by backend
        })
      });

      const data = await response.json();

      if (response.ok) {
        const aiMessage: Message = {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage: Message = {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'Sorry, I encountered an error processing your request. Please try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered a network error. Please check your connection and try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-blue-50 to-purple-50 text-blue-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/4 left-1/4 w-64 h-64 bg-pink-300/10 rounded-full mix-blend-multiply filter blur-xl"
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 20, 0],
            y: [0, -20, 0]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
        <motion.div
          className="absolute top-1/3 right-1/4 w-64 h-64 bg-blue-300/10 rounded-full mix-blend-multiply filter blur-xl"
          animate={{
            scale: [1, 1.3, 1],
            x: [0, -30, 0],
            y: [0, -10, 0]
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            repeatType: "reverse",
            delay: 1
          }}
        />
        <motion.div
          className="absolute bottom-1/4 left-1/3 w-64 h-64 bg-purple-300/10 rounded-full mix-blend-multiply filter blur-xl"
          animate={{
            scale: [1, 1.1, 1],
            x: [0, 40, 0],
            y: [0, 30, 0]
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            repeatType: "reverse",
            delay: 2
          }}
        />
      </div>

      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="flex flex-col md:flex-row gap-6 max-w-7xl mx-auto">
          {/* Sidebar with Robot Avatar */}
          <motion.div
            initial={{ opacity: 0, x: -30, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="md:w-1/4 flex flex-col items-center p-6 rounded-3xl bg-white/80 backdrop-blur-xl border border-pink-200 shadow-2xl"
          >
            <div className="w-24 h-24 flex items-center justify-center mb-4">
              <RobotAvatar status={isLoading ? "thinking" : "online"} isTyping={isLoading} />
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-2 text-center"
            >
              <h2 className="text-xl font-bold text-blue-800">
                AI Task Assistant
              </h2>
              <p className="text-sm text-blue-600 mt-2">
                Your intelligent robot assistant for task management
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mt-8 w-full"
            >
              <h3 className="font-semibold text-blue-700 mb-3 flex items-center justify-center">
                <Sparkles className="mr-2" size={16} />
                Quick Actions
              </h3>
              <div className="space-y-2">
                {[
                  "Create a task",
                  "Show my tasks",
                  "Complete a task",
                  "Set a reminder"
                ].map((action, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                    whileHover={{ scale: 1.03, x: 5 }}
                    whileTap={{ scale: 0.98 }}
                    className="p-3 bg-white/90 backdrop-blur-sm rounded-xl border border-pink-200 cursor-pointer hover:border-blue-400 transition-all duration-300 shadow-sm hover:shadow-md"
                  >
                    <p className="text-sm text-blue-800 font-medium">{action}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>

          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col">
            <motion.div
              initial={{ opacity: 0, y: 30, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
              className="flex-1 bg-white/90 backdrop-blur-xl rounded-3xl border border-pink-200 shadow-2xl overflow-hidden flex flex-col"
            >
              {/* Chat Header */}
              <div className="p-5 border-b border-pink-200 bg-gradient-to-r from-pink-50 to-blue-50">
                <div className="flex items-center space-x-3">
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                    className={`w-3 h-3 rounded-full ${isLoading ? 'bg-yellow-500' : 'bg-green-500'}`}
                  ></motion.div>
                  <h1 className="text-xl font-bold text-blue-800">Task Management Chat</h1>
                </div>
                <p className="text-sm text-blue-600 mt-1 flex items-center">
                  <motion.span
                    className="w-2 h-2 rounded-full bg-blue-500 mr-2"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  ></motion.span>
                  {isLoading ? "AI is processing..." : "AI assistant ready to help"}
                </p>
              </div>

              {/* Messages Container */}
              <div className="flex-1 overflow-y-auto p-5 space-y-4 max-h-[calc(100vh-300px)] bg-white">
                <AnimatePresence initial={false}>
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <MessageBubble
                        role={message.role}
                        content={message.content}
                        timestamp={message.timestamp}
                      />
                    </motion.div>
                  ))}
                </AnimatePresence>

                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start mb-4"
                  >
                    <div className="max-w-[75%] rounded-2xl p-4 bg-gray-100 border border-pink-200 rounded-bl-none">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <motion.div
                            animate={{ y: [0, -5, 0] }}
                            transition={{ repeat: Infinity, duration: 1.5 }}
                            className="w-2 h-2 bg-blue-500 rounded-full"
                          ></motion.div>
                          <motion.div
                            animate={{ y: [0, -5, 0] }}
                            transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }}
                            className="w-2 h-2 bg-blue-500 rounded-full"
                          ></motion.div>
                          <motion.div
                            animate={{ y: [0, -5, 0] }}
                            transition={{ repeat: Infinity, duration: 1.5, delay: 0.4 }}
                            className="w-2 h-2 bg-blue-500 rounded-full"
                          ></motion.div>
                        </div>
                        <span className="text-sm text-blue-700 font-medium">AI is thinking...</span>
                      </div>
                    </div>
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-5 border-t border-pink-200 bg-pink-50">
                <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};