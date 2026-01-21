import React, { createContext, useContext, useState, ReactNode } from 'react';
import { type ChatMessage } from '../services/api';

interface ChatContextType {
  messages: ChatMessage[];
  isLoading: boolean;
  currentConversationId: number | null;
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  setIsLoading: (loading: boolean) => void;
  setCurrentConversationId: (id: number | null) => void;
  clearMessages: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);

  const addMessage = (message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
  };

  const clearMessages = () => {
    setMessages([]);
    setCurrentConversationId(null);
  };

  const value: ChatContextType = {
    messages,
    isLoading,
    currentConversationId,
    addMessage,
    setMessages,
    setIsLoading,
    setCurrentConversationId,
    clearMessages,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};