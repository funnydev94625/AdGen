import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.error || 'Server error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

// API methods
export const videoAPI = {
  generate: async (prompt) => {
    const response = await api.post('/generate/video', { prompt });
    return response.data;
  }
};

export const imageAPI = {
  generate: async (prompt) => {
    const response = await api.post('/generate/image', { prompt });
    return response.data;
  }
};

export const pdfAPI = {
  generate: async (prompt, title) => {
    const response = await api.post('/generate/pdf', { prompt, title });
    return response.data;
  }
};

export const statusAPI = {
  getTask: async (taskId) => {
    const response = await api.get(`/status/${taskId}`);
    return response.data;
  },
  
  getAllTasks: async () => {
    const response = await api.get('/status');
    return response.data;
  }
};

export const downloadAPI = {
  downloadFile: (filename) => {
    const url = `${API_BASE_URL}/download/${filename}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
  
  getDownloadUrl: (filename) => {
    return `${API_BASE_URL}/download/${filename}`;
  }
};

export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api;
