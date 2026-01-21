import React from 'react';
import { useParams } from 'react-router-dom';
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

export const TaskDetails: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const { user } = useAuth();

  // Mock task data - in a real app, this would come from an API call
  const mockTask: Task = {
    id: parseInt(taskId || '1'),
    title: taskId === '1' ? 'Buy groceries' : taskId === '2' ? 'Complete project proposal' : 'Schedule team meeting',
    description: taskId === '1'
      ? 'Milk, bread, eggs, fruits'
      : taskId === '2'
        ? 'Finish the proposal document for client review'
        : 'Schedule with team members for next week',
    status: taskId === '1' ? 'pending' : taskId === '2' ? 'in-progress' : 'completed',
    priority: taskId === '1' ? 'medium' : taskId === '2' ? 'high' : 'low',
    dueDate: taskId === '2' ? new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString() : undefined,
    createdAt: new Date().toISOString(),
  };

  const handleToggleComplete = async (id: number) => {
    // In a real app, this would be an API call to update the task
    console.log(`Toggling task ${id} status`);
  };

  const handleDeleteTask = async (id: number) => {
    // In a real app, this would be an API call to delete the task
    console.log(`Deleting task ${id}`);
  };

  if (!user) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="task-details-page">
      <h1>Task Details</h1>
      <TaskCard
        task={mockTask}
        onToggleComplete={handleToggleComplete}
        onDelete={handleDeleteTask}
      />

      <div className="task-actions">
        <button className="btn btn-primary">Edit Task</button>
        <button className="btn btn-secondary">Add Subtask</button>
      </div>
    </div>
  );
};