'use client'


import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Sparkles } from 'lucide-react';
import type { FormEvent } from 'react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      onSubmit={handleSubmit}
      className="w-full max-w-4xl mx-auto"
    >
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-indigo-400/20 rounded-2xl blur-md opacity-0 group-focus-within:opacity-100 transition-opacity duration-300"></div>

        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me to manage your tasks..."
          disabled={disabled}
          className="w-full bg-white/90 backdrop-blur-sm border border-purple-300/50 rounded-2xl py-4 pl-16 pr-20 text-purple-900 placeholder-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/80 resize-none transition-all duration-300 shadow-lg group-focus-within:shadow-xl"
          rows={1}
          style={{ minHeight: '60px', maxHeight: '150px' }}
        />

        <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-purple-500/60">
          <Sparkles size={18} />
        </div>

        <motion.button
          whileHover={{ scale: 1.05, boxShadow: "0 0 20px rgba(139, 92, 246, 0.4)" }}
          whileTap={{ scale: 0.95 }}
          type="submit"
          disabled={!message.trim() || disabled}
          className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-3 rounded-full ${
            message.trim() && !disabled
              ? 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-lg shadow-purple-500/30'
              : 'bg-gray-300 text-gray-500'
          } transition-all duration-300`}
        >
          <Send size={18} />
        </motion.button>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-3 text-center text-xs text-purple-600/70"
      >
        AI assistant can help you create, list, update, and manage your tasks
      </motion.div>
    </motion.form>
  );
};