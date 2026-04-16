import { useState } from 'react';
import { Mail, Wand2, Download, CheckCircle, PenTool } from 'lucide-react';
import { apiClient } from '../api/client';

export default function CoverLetter() {
  const [jobId, setJobId] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [generatedLetter, setGeneratedLetter] = useState<any>(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (!jobId) {
      setError('Please provide a target Job ID for the cover letter context.');
      return;
    }
    
    setIsGenerating(true);
    setError('');
    
    try {
      const res = await apiClient.post('/cover_letter/generate', {
        job_id: jobId,
        custom_instructions: customInstructions
      });
      setGeneratedLetter(res.data);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate cover letter');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPdf = async () => {
    if (!generatedLetter) return;
    try {
      const res = await apiClient.get(`/cover_letter/${generatedLetter.id}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Cover_Letter_${generatedLetter.company.replace(' ', '_')}.pdf`);
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
        <h1 className="text-3xl font-bold text-white">AI Cover Letter Writer</h1>
        <p className="text-slate-400 mt-1">Generate a highly personalized cover letter utilizing your precise skill gaps and job matches.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="glass-card p-6 border-t-4 border-t-amber-500">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <PenTool className="w-5 h-5 mr-3 text-amber-400" />
              Writing Parameters
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
                  className="input-field border-slate-700/50" 
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Tone & Focus (Optional)</label>
                <textarea 
                  value={customInstructions}
                  onChange={(e) => setCustomInstructions(e.target.value)}
                  placeholder="E.g. Keep it confident and brief. Focus heavily on my React capabilities." 
                  className="input-field min-h-[120px] border-slate-700/50 resize-y" 
                />
              </div>

              <button 
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full py-3 bg-amber-600 hover:bg-amber-500 text-white rounded-lg flex items-center justify-center font-bold text-lg disabled:opacity-50 transition-colors shadow-lg shadow-amber-500/20"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white mr-3"></div>
                    Writing...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5 mr-2" /> Write Cover Letter
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="glass-card p-6 flex flex-col items-center justify-center min-h-[400px]">
          {!generatedLetter && !isGenerating && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto border border-dark-border">
                <Mail className="w-8 h-8 text-slate-500" />
              </div>
              <div>
                <p className="text-slate-300 font-medium">Ready to Write</p>
                <p className="text-sm text-slate-500 max-w-sm mt-1">Provide the parameters on the left to ignite the Gemini AI engine for an incredible cover letter.</p>
              </div>
            </div>
          )}

          {isGenerating && (
            <div className="text-center space-y-6">
              <div className="relative">
                <div className="w-20 h-20 border-4 border-slate-700 border-t-amber-500 rounded-full animate-spin mx-auto"></div>
                <PenTool className="w-8 h-8 text-amber-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
              </div>
              <div>
                <p className="text-amber-400 font-bold text-lg animate-pulse">Drafting Masterpiece</p>
                <p className="text-sm text-slate-400">Synthesizing tone and formatting parameters...</p>
              </div>
            </div>
          )}

          {generatedLetter && !isGenerating && (
            <div className="w-full flex flex-col items-start h-full text-left">
               <h3 className="text-xl font-bold text-white mb-2 flex items-center w-full">
                 <CheckCircle className="w-5 h-5 mr-2 text-emerald-400"/> Letter Drafted
               </h3>
               
               <div className="w-full mt-4 bg-slate-900 border border-dark-border rounded-xl p-6 overflow-y-auto max-h-[350px]">
                 <div className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed font-serif">
                   {generatedLetter.content}
                 </div>
               </div>
               
               <div className="mt-6 flex space-x-4 w-full">
                 <button onClick={downloadPdf} className="flex-1 btn-primary flex justify-center items-center bg-amber-600 hover:bg-amber-500 shadow-amber-500/20">
                   <Download className="w-4 h-4 mr-2" /> Download PDF
                 </button>
               </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
