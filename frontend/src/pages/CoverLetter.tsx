import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Mail, Download, CheckCircle, PenTool, Sparkles, 
  Building, MapPin, ExternalLink, RefreshCw, 
  Clipboard, ClipboardCheck, ChevronRight, Briefcase 
} from 'lucide-react';
import { useJobStore } from '../store/jobStore';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../api/client';

export default function CoverLetter() {
  const { selectedJob, selectJob, clearSelectedJob, savedJobs, fetchSavedJobs } = useJobStore();
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const [customInstructions, setCustomInstructions] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedLetter, setGeneratedLetter] = useState<any>(null);
  const [error, setError] = useState('');
  const [isCopied, setIsCopied] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    fetchSavedJobs();
  }, [fetchSavedJobs]);

  const handleGenerate = async () => {
    if (!selectedJob) {
      setError('Please select a target job.');
      return;
    }
    
    setIsGenerating(true);
    setError('');
    
    try {
      const res = await apiClient.post('/cover-letter/generate', {
        job_id: selectedJob.id,
        custom_instructions: customInstructions
      });
      setGeneratedLetter(res.data);
      setIsCopied(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate cover letter');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPdf = async () => {
    if (!generatedLetter) return;
    setIsDownloading(true);
    try {
      const res = await apiClient.get(`/cover-letter/${generatedLetter.id}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Cover_Letter_${selectedJob?.company.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch {
      setError('Failed to download PDF');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleCopyToClipboard = () => {
    if (!generatedLetter) return;
    navigator.clipboard.writeText(generatedLetter.content);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Mail className="w-8 h-8 text-amber-500 animate-pulse" />
            AI Cover Letter Writer
          </h1>
          <p className="text-slate-400 mt-1">Dual-source pipeline drafting bespoke cover letters targeting specific company cultures</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Side: Parameters */}
        <div className="lg:col-span-5 space-y-6">
          {/* Target Job Selector Card */}
          <div className="glass-card p-6 border-slate-800">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-amber-400" />
              Target Internship
            </h2>

            {selectedJob ? (
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 relative group">
                <button 
                  onClick={clearSelectedJob}
                  className="absolute top-3 right-3 text-slate-500 hover:text-slate-300 text-xs transition-colors"
                >
                  Change target
                </button>
                
                <h3 className="font-bold text-slate-200 pr-16">{selectedJob.title}</h3>
                <p className="text-sm text-slate-400 mt-1 flex items-center">
                  <Building className="w-3.5 h-3.5 mr-1 text-slate-500" />
                  {selectedJob.company}
                </p>
                {selectedJob.location && (
                  <p className="text-xs text-slate-500 mt-1 flex items-center">
                    <MapPin className="w-3.5 h-3.5 mr-1 text-slate-500" />
                    {selectedJob.location}
                  </p>
                )}

                <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                  <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                    ID: {selectedJob.job_id}
                  </span>
                  <a 
                    href={selectedJob.source_url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="flex items-center text-amber-400 hover:text-amber-300"
                  >
                    View Original <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-900/50 border border-dashed border-slate-800 text-center">
                  <p className="text-slate-400 text-sm">No target internship selected</p>
                  <button 
                    onClick={() => navigate('/jobs')}
                    className="text-xs text-amber-400 hover:text-amber-300 font-semibold mt-2 inline-flex items-center gap-1"
                  >
                    Browse active jobs <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {savedJobs.length > 0 && (
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      Or select from Saved Jobs:
                    </label>
                    <select
                      onChange={(e) => {
                        const job = savedJobs.find(j => j.id === e.target.value);
                        if (job) selectJob(job);
                      }}
                      className="input-field py-2 text-sm bg-slate-900 border-slate-800 focus:ring-amber-500 focus:border-amber-500"
                      defaultValue=""
                    >
                      <option value="" disabled>-- Choose a saved job --</option>
                      {savedJobs.map(job => (
                        <option key={job.id} value={job.id}>
                          {job.title} at {job.company}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Prompt/Instructions Card */}
          <div className="glass-card p-6 border-slate-800">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <PenTool className="w-5 h-5 text-amber-400" />
              Writing Parameters
            </h2>
            
            {error && (
              <div className="p-3 mb-4 bg-rose-500/10 border border-rose-500/50 rounded-lg text-rose-300 text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Tone & focus instructions (Optional)
                </label>
                <textarea 
                  value={customInstructions}
                  onChange={(e) => setCustomInstructions(e.target.value)}
                  className="input-field min-h-[140px] text-sm border-slate-800 focus:ring-amber-500 focus:border-amber-500" 
                  placeholder="E.g. Focus on my experience scaling database services, make the tone highly enthusiastic and keep it under 3 paragraphs..."
                />
              </div>

              <button 
                onClick={handleGenerate}
                disabled={isGenerating || !selectedJob}
                className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-amber-600 hover:bg-amber-500 text-white rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-amber-500/20"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    AI Sourcing & Writing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 text-white animate-pulse" />
                    Generate Cover Letter
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Side: A4 letterhead Preview Container */}
        <div className="lg:col-span-7 space-y-6">
          {!generatedLetter && !isGenerating && (
            <div className="glass-card p-12 flex flex-col items-center justify-center min-h-[500px] border-slate-800 text-center">
              <Mail className="w-16 h-16 text-slate-700 mb-4" />
              <h3 className="text-lg font-bold text-white">Interactive Letter Preview</h3>
              <p className="text-slate-500 text-sm max-w-sm mt-2">
                Draft a highly personalized, custom cover letter for your target internship role using industry-tested conventions.
              </p>
            </div>
          )}

          {isGenerating && (
            <div className="glass-card p-12 flex flex-col items-center justify-center min-h-[500px] border-slate-800 text-center space-y-4">
              <div className="relative w-16 h-16 flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-4 border-slate-800"></div>
                <div className="absolute inset-0 rounded-full border-4 border-amber-500 border-t-transparent animate-spin"></div>
                <PenTool className="w-6 h-6 text-amber-500 animate-pulse" />
              </div>
              <h3 className="text-lg font-bold text-white animate-pulse">Running Cover Letter Pipeline</h3>
              <div className="text-xs text-slate-400 max-w-xs space-y-1 mt-2">
                <p>1. Analyzing industry expectations for {selectedJob?.company}...</p>
                <p>2. Aligning credentials to JD criteria...</p>
                <p>3. Writing persuasive 3-4 paragraph pitch...</p>
              </div>
            </div>
          )}

          {generatedLetter && !isGenerating && (
            <div className="space-y-4">
              <div className="flex items-center justify-between px-2">
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle className="w-4 h-4" />
                  Successfully tailored!
                </span>
                
                <div className="flex items-center gap-2">
                  <button 
                    onClick={handleCopyToClipboard}
                    className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors bg-slate-850 px-2.5 py-1.5 rounded-lg border border-slate-800"
                  >
                    {isCopied ? (
                      <>
                        <ClipboardCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400 font-semibold">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Clipboard className="w-3.5 h-3.5" />
                        <span>Copy Text</span>
                      </>
                    )}
                  </button>

                  <button 
                    onClick={downloadPdf}
                    disabled={isDownloading}
                    className="flex items-center gap-1.5 text-xs text-white bg-amber-600 hover:bg-amber-500 transition-colors px-2.5 py-1.5 rounded-lg border border-amber-700 shadow-md shadow-amber-500/10"
                  >
                    {isDownloading ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Download className="w-3.5 h-3.5" />
                    )}
                    <span>PDF</span>
                  </button>
                </div>
              </div>

              {/* Cover Letter Sheet */}
              <div 
                className="bg-white text-slate-900 shadow-2xl rounded-lg p-8 sm:p-12 mx-auto font-serif text-[12px] leading-relaxed max-w-[800px] border border-slate-200"
              >
                {/* Sender Address */}
                <div className="text-slate-800 font-bold mb-1">
                  {user?.full_name || 'Candidate Name'}
                </div>
                <div className="text-slate-500 text-[10px] mb-6">
                  {user?.email || 'email@example.com'} &bull; {user?.profile_data?.location || 'India'}
                </div>

                {/* Date */}
                <div className="text-slate-600 mb-6 font-medium">
                  {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                </div>

                {/* Recipient */}
                <div className="text-slate-800 mb-6">
                  <div><strong>Hiring Team / Recruiting Team</strong></div>
                  <div>{selectedJob?.company}</div>
                  <div>{selectedJob?.location || 'Remote'}</div>
                </div>

                {/* Letter Body */}
                <div className="text-slate-700 space-y-4 text-justify whitespace-pre-wrap">
                  {generatedLetter.content}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
