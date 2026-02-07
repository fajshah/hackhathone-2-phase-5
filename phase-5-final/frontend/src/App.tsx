import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ChatInterface from './components/ChatInterface';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import { Task, TaskStatus } from './types/task';
import apiService from './services/api';

// Define the shape of a chat message
interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  actions?: any[];
}

const App: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: 'Hello! I\'m your todo chatbot. How can I help you today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [userId] = useState<string>('demo-user'); // In a real app, this would come from authentication

  // Load tasks on initial mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    setIsLoading(true);
    try {
      const taskData = await apiService.getTasks(userId);
      setTasks(taskData);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      // In a real app, we would show an error message to the user
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    // Add user message to the chat
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      text: message,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    // Call the backend to process the message
    try {
      setIsLoading(true);
      const response = await apiService.sendMessage({
        message: message,
        user_id: userId
      });

      // Add bot response to the chat
      const botMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        text: response.response,
        sender: 'bot',
        timestamp: new Date(),
        actions: response.actions
      };

      setMessages(prev => [...prev, botMessage]);

      // If the message resulted in actions (like creating tasks), reload tasks
      if (response.actions && response.actions.length > 0) {
        loadTasks(); // Refresh the task list
      }
    } catch (error) {
      console.error('Failed to send message:', error);

      const errorMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTaskStatusChange = async (taskId: string, newStatus: TaskStatus) => {
    try {
      await apiService.updateTask(taskId, { status: newStatus }, userId);
      // Update the local state
      setTasks(prev => prev.map(task =>
        task.id === taskId ? { ...task, status: newStatus } : task
      ));
    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  const handleCreateTask = async (taskData: any) => {
    try {
      const newTask = await apiService.createTask({ ...taskData, user_id: userId });
      setTasks(prev => [...prev, newTask]);
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  return (
    <Router>
      <div className="h-screen flex flex-col bg-gray-50">
        {/* Header */}
        <header className="bg-indigo-600 text-white p-4 shadow-md">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-xl font-bold">Todo Chatbot</h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm">User: {userId}</span>
              <div className="h-8 w-8 rounded-full bg-indigo-700 flex items-center justify-center">
                {userId.charAt(0).toUpperCase()}
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 container mx-auto p-4">
          <Routes>
            <Route
              path="/"
              element={
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
                  {/* Chat Interface - takes 2/3 width on large screens */}
                  <div className="lg:col-span-2 h-[calc(100vh-8rem)] flex flex-col">
                    <ChatInterface
                      onSendMessage={handleSendMessage}
                      messages={messages}
                      tasks={tasks}
                    />
                  </div>

                  {/* Task List - takes 1/3 width on large screens */}
                  <div className="lg:col-span-1">
                    <TaskList
                      tasks={tasks}
                      onTaskStatusChange={handleTaskStatusChange}
                    />
                  </div>
                </div>
              }
            />

            <Route
              path="/tasks"
              element={
                <div className="max-w-4xl mx-auto">
                  <TaskList
                    tasks={tasks}
                    onTaskStatusChange={handleTaskStatusChange}
                  />
                </div>
              }
            />

            <Route
              path="/chat"
              element={
                <div className="max-w-2xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
                  <ChatInterface
                    onSendMessage={handleSendMessage}
                    messages={messages}
                    tasks={tasks}
                  />
                </div>
              }
            />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-gray-800 text-white p-4 text-center text-sm">
          <p>© {new Date().getFullYear()} Todo Chatbot System. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;