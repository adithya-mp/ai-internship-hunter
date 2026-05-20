import { create } from 'zustand';
import { apiClient } from '../api/client';

export interface Job {
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

export interface SelectedJob extends Job {
  job_id: string;      // Inferred external ID
  source_url: string;  // apply_url
}

interface JobState {
  jobs: Job[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  matchedJobs: any[];
  savedJobs: Job[];
  isLoading: boolean;
  selectedJob: SelectedJob | null;

  fetchJobs: (query?: string, source?: string) => Promise<void>;
  fetchMatchedJobs: () => Promise<void>;
  fetchSavedJobs: () => Promise<void>;
  saveJob: (jobId: string) => Promise<void>;
  selectJob: (job: Job) => void;
  clearSelectedJob: () => void;
}

export const useJobStore = create<JobState>((set) => ({
  jobs: [],
  matchedJobs: [],
  savedJobs: [],
  isLoading: false,
  selectedJob: null,

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

  selectJob: (job: Job) => {
    let jobId = job.id; // fallback
    const sourceUrl = job.apply_url || '';

    if (job.source === 'linkedin' && job.apply_url) {
      // URL: https://www.linkedin.com/jobs/view/123456789
      const match = job.apply_url.match(/\/view\/(\d+)/);
      if (match) {
        jobId = match[1];
      }
    } else if (job.source === 'internshala' && job.apply_url) {
      // URL: https://internshala.com/internship/detail/software-development-internship-171612...
      const match = job.apply_url.match(/-(\d+)$/) || job.apply_url.match(/\/detail\/.*?-(\d+)/);
      if (match) {
        jobId = match[1];
      } else {
        const segments = job.apply_url.split('/');
        const last = segments[segments.length - 1];
        if (last) jobId = last;
      }
    } else if (job.source === 'unstop' && job.apply_url) {
      // URL: https://unstop.com/o/123456 or similar
      const match = job.apply_url.match(/\/o\/(\d+)/) || job.apply_url.match(/-(\d+)$/);
      if (match) {
        jobId = match[1];
      }
    }
    set({ selectedJob: { ...job, job_id: jobId, source_url: sourceUrl } });
  },

  clearSelectedJob: () => {
    set({ selectedJob: null });
  },
}));

