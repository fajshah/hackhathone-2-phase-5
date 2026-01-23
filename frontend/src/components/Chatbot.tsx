'use client';

import React, { useState } from 'react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: 'Hello! I am your AI 🤖', sender: 'ai' }
  ]);
  const [inputValue, setInputValue] = useState<string>('');

  const handleSend = () => {
    if (inputValue.trim() === '') return;

    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user'
    };

    setMessages(prev => [...prev, userMessage]);

    // Add fake AI reply
    setTimeout(() => {
      const aiMessage: Message = {
        id: messages.length + 2,
        text: 'Hello, I am your AI 🤖',
        sender: 'ai'
      };
      setMessages(prev => [...prev, aiMessage]);
    }, 500);

    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div style={{
      width: '400px',
      height: '600px',
      border: '2px solid #ccc',
      borderRadius: '8px',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f9f9f9',
      fontFamily: 'Arial, sans-serif',
      margin: '20px auto'
    }}>
      {/* Chat Header */}
      <div style={{
        backgroundColor: '#4a6cf7',
        color: 'white',
        padding: '15px',
        borderTopLeftRadius: '6px',
        borderTopRightRadius: '6px',
        textAlign: 'center'
      }}>
        <h3>AI Chatbot</h3>
      </div>

      {/* Messages Container */}
      <div style={{
        flex: 1,
        padding: '15px',
        overflowY: 'auto',
        backgroundColor: 'white'
      }}>
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              marginBottom: '10px',
              textAlign: message.sender === 'user' ? 'right' : 'left'
            }}
          >
            <div
              style={{
                display: 'inline-block',
                padding: '8px 12px',
                borderRadius: '12px',
                backgroundColor: message.sender === 'user' ? '#e3f2fd' : '#f0f0f0',
                border: message.sender === 'user' ? '1px solid #bbdefb' : '1px solid #e0e0e0',
                maxWidth: '80%'
              }}
            >
              {message.text}
            </div>
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div style={{
        padding: '15px',
        borderTop: '1px solid #eee',
        backgroundColor: '#fafafa',
        display: 'flex',
        gap: '8px'
      }}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '14px'
          }}
        />
        <button
          onClick={handleSend}
          style={{
            padding: '10px 15px',
            backgroundColor: '#4a6cf7',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chatbot;