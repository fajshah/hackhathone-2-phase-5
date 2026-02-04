import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Circle, Trash2, Edit3, FlagTriangleRight } from 'lucide-react';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'in-progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  dueDate?: string;
  createdAt: string;
}

interface TaskCardProps {
  task: Task;
  onToggleComplete?: (taskId: number) => void;
  onDelete?: (taskId: number) => void;
  onEdit?: (taskId: number) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onToggleComplete,
  onDelete,
  onEdit
}) => {
  const [isCompleted, setIsCompleted] = useState(task.status === 'completed');
  const [isDeleting, setIsDeleting] = useState(false);

  const handleToggleComplete = () => {
    setIsCompleted(!isCompleted);
    onToggleComplete && onToggleComplete(task.id);
  };

  const handleDelete = () => {
    setIsDeleting(true);
    setTimeout(() => {
      onDelete && onDelete(task.id);
    }, 300);
  };

  const handleEdit = () => {
    onEdit && onEdit(task.id);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600';
      case 'high': return 'text-orange-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getPriorityBg = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 border-red-300';
      case 'high': return 'bg-orange-100 border-orange-300';
      case 'medium': return 'bg-yellow-100 border-yellow-300';
      case 'low': return 'bg-green-100 border-green-300';
      default: return 'bg-gray-100 border-gray-300';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3 }}
      className={`relative overflow-hidden rounded-2xl border ${
        isCompleted
          ? 'border-green-300 bg-green-50'
          : 'border-purple-200 bg-white/80'
      } backdrop-blur-sm p-5 mb-4 shadow-sm hover:shadow-md transition-shadow duration-300`}
    >
      <AnimatePresence>
        {isDeleting && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0 bg-red-100 z-10"
          />
        )}
      </AnimatePresence>

      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1 min-w-0">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleToggleComplete}
            className={`mt-1 flex-shrink-0 ${isCompleted ? 'text-green-600' : 'text-purple-400'}`}
            disabled={isDeleting}
          >
            {isCompleted ? (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              >
                <CheckCircle size={20} className="text-green-600" />
              </motion.div>
            ) : (
              <Circle size={20} className="text-purple-400" />
            )}
          </motion.button>

          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3
                className={`font-medium truncate ${
                  isCompleted
                    ? 'text-gray-500 line-through'
                    : 'text-purple-900'
                }`}
              >
                {task.title}
              </h3>

              <span className={`text-xs px-2 py-1 rounded-full border ${getPriorityBg(task.priority)} ${getPriorityColor(task.priority)}`}>
                <FlagTriangleRight size={10} className="inline mr-1" />
                {task.priority}
              </span>
            </div>

            {task.description && (
              <p className={`text-sm mt-2 ${isCompleted ? 'text-gray-500' : 'text-gray-600'}`}>
                {task.description}
              </p>
            )}

            {task.dueDate && (
              <div className="mt-3 flex items-center text-xs text-gray-500">
                <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex space-x-2 ml-4">
          {onEdit && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleEdit}
              disabled={isDeleting}
              className="text-purple-600 hover:text-purple-800 transition-colors"
            >
              <Edit3 size={16} />
            </motion.button>
          )}

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-purple-600 hover:text-red-600 transition-colors"
          >
            <Trash2 size={16} />
          </motion.button>
        </div>
      </div>

      <div className="mt-4 flex justify-between items-center text-xs text-gray-500">
        <span>Created: {new Date(task.createdAt).toLocaleDateString()}</span>
        <span className={`px-2 py-1 rounded-full ${
          task.status === 'completed' ? 'bg-green-200 text-green-700' :
          task.status === 'in-progress' ? 'bg-blue-200 text-blue-700' :
          task.status === 'cancelled' ? 'bg-red-200 text-red-700' :
          'bg-purple-200 text-purple-700'
        }`}>
          {task.status.replace('-', ' ')}
        </span>
      </div>

      {/* Completion animation overlay */}
      <AnimatePresence>
        {isCompleted && (
          <motion.div
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
          className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-green-500 to-purple-500 z-0"
        />
        )}
      </AnimatePresence>
    </motion.div>
  );
};