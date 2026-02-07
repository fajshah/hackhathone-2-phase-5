export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string; // ISO string format
  created_at: string; // ISO string format
  updated_at: string; // ISO string format
  user_id: string;
  assigned_to?: string;
  tags: string[];
}

export type TaskStatus = 'pending' | 'completed' | 'in-progress';

export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

// Export interfaces for reminder and session types as well
export interface Reminder {
  id: string;
  task_id: string;
  user_id: string;
  scheduled_time: string; // ISO string format
  status: 'scheduled' | 'sent' | 'cancelled';
  method: 'email' | 'push' | 'sms' | 'in-app';
  created_at: string; // ISO string format
  sent_at?: string; // ISO string format
}

export interface UserSession {
  session_id: string;
  user_id: string;
  current_context: string;
  last_interaction: string; // ISO string format
  created_at: string; // ISO string format
  expires_at: string; // ISO string format
  status: 'active' | 'expired' | 'terminated';
}