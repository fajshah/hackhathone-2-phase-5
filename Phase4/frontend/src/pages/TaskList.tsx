import React, { useState, useEffect } from 'react';
import { TaskCard } from '../components/TaskCard';
import { useAuth } from '../context/AuthContext';
import '../App.css';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'completed' | 'in-progress';
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  createdAt: string;
}

export const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        // For now, we'll simulate fetching tasks
        // In a real app, this would be an API call to get user's tasks
        const mockTasks: Task[] = [
          {
            id: 1,
            title: 'Buy groceries',
            description: 'Milk, bread, eggs, fruits',
            status: 'pending',
            priority: 'medium',
            createdAt: new Date().toISOString(),
          },
          {
            id: 2,
            title: 'Complete project proposal',
            description: 'Finish the proposal document for client review',
            status: 'in-progress',
            priority: 'high',
            dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days from now
            createdAt: new Date().toISOString(),
          },
          {
            id: 3,
            title: 'Schedule team meeting',
            status: 'completed',
            priority: 'low',
            createdAt: new Date().toISOString(),
          },
        ];

        setTasks(mockTasks);
      } catch (err) {
        setError('Failed to load tasks');
        console.error('Error fetching tasks:', err);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchTasks();
    }
  }, [user]);

  const handleToggleComplete = async (taskId: number) => {
    try {
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId
            ? { ...task, status: task.status === 'completed' ? 'pending' : 'completed' }
            : task
        )
      );

      // In a real app, this would be an API call to update the task
    } catch (err) {
      console.error('Error updating task:', err);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
      // In a real app, this would be an API call to delete the task
    } catch (err) {
      console.error('Error deleting task:', err);
    }
  };

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="task-list-page">
      <h1>Your Tasks</h1>
      {tasks.length === 0 ? (
        <div className="no-tasks">
          <p>No tasks found. Start by adding a new task!</p>
        </div>
      ) : (
        <div className="task-list">
          {tasks.map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onToggleComplete={handleToggleComplete}
              onDelete={handleDeleteTask}
            />
          ))}
        </div>
      )}
    </div>
  );
};