"use client";

import { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, Bot, User } from 'lucide-react';

export default function PremiumChatbot() {
  const [messages, setMessages] = useState<{ sender: 'user' | 'ai'; text: string; id: number }[]>([
    { sender: 'ai', text: 'Hello! I\'m your premium AI assistant. How can I help you manage your tasks today?', id: 1 }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input, id: Date.now() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response after a delay
    setTimeout(() => {
      const aiResponses = [
        "I understand your request. How else can I assist you?",
        "That's noted. Is there anything else you'd like to do?",
        "Your task has been processed. What else can I help with?",
        "I've completed that action. Do you have other tasks?",
        "Thanks for sharing. How can I help further?"
      ];

      const aiMessage = {
        sender: 'ai',
        text: aiResponses[Math.floor(Math.random() * aiResponses.length)],
        id: Date.now() + 1
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-blue-50 to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-pink-200 overflow-hidden">

          {/* Header */}
          <div className="bg-gradient-to-r from-pink-500 to-blue-600 p-5 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-400 to-blue-500 flex items-center justify-center">
                    <Bot size={20} className="text-white" />
                  </div>
                  <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
                </div>
                <div>
                  <h1 className="text-lg font-semibold">AI Task Assistant</h1>
                  <p className="text-pink-100 text-sm">Online • Ready to help</p>
                </div>
              </div>
            </div>
          </div>

          {/* Messages Container */}
          <div className="h-[50vh] overflow-y-auto p-4 space-y-4 bg-white">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl p-4 ${
                    msg.sender === 'user'
                      ? 'bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-br-none'
                      : 'bg-white text-blue-900 rounded-bl-none border border-pink-200'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {msg.sender === 'ai' ? (
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-r from-pink-400 to-blue-500 flex items-center justify-center">
                          <Bot size={14} className="text-white" />
                        </div>
                      </div>
                    ) : null}

                    <div className="flex-1">
                      {msg.text}
                    </div>

                    {msg.sender === 'user' ? (
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-r from-blue-400 to-cyan-500 flex items-center justify-center">
                          <User size={14} className="text-white" />
                        </div>
                      </div>
                    ) : null}
                  </div>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-2xl p-4 bg-white rounded-bl-none border border-pink-200">
                  <div className="flex items-center space-x-2">
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-r from-pink-400 to-blue-500 flex items-center justify-center">
                        <Bot size={14} className="text-white" />
                      </div>
                    </div>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce delay-75"></div>
                      <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce delay-150"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-pink-200 bg-pink-50">
            <div className="flex items-end space-x-2">
              <div className="flex-1 relative">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Describe your task or ask for help..."
                  className="w-full bg-pink-100 border border-pink-300 rounded-xl py-3 pl-4 pr-12 text-blue-900 placeholder-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="absolute left-3 top-3 text-pink-600">
                  <Sparkles size={16} />
                </div>
              </div>

              <button
                onClick={handleSend}
                disabled={!input.trim() || isTyping}
                className={`p-3 rounded-xl ${
                  input.trim() && !isTyping
                    ? 'bg-gradient-to-r from-pink-500 to-blue-600 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}