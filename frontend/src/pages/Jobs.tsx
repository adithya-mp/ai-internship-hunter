import { useEffect, useState } from 'react';
import { Building, MapPin, DollarSign, ExternalLink, BookmarkPlus, CheckCircle } from 'lucide-react';
import { useJobStore } from '../store/jobStore';

export default function Jobs() {
  const { jobs, fetchJobs, saveJob, isLoading } = useJobStore();
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs(searchTerm);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Find Jobs</h1>
          <p className="text-slate-400 mt-1">Discover your next career move</p>
        </div>
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="Search by role or company..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field max-w-xs"
          />
          <button type="submit" className="btn-primary">
            Search
          </button>
        </form>
      </div>

      {isLoading ? (
        <div className="animate-pulse space-y-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-32 bg-slate-800/50 rounded-xl"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {jobs.map((job: any) => (
            <div key={job.id} className="glass-card p-6 flex flex-col justify-between hover:border-primary-500/50 transition-colors group">
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold text-white group-hover:text-primary-400 transition-colors">
                      {job.title}
                    </h3>
                    <div className="mt-2 space-y-2">
                      <div className="flex items-center text-sm text-slate-300">
                        <Building className="w-4 h-4 mr-2 text-slate-500" />
                        {job.company}
                      </div>
                      <div className="flex items-center text-sm text-slate-300">
                        <MapPin className="w-4 h-4 mr-2 text-slate-500" />
                        {job.location || 'Remote'}
                      </div>
                      <div className="flex items-center text-sm text-slate-300">
                        <DollarSign className="w-4 h-4 mr-2 text-slate-500" />
                        {job.salary_range || 'Competitive'}
                      </div>
                    </div>
                  </div>
                  <button 
                    onClick={() => saveJob(job.id)}
                    className="p-2 bg-slate-800 hover:bg-primary-500/20 text-slate-400 hover:text-primary-400 rounded-lg transition-colors"
                    title="Save Job"
                  >
                    <BookmarkPlus className="w-5 h-5" />
                  </button>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {job.skills_required?.slice(0, 3).map((skill: string) => (
                    <span key={skill} className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300">
                      {skill}
                    </span>
                  ))}
                  {job.skills_required?.length > 3 && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800/50 text-slate-400">
                      +{job.skills_required.length - 3} more
                    </span>
                  )}
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t border-dark-border flex items-center justify-between">
                <button className="flex items-center text-sm text-slate-400 hover:text-white transition-colors duration-200">
                  <CheckCircle className="w-4 h-4 mr-1" /> Target Job
                </button>
                <a 
                  href={job.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="flex items-center px-4 py-2 bg-primary-600/10 text-primary-400 hover:bg-primary-600/20 rounded-lg text-sm font-medium transition-colors"
                >
                  Apply Now <ExternalLink className="w-4 h-4 ml-2" />
                </a>
              </div>
            </div>
          ))}
          {jobs.length === 0 && (
             <div className="col-span-full py-12 text-center text-slate-400">
               No jobs found. Try adjusting your search query!
             </div>
          )}
        </div>
      )}
    </div>
  );
}
