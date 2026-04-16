import { create } from 'zustand';
import { apiClient } from '../api/client';

interface User {
  id: string;
  email: string;
  full_name: string;
  bio?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  profile_data?: any;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('applyiq_token'),
  isAuthenticated: !!localStorage.getItem('applyiq_token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('applyiq_token', access_token);
      set({ user, token: access_token, isAuthenticated: true, isLoading: false });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to login', 
        isLoading: false 
      });
      throw error;
    }
  },

  register: async (name, email, password) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post('/auth/register', { full_name: name, email, password });
      // Login after register
      await get().login(email, password);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to register', 
        isLoading: false 
      });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('applyiq_token');
    set({ user: null, token: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const { token } = get();
    if (!token) return;

    set({ isLoading: true });
    try {
      const response = await apiClient.get('/auth/me');
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem('applyiq_token');
      set({ user: null, token: null, isAuthenticated: false, isLoading: false });
    }
  }
}));
