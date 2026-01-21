import React, { useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useAuth } from '../context/AuthContext';
import { useChat } from '../context/ChatContext';
import { chatService } from '../services/api';
import { type ChatMessage } from '../services/api';

interface ChatInterfaceProps {
  conversationId?: number;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ conversationId }) => {
  const { messages, addMessage, clearMessages, currentConversationId, setCurrentConversationId, isLoading, setIsLoading } = useChat();
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize conversation ID if passed as prop
  useEffect(() => {
    if (conversationId && conversationId !== currentConversationId) {
      setCurrentConversationId(conversationId);
    }
  }, [conversationId, currentConversationId, setCurrentConversationId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || !user) return;

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      id: Date.now(), // Temporary ID
      role: 'user',
      content: messageText,
      createdAt: new Date().toISOString()
    };

    addMessage(userMessage);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await chatService.sendMessage({
        message: messageText,
        conversation_id: currentConversationId || undefined
      });

      // Update conversation ID if it was created
      if (response.conversation_id && !currentConversationId) {
        setCurrentConversationId(response.conversation_id);
      }

      // Add AI response to messages
      const aiMessage: ChatMessage = {
        id: Date.now() + 1, // Temporary ID
        role: 'assistant',
        content: response.response,
        createdAt: new Date().toISOString()
      };

      addMessage(aiMessage);
    } catch (error: any) {
      console.error('Error sending message:', error);

      // Add error message to UI
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: error.message || 'Sorry, I encountered an error processing your request. Please try again.',
        createdAt: new Date().toISOString()
      };

      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Todo AI Assistant</h2>
        {user && <div className="user-info">Welcome, {user.email}</div>}
      </div>

      <MessageList messages={messages} isLoading={isLoading} />

      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isLoading || !isAuthenticated}
      />

      <div ref={messagesEndRef} />
    </div>
  );
};