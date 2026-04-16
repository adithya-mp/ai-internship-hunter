import { create } from 'zustand';
import { apiClient } from '../api/client';

interface Job {
  id: string;
  title: string;
  company: string;
  location?: string;
  source: string;
  skills_required?: string[];
}

interface JobState {
  jobs: Job[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  matchedJobs: any[];
  savedJobs: Job[];
  isLoading: boolean;
  
  fetchJobs: (query?: string) => Promise<void>;
  fetchMatchedJobs: () => Promise<void>;
  fetchSavedJobs: () => Promise<void>;
  saveJob: (jobId: string) => Promise<void>;
}

export const useJobStore = create<JobState>((set) => ({
  jobs: [],
  matchedJobs: [],
  savedJobs: [],
  isLoading: false,

  fetchJobs: async (query = '') => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get(`/jobs?q=${query}`);
      set({ jobs: response.data.items, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      console.error(error);
    }
  },

  fetchMatchedJobs: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get('/jobs/matched');
      set({ matchedJobs: response.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      console.error(error);
    }
  },

  fetchSavedJobs: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get('/jobs/user/saved');
      set({ savedJobs: response.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      console.error(error);
    }
  },

  saveJob: async (jobId: string) => {
    try {
      await apiClient.post(`/jobs/${jobId}/save`);
      // Optimistically fetch saved
      const response = await apiClient.get('/jobs/user/saved');
      set({ savedJobs: response.data });
    } catch (error) {
      console.error('Failed to save job', error);
    }
  }
}));
