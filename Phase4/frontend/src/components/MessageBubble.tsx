import React from 'react';
import { motion } from 'framer-motion';
import { User, Bot } from 'lucide-react';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  isLast?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  role,
  content,
  timestamp,
  isLast = false
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.4,
        ease: "easeOut"
      }}
      className={`flex mb-4 ${role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[75%] p-4 relative overflow-hidden ${
          role === 'user'
            ? 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-2xl rounded-br-none shadow-lg shadow-purple-500/25'
            : 'bg-white/80 backdrop-blur-sm text-purple-800 rounded-2xl rounded-bl-none border border-purple-200 shadow-sm hover:shadow-md transition-shadow duration-300'
        }`}
        style={{
          boxShadow: role === 'user'
            ? '0 4px 20px rgba(139, 92, 246, 0.3)'
            : '0 4px 15px rgba(139, 92, 246, 0.1)'
        }}
      >
        {/* Decorative elements */}
        <div className={`absolute top-0 left-0 w-full h-0.5 ${
          role === 'user'
            ? 'bg-gradient-to-r from-transparent via-white/50 to-transparent'
            : 'bg-gradient-to-r from-transparent via-purple-400/30 to-transparent'
        }`}></div>

        <div className="flex items-start space-x-2">
          {role === 'assistant' && (
            <div className="flex-shrink-0 mt-0.5">
              <div className="w-5 h-5 rounded-full bg-gradient-to-r from-purple-400 to-indigo-500 flex items-center justify-center">
                <Bot size={12} className="text-white" />
              </div>
            </div>
          )}

          <div className="flex-1 min-w-0">
            {content.split('\n').map((paragraph, index) => (
              <p key={index} className="leading-relaxed mb-2 last:mb-0">{paragraph}</p>
            ))}
          </div>

          {role === 'user' && (
            <div className="flex-shrink-0 mt-0.5">
              <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center">
                <User size={12} className="text-white" />
              </div>
            </div>
          )}
        </div>

        {timestamp && (
          <div className={`text-xs mt-2 ${role === 'user' ? 'text-right' : 'text-left'} ${
            role === 'user' ? 'text-purple-200' : 'text-purple-500'
          }`}>
            {timestamp}
          </div>
        )}
      </div>
    </motion.div>
  );
};