import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { chatService } from '../services/api';
import { Send, Bot, User, Plus, Menu, X } from 'lucide-react';

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<{ id: number; role: 'user' | 'assistant'; content: string; timestamp: Date }[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { user, logout } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user' as const,
      content: inputValue,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the chat API
      const response = await chatService.sendMessage({ message: inputValue });
      
      // Add assistant message
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant' as const,
        content: response.response,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant' as const,
        content: `Sorry, I encountered an error: ${error.message || 'Unable to process your request'}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const quickActions = [
    "Add a new task: Buy groceries",
    "Show me my tasks",
    "Mark task as completed",
    "Set a reminder for tomorrow"
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-30 w-64 bg-white shadow-lg transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-bold text-indigo-600">Todo AI</h2>
          <button 
            onClick={() => setSidebarOpen(false)} 
            className="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <X size={24} />
          </button>
        </div>
        
        <div className="p-4">
          <div className="bg-indigo-50 rounded-lg p-4 mb-4">
            <h3 className="font-medium text-indigo-800">Quick Actions</h3>
            <div className="mt-2 space-y-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => setInputValue(action)}
                  className="block w-full text-left text-sm text-indigo-700 hover:bg-indigo-100 p-2 rounded transition-colors"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
          
          <div className="mt-6">
            <h3 className="font-medium text-gray-700 mb-2">Account</h3>
            <div className="text-sm text-gray-600">
              <p>{user?.email}</p>
              <button 
                onClick={logout}
                className="mt-2 text-red-600 hover:text-red-800 text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm z-10">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center">
              <button 
                onClick={() => setSidebarOpen(true)} 
                className="lg:hidden mr-3 text-gray-500 hover:text-gray-700"
              >
                <Menu size={24} />
              </button>
              <div className="flex items-center">
                <Bot className="text-indigo-600 mr-2" size={24} />
                <h1 className="text-xl font-bold text-gray-800">Todo Assistant</h1>
              </div>
            </div>
            <div className="hidden md:block text-sm text-gray-500">
              {user?.firstName} {user?.lastName}
            </div>
          </div>
        </header>

        {/* Messages container */}
        <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-white to-gray-50">
          <div className="max-w-3xl mx-auto">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-block p-4 bg-indigo-100 rounded-full mb-4">
                  <Bot className="text-indigo-600" size={48} />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome to Todo AI!</h2>
                <p className="text-gray-600 mb-6">How can I help you manage your tasks today?</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
                  {quickActions.map((action, index) => (
                    <button
                      key={index}
                      onClick={() => setInputValue(action)}
                      className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-indigo-300 hover:shadow-md transition-all"
                    >
                      <div className="font-medium text-gray-800">{action.split(':')[0]}</div>
                      <div className="text-sm text-gray-500 mt-1">{action.split(':')[1]}</div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message) => (
                  <div 
                    key={message.id} 
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-start max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === 'user' 
                          ? 'bg-indigo-100 ml-3' 
                          : 'bg-purple-100 mr-3'
                      }`}>
                        {message.role === 'user' ? (
                          <User className="text-indigo-600" size={18} />
                        ) : (
                          <Bot className="text-purple-600" size={18} />
                        )}
                      </div>
                      <div className={`rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-indigo-600 text-white rounded-tr-none'
                          : 'bg-white border border-gray-200 rounded-tl-none shadow-sm'
                      }`}>
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        <div className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                        }`}>
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-start max-w-[80%]">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-100 mr-3 flex items-center justify-center">
                        <Bot className="text-purple-600" size={18} />
                      </div>
                      <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
                        <div className="flex space-x-2">
                          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input area */}
        <div className="border-t border-gray-200 bg-white p-4">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex items-center">
              <div className="flex-1 bg-gray-100 rounded-full pr-4">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message here..."
                  className="w-full bg-transparent border-0 focus:ring-0 rounded-full py-3 px-4 text-gray-800"
                  disabled={isLoading}
                />
              </div>
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                className={`ml-3 flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
                  inputValue.trim() && !isLoading
                    ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                } transition-colors`}
              >
                <Send size={20} />
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-500 text-center">
              Ask me to add tasks, mark them as complete, set reminders, or anything else about your to-dos!
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};