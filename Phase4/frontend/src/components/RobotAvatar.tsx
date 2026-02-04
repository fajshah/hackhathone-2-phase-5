import React from 'react';
import { motion } from 'framer-motion';

interface RobotAvatarProps {
  isTyping?: boolean;
  status?: 'online' | 'thinking' | 'offline';
}

export const RobotAvatar: React.FC<RobotAvatarProps> = ({
  status = 'online',
  isTyping = false
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'thinking': return 'bg-yellow-500';
      case 'offline': return 'bg-gray-500';
      default: return 'bg-green-500';
    }
  };

  return (
    <div className="flex flex-col items-center">
      <motion.div
        className={`relative w-20 h-20 rounded-full ${
          status === 'online'
            ? 'bg-gradient-to-br from-cyan-400/20 via-purple-500/20 to-indigo-600/20'
            : status === 'thinking'
            ? 'bg-gradient-to-br from-yellow-400/20 via-orange-500/20 to-red-600/20'
            : 'bg-gradient-to-br from-gray-400/20 via-gray-500/20 to-gray-600/20'
        } backdrop-blur-lg border-2 ${
          status === 'online'
            ? 'border-cyan-400/50 shadow-lg shadow-cyan-500/30'
            : status === 'thinking'
            ? 'border-yellow-400/50 shadow-lg shadow-yellow-500/30'
            : 'border-gray-400/50'
        } overflow-hidden`}
        animate={{
          scale: isTyping ? [1, 1.05, 1] : 1,
          rotate: isTyping ? [0, 3, -3, 0] : 0,
        }}
        transition={{
          duration: 2,
          repeat: isTyping ? Infinity : 0,
          ease: "easeInOut"
        }}
      >
        {/* Robot face with advanced styling */}
        <div className="absolute inset-2 rounded-full bg-gradient-to-br from-white/90 to-gray-100/90 flex items-center justify-center shadow-inner">
          {/* Eyes */}
          <div className="flex space-x-3">
            <motion.div
              className={`w-3 h-3 rounded-full ${
                status === 'thinking' ? 'bg-gradient-to-r from-yellow-400 to-orange-500' : 'bg-gradient-to-r from-purple-600 to-indigo-700'
              } shadow-sm`}
              animate={isTyping ? {
                scale: [1, 1.2, 1],
                opacity: [0.8, 1, 0.8],
              } : {}}
              transition={{
                duration: 1.5,
                repeat: isTyping ? Infinity : 0,
                repeatType: "reverse"
              }}
            />
            <motion.div
              className={`w-3 h-3 rounded-full ${
                status === 'thinking' ? 'bg-gradient-to-r from-yellow-400 to-orange-500' : 'bg-gradient-to-r from-purple-600 to-indigo-700'
              } shadow-sm`}
              animate={isTyping ? {
                scale: [1, 1.2, 1],
                opacity: [0.8, 1, 0.8],
              } : {}}
              transition={{
                duration: 1.5,
                repeat: isTyping ? Infinity : 0,
                repeatType: "reverse",
                delay: 0.2
              }}
            />
          </div>

          {/* Mouth/Status indicator */}
          <div className="absolute bottom-3 w-6 h-1 rounded-full bg-gradient-to-r from-gray-400 to-gray-600" />
        </div>

        {/* Glowing ring effect */}
        <motion.div
          className="absolute inset-0 rounded-full opacity-50"
          animate={{
            boxShadow: isTyping
              ? [
                  '0 0 20px rgba(59, 130, 246, 0.5)',
                  '0 0 40px rgba(139, 92, 246, 0.7)',
                  '0 0 20px rgba(59, 130, 246, 0.5)'
                ]
              : '0 0 20px rgba(59, 130, 246, 0.3)',
          }}
          transition={{
            duration: 2,
            repeat: isTyping ? Infinity : 0,
            ease: "easeInOut"
          }}
        />

        {/* Additional glow effect */}
        <motion.div
          className="absolute inset-0 rounded-full opacity-30"
          animate={{
            background: isTyping
              ? [
                  'radial-gradient(circle at 30% 30%, rgba(59, 130, 246, 0.3), transparent 70%)',
                  'radial-gradient(circle at 70% 70%, rgba(139, 92, 246, 0.3), transparent 70%)',
                  'radial-gradient(circle at 30% 30%, rgba(59, 130, 246, 0.3), transparent 70%)'
                ]
              : 'radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.3), transparent 70%)'
          }}
          transition={{
            duration: 4,
            repeat: isTyping ? Infinity : 0,
            ease: "linear"
          }}
        />
      </motion.div>

      {/* Status indicator with enhanced styling */}
      <motion.div
        className="mt-4 flex items-center space-x-3"
        animate={isTyping ? { opacity: [0.7, 1, 0.7] } : {}}
        transition={{ duration: 1.5, repeat: isTyping ? Infinity : 0 }}
      >
        <motion.div
          className={`w-3 h-3 rounded-full ${getStatusColor()}`}
          animate={isTyping ? { scale: [1, 1.2, 1] } : {}}
          transition={{ repeat: isTyping ? Infinity : 0, duration: 1.5 }}
        />
        <span className={`text-sm font-medium ${
          status === 'online' ? 'text-cyan-600' :
          status === 'thinking' ? 'text-yellow-600' :
          'text-gray-600'
        } capitalize font-semibold`}>
          {status === 'online' ? 'AI Assistant Online' :
           status === 'thinking' ? 'AI is Thinking...' : 'AI Offline'}
        </span>
      </motion.div>
    </div>
  );
};