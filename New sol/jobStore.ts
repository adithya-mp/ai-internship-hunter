import { create } from 'zustand';
import { apiClient } from '../api/client';

interface Job {
  id: string;
  title: string;
  company: string;
  location?: string;
  source: string;
  skills_required?: string[];
  stipend?: string;
  duration?: string;
  apply_url?: string;
}

interface JobState {
  jobs: Job[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  matchedJobs: any[];
  savedJobs: Job[];
  isLoading: boolean;

  fetchJobs: (query?: string, source?: string) => Promise<void>;
  fetchMatchedJobs: () => Promise<void>;
  fetchSavedJobs: () => Promise<void>;
  saveJob: (jobId: string) => Promise<void>;
}

export const useJobStore = create<JobState>((set) => ({
  jobs: [],
  matchedJobs: [],
  savedJobs: [],
  isLoading: false,

  fetchJobs: async (query = '', source?: string) => {
    set({ isLoading: true });
    try {
      const params: Record<string, string> = {};
      if (query) params.q = query;
      if (source) params.source = source;

      const response = await apiClient.get('/jobs', { params });
      set({ jobs: response.data.items, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      console.error('fetchJobs error:', error);
    }
  },

  fetchMatchedJobs: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get('/jobs/matched');
      set({ matchedJobs: response.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      console.error('fetchMatchedJobs error:', error);
    }
  },

  fetchSavedJobs: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get('/jobs/user/saved');
      set({ savedJobs: response.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      console.error('fetchSavedJobs error:', error);
    }
  },

  saveJob: async (jobId: string) => {
    try {
      await apiClient.post(`/jobs/${jobId}/save`);
      const response = await apiClient.get('/jobs/user/saved');
      set({ savedJobs: response.data });
    } catch (error) {
      console.error('saveJob error:', error);
    }
  },
}));
