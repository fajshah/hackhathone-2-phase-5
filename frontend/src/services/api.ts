import axios, { AxiosInstance } from 'axios';

// Define API configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 seconds timeout
    });

    // Add request interceptor to include authentication token if available
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('todo-chatbot-token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle errors globally
    this.api.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        // Handle specific error cases
        if (error.response?.status === 401) {
          // Token might be expired, clear and redirect to login
          localStorage.removeItem('todo-chatbot-token');
          window.location.href = '/login';
        }

        return Promise.reject(error);
      }
    );
  }

  // Task-related API calls
  async getTasks(userId: string) {
    try {
      const response = await this.api.get(`/tasks?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getTaskById(taskId: string, userId: string) {
    try {
      const response = await this.api.get(`/tasks/${taskId}?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createTask(taskData: any) {
    try {
      const response = await this.api.post('/tasks', taskData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateTask(taskId: string, taskData: any, userId: string) {
    try {
      const response = await this.api.put(`/tasks/${taskId}?user_id=${userId}`, taskData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteTask(taskId: string, userId: string) {
    try {
      const response = await this.api.delete(`/tasks/${taskId}?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async completeTask(taskId: string, userId: string) {
    try {
      const response = await this.api.post(`/tasks/${taskId}/complete?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async assignTask(taskId: string, assignedUserId: string, userId: string) {
    try {
      const response = await this.api.post(
        `/tasks/${taskId}/assign?assigned_user_id=${assignedUserId}&user_id=${userId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Chat-related API calls
  async sendMessage(chatData: any) {
    try {
      const response = await this.api.post('/chat', chatData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getSessionContext(userId: string) {
    try {
      const response = await this.api.get(`/chat/session?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async resetSessionContext(userId: string) {
    try {
      const response = await this.api.post(`/chat/session/reset?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Reminder-related API calls
  async createReminder(reminderData: any) {
    try {
      const response = await this.api.post('/reminders', reminderData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getReminders(userId: string) {
    try {
      const response = await this.api.get(`/reminders?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async cancelReminder(reminderId: string, userId: string) {
    try {
      const response = await this.api.delete(`/reminders/${reminderId}?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Health check
  async healthCheck() {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Helper method to handle errors consistently
  private handleError(error: any) {
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.detail || error.response.statusText;
      return new Error(`API Error: ${errorMessage} (Status: ${error.response.status})`);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network Error: No response received from server');
    } else {
      // Something else happened
      return new Error(`Request Error: ${error.message}`);
    }
  }
}

// Create a singleton instance of the API service
const apiService = new ApiService();

export default apiService;