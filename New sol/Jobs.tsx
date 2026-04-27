import { useEffect, useState } from 'react';
import { Building, MapPin, DollarSign, ExternalLink, BookmarkPlus, RefreshCw, Zap } from 'lucide-react';
import { useJobStore } from '../store/jobStore';
import { apiClient } from '../api/client';

const SOURCES = ['all', 'linkedin', 'internshala', 'unstop', 'mock'];

export default function Jobs() {
  const { jobs, fetchJobs, saveJob, isLoading } = useJobStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeSource, setActiveSource] = useState('all');
  const [isScanning, setIsScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState('');
  const [sourceCounts, setSourceCounts] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchJobs();
    loadSourceCounts();
  }, [fetchJobs]);

  const loadSourceCounts = async () => {
    try {
      const res = await apiClient.get('/jobs/sources');
      setSourceCounts(res.data.sources || {});
    } catch { /* silent */ }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs(searchTerm, activeSource === 'all' ? undefined : activeSource);
  };

  const handleSourceChange = (source: string) => {
    setActiveSource(source);
    fetchJobs(searchTerm, source === 'all' ? undefined : source);
  };

  const handleScanPlatforms = async () => {
    setIsScanning(true);
    setScanMessage('');
    try {
      const res = await apiClient.post('/jobs/scrape');
      setScanMessage(res.data.message);
      // Refresh after 30s to show new results
      setTimeout(async () => {
        await fetchJobs(searchTerm);
        await loadSourceCounts();
        setIsScanning(false);
      }, 30000);
    } catch {
      setScanMessage('Scan failed. Please try again.');
      setIsScanning(false);
    }
  };

  const sourceLabel = (src: string) => {
    const labels: Record<string, string> = {
      all: 'All',
      linkedin: 'LinkedIn',
      internshala: 'Internshala',
      unstop: 'Unstop',
      mock: 'Demo',
    };
    return labels[src] || src;
  };

  const sourceColor = (src: string) => {
    const colors: Record<string, string> = {
      linkedin: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      internshala: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      unstop: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      mock: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    };
    return colors[src] || 'bg-slate-700 text-slate-300';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Find Internships</h1>
          <p className="text-slate-400 mt-1">
            Live listings from LinkedIn, Internshala &amp; Unstop — matched to your resume
          </p>
        </div>

        <button
          onClick={handleScanPlatforms}
          disabled={isScanning}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white rounded-xl font-semibold shadow-lg shadow-primary-500/30 disabled:opacity-60 transition-all"
        >
          {isScanning ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Scanning...
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              Scan Platforms
            </>
          )}
        </button>
      </div>

      {/* Scan status banner */}
      {scanMessage && (
        <div className="p-4 bg-primary-500/10 border border-primary-500/30 rounded-xl text-primary-300 text-sm flex items-center gap-3">
          <RefreshCw className={`w-4 h-4 flex-shrink-0 ${isScanning ? 'animate-spin' : ''}`} />
          {scanMessage}
        </div>
      )}

      {/* Source tabs + counts */}
      <div className="flex flex-wrap gap-2">
        {SOURCES.map((src) => {
          const count = src === 'all'
            ? Object.values(sourceCounts).reduce((a, b) => a + b, 0)
            : (sourceCounts[src] || 0);

          return (
            <button
              key={src}
              onClick={() => handleSourceChange(src)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-sm font-medium transition-all ${
                activeSource === src
                  ? 'bg-primary-600/20 text-primary-400 border-primary-500/50'
                  : 'bg-slate-800/50 text-slate-400 border-slate-700/50 hover:border-slate-600'
              }`}
            >
              {sourceLabel(src)}
              {count > 0 && (
                <span className="px-1.5 py-0.5 rounded-md bg-slate-700/60 text-slate-300 text-xs">
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-3">
        <input
          type="text"
          placeholder="Search by role, company, or skill..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input-field flex-1"
        />
        <button type="submit" className="btn-primary px-6">
          Search
        </button>
      </form>

      {/* Job grid */}
      {isLoading ? (
        <div className="animate-pulse space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-36 bg-slate-800/50 rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {jobs.map((job: any) => (
            <div
              key={job.id}
              className="glass-card p-5 flex flex-col justify-between hover:border-primary-500/50 transition-all group"
            >
              <div>
                {/* Title + source badge */}
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-lg font-bold text-white group-hover:text-primary-400 transition-colors leading-tight">
                    {job.title}
                  </h3>
                  <span className={`flex-shrink-0 px-2 py-0.5 rounded-full text-xs font-medium border ${sourceColor(job.source)}`}>
                    {sourceLabel(job.source)}
                  </span>
                </div>

                {/* Meta info */}
                <div className="mt-3 space-y-1.5">
                  <div className="flex items-center text-sm text-slate-300">
                    <Building className="w-4 h-4 mr-2 text-slate-500 flex-shrink-0" />
                    {job.company}
                  </div>
                  <div className="flex items-center text-sm text-slate-300">
                    <MapPin className="w-4 h-4 mr-2 text-slate-500 flex-shrink-0" />
                    {job.location || 'Remote / Not Specified'}
                  </div>
                  {job.stipend && (
                    <div className="flex items-center text-sm text-slate-300">
                      <DollarSign className="w-4 h-4 mr-2 text-slate-500 flex-shrink-0" />
                      {job.stipend}
                      {job.duration && <span className="ml-2 text-slate-500">• {job.duration}</span>}
                    </div>
                  )}
                </div>

                {/* Skills */}
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {job.skills_required?.slice(0, 4).map((skill: string) => (
                    <span
                      key={skill}
                      className="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700"
                    >
                      {skill}
                    </span>
                  ))}
                  {job.skills_required?.length > 4 && (
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-800/50 text-slate-500">
                      +{job.skills_required.length - 4} more
                    </span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="mt-5 pt-4 border-t border-dark-border flex items-center justify-between">
                <button
                  onClick={() => saveJob(job.id)}
                  className="flex items-center text-sm text-slate-400 hover:text-primary-400 transition-colors"
                >
                  <BookmarkPlus className="w-4 h-4 mr-1.5" /> Save
                </button>
                <a
                  href={job.apply_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center px-4 py-1.5 bg-primary-600/10 text-primary-400 hover:bg-primary-600/20 rounded-lg text-sm font-medium transition-colors"
                >
                  Apply Now <ExternalLink className="w-3.5 h-3.5 ml-1.5" />
                </a>
              </div>
            </div>
          ))}

          {jobs.length === 0 && (
            <div className="col-span-full py-16 text-center">
              <p className="text-slate-400 text-lg">No internships found.</p>
              <p className="text-slate-500 text-sm mt-2">
                Click <strong className="text-primary-400">Scan Platforms</strong> to fetch live listings from LinkedIn, Internshala &amp; Unstop.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
