import React from 'react';
import { Task, TaskStatus, TaskPriority } from '../types/task';

interface TaskListProps {
  tasks: Task[];
  onTaskStatusChange: (taskId: string, newStatus: TaskStatus) => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onTaskStatusChange }) => {
  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in-progress':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case 'low':
        return 'bg-gray-100 text-gray-800';
      case 'medium':
        return 'bg-blue-100 text-blue-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'critical':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-medium text-gray-700 mb-4">Your Tasks</h3>

      {tasks.length === 0 ? (
        <p className="text-gray-500 italic">No tasks found. Create one using the chat!</p>
      ) : (
        <ul className="space-y-2">
          {tasks.map((task) => (
            <li
              key={task.id}
              className={`p-4 bg-white rounded-lg shadow-sm border-l-4 ${
                task.status === 'completed'
                  ? 'border-l-green-500'
                  : task.status === 'in-progress'
                    ? 'border-l-blue-500'
                    : 'border-l-yellow-500'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className={`font-medium ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                      {task.title}
                    </h4>
                    <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>

                  {task.description && (
                    <p className="text-gray-600 text-sm mb-2">{task.description}</p>
                  )}

                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(task.status)}`}>
                      {task.status}
                    </span>

                    {task.due_date && (
                      <span className="text-xs text-gray-500">
                        Due: {new Date(task.due_date).toLocaleDateString()}
                      </span>
                    )}

                    {task.assigned_to && (
                      <span className="text-xs text-gray-500">
                        Assigned to: {task.assigned_to}
                      </span>
                    )}
                  </div>

                  {task.tags && task.tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {task.tags.map((tag, index) => (
                        <span key={index} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex flex-col items-end ml-2">
                  <button
                    onClick={() => onTaskStatusChange(task.id, task.status === 'completed' ? 'pending' : 'completed')}
                    className={`px-3 py-1 rounded text-sm ${
                      task.status === 'completed'
                        ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {task.status === 'completed' ? 'Reopen' : 'Complete'}
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TaskList;