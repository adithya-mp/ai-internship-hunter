import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FileText, Wand2, Download, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';

export default function ResumeBuilder() {
  const [searchParams] = useSearchParams();
  const [jobId, setJobId] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResume, setGeneratedResume] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const idParam = searchParams.get('jobId');
    if (idParam) setJobId(idParam);
  }, [searchParams]);

  const handleGenerate = async () => {
    if (!jobId) {
      setError('Please provide a target Job ID.');
      return;
    }
    
    setIsGenerating(true);
    setError('');
    
    try {
      const res = await apiClient.post('/resume/generate', {
        job_id: jobId,
        custom_instructions: customInstructions
      });
      setGeneratedResume(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate tailored resume');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPdf = async () => {
    if (!generatedResume) return;
    try {
      const res = await apiClient.get(`/resume/${generatedResume.id}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Tailored_Resume.pdf');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch {
      setError('Failed to download PDF');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white leading-tight">AI Resume Builder</h1>
        <p className="text-slate-400 mt-1">Tailor your profile for maximum ATS compatibility</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="glass-card p-6 border-t-2 border-primary-500">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
               Generator Parameters
            </h2>
            
            {error && (
              <div className="p-3 mb-4 bg-rose-500/10 border border-rose-500/50 rounded-lg text-rose-300 text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Job ID</label>
                <input 
                  type="text" 
                  value={jobId}
                  onChange={(e) => setJobId(e.target.value)}
                  className="input-field" 
                  placeholder="Paste Job ID"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Custom Instructions</label>
                <textarea 
                  value={customInstructions}
                  onChange={(e) => setCustomInstructions(e.target.value)}
                  className="input-field min-h-[120px]" 
                  placeholder="E.g. Focus on my Python projects..."
                />
              </div>

              <button 
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full btn-primary py-3 flex items-center justify-center font-bold"
              >
                {isGenerating ? "AI Processing..." : "Generate Tailored Resume"}
              </button>
            </div>
          </div>
        </div>

        <div className="glass-card p-6 flex flex-col items-center justify-center min-h-[400px]">
          {!generatedResume && !isGenerating && (
            <div className="text-center space-y-4">
              <FileText className="w-12 h-12 text-slate-500 mx-auto" />
              <p className="text-slate-400">Your tailored resume will appear here.</p>
            </div>
          )}

          {isGenerating && (
            <div className="text-center space-y-4">
              <div className="w-12 h-12 border-4 border-slate-700 border-t-primary-500 rounded-full animate-spin mx-auto"></div>
              <p className="text-primary-400 font-medium animate-pulse">Gemini AI is analyzing the job requirements...</p>
            </div>
          )}

          {generatedResume && !isGenerating && (
            <div className="w-full text-left">
              <h3 className="text-xl font-bold text-white mb-2 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-emerald-400"/> Success!
              </h3>
              <p className="text-sm text-slate-400 mb-6 font-medium">Your resume is ready for download.</p>
              
              <div className="bg-slate-900 border border-dark-border rounded-xl p-4 overflow-y-auto max-h-[300px]">
                <pre className="text-xs text-slate-300 font-mono whitespace-pre-wrap">
                  {JSON.stringify(generatedResume.content, null, 2)}
                </pre>
              </div>
              
              <button onClick={downloadPdf} className="mt-6 w-full btn-primary flex justify-center items-center py-3">
                <Download className="w-4 h-4 mr-2" /> Download PDF
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
