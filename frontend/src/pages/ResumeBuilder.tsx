import { useState } from 'react';
import { FileText, Wand2, Download, Eye, FileUp } from 'lucide-react';
import { apiClient } from '../api/client';

export default function ResumeBuilder() {
  const [jobId, setJobId] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [generatedResume, setGeneratedResume] = useState<any>(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (!jobId) {
      setError('Please provide a target Job ID to tailor the resume.');
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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate tailored resume');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPdf = async () => {
    if (!generatedResume) return;
    try {
      // Create a blob from the download URL to force download
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
        <h1 className="text-3xl font-bold text-white">AI Resume Builder</h1>
        <p className="text-slate-400 mt-1">Tailor your resume precisely to any job description in seconds</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="space-y-6">
          <div className="glass-card p-6 border-t-4 border-t-primary-500">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <FileUp className="w-5 h-5 mr-3 text-primary-400" />
              Generator Settings
            </h2>
            
            {error && (
              <div className="p-3 mb-4 bg-rose-500/10 border border-rose-500/50 rounded-lg text-rose-300 text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Target Job ID</label>
                <input 
                  type="text" 
                  value={jobId}
                  onChange={(e) => setJobId(e.target.value)}
                  placeholder="Paste Job ID (e.g. from Jobs tab)" 
                  className="input-field" 
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Custom Instructions (Optional)</label>
                <textarea 
                  value={customInstructions}
                  onChange={(e) => setCustomInstructions(e.target.value)}
                  placeholder="E.g. Highlight my leadership experience and cloud certifications more prominently." 
                  className="input-field min-h-[120px] resize-y" 
                />
              </div>

              <button 
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full btn-primary py-3 flex items-center justify-center font-bold text-lg disabled:opacity-50"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white mr-3"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5 mr-2" /> Generate Tailored Resume
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Preview / Output */}
        <div className="glass-card p-6 flex flex-col items-center justify-center min-h-[400px]">
          {!generatedResume && !isGenerating && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto border border-dark-border">
                <FileText className="w-8 h-8 text-slate-500" />
              </div>
              <div>
                <p className="text-slate-300 font-medium">No resume generated yet</p>
                <p className="text-sm text-slate-500 max-w-sm mt-1">Configure your parameters and click generate to create an AI-optimized resume targeting your chosen job.</p>
              </div>
            </div>
          )}

          {isGenerating && (
            <div className="text-center space-y-6">
              <div className="relative">
                <div className="w-20 h-20 border-4 border-slate-700 border-t-primary-500 rounded-full animate-spin mx-auto"></div>
                <Wand2 className="w-8 h-8 text-primary-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
              </div>
              <div>
                <p className="text-primary-400 font-bold text-lg animate-pulse">Running AI Engine</p>
                <p className="text-sm text-slate-400">Analyzing Job Description & Profiling Gap...</p>
              </div>
            </div>
          )}

          {generatedResume && !isGenerating && (
            <div className="w-full flex justify-between items-start h-full">
               <div className="w-full">
                 <h3 className="text-xl font-bold text-white mb-2 flex items-center"><CheckCircle className="w-5 h-5 mr-2 text-emerald-400"/> Resume Completed!</h3>
                 <p className="text-sm text-slate-400 mb-6">Your tailored resume is ready. You can download the ATS-friendly PDF directly.</p>
                 
                 <div className="bg-slate-900 border border-dark-border rounded-xl p-4 overflow-y-auto max-h-[300px]">
                   <pre className="text-xs text-slate-300 font-mono whitespace-pre-wrap">
                     {JSON.stringify(generatedResume.content, null, 2)}
                   </pre>
                 </div>
                 
                 <div className="mt-6 flex space-x-4">
                   <button onClick={downloadPdf} className="flex-1 btn-primary flex justify-center items-center">
                     <Download className="w-4 h-4 mr-2" /> Download PDF
                   </button>
                   <button className="flex-1 btn-secondary flex justify-center items-center">
                     <Eye className="w-4 h-4 mr-2" /> Quick Preview
                   </button>
                 </div>
               </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
