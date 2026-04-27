import { useEffect, useState } from 'react';
import { Layers, Target, BookOpen, AlertCircle, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../api/client';

interface Skill {
  name: string;
  count: number;
}

export default function Skills() {
  const [userSkills, setUserSkills] = useState<string[]>([]);
  const [skillGap, setSkillGap] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchSkillsData();
  }, []);

  const fetchSkillsData = async () => {
    setIsLoading(true);
    try {
      // Mocking the data structure based on typical internship requirements
      // In a real scenario, this would come from a backend analyzer service
      const skillsRes = await apiClient.get('/skills');
      setUserSkills(skillsRes.data.map((s: any) => s.name));
      
      // Simulated gap analysis (normally would be calculated based on saved jobs)
      setSkillGap(['Docker', 'Redis', 'AWS', 'System Design']);
    } catch (err) {
      console.error('Failed to fetch skills:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Skill Analysis</h1>
        <p className="text-slate-400 mt-1">Real-time mapping of your capabilities against market requirements</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Current Skills */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6 border-t-2 border-primary-500">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <CheckCircle2 className="w-5 h-5 mr-3 text-emerald-400" />
              Your Skill Matrix
            </h2>
            
            {isLoading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-primary-500"></div>
              </div>
            ) : (
              <div className="flex flex-wrap gap-3">
                {userSkills.length > 0 ? userSkills.map(skill => (
                  <div key={skill} className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-slate-200 font-medium hover:border-primary-500/50 transition-colors">
                    {skill}
                  </div>
                )) : (
                  <p className="text-slate-500 p-4">No skills detected. Upload a resume to populate your matrix.</p>
                )}
              </div>
            )}
          </div>

          <div className="glass-card p-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <BookOpen className="w-5 h-5 mr-3 text-primary-400" />
              Recommended Learning Path
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {['Advanced React Patterns', 'Microservices Architecture', 'Database Optimization'].map(topic => (
                <div key={topic} className="p-4 bg-slate-900 border border-slate-700/50 rounded-xl flex items-center space-x-4">
                  <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
                    <Layers className="w-5 h-5 text-primary-400" />
                  </div>
                  <span className="text-slate-200 font-medium">{topic}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Skill Gaps */}
        <div className="space-y-6">
          <div className="glass-card p-6 border-t-2 border-rose-500">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Target className="w-5 h-5 mr-3 text-rose-400" />
              High Priority Gaps
            </h2>
            <p className="text-sm text-slate-400 mb-6">These skills are frequently appearing in your matched jobs but are missing from your profile.</p>
            
            <div className="space-y-4">
              {skillGap.map(skill => (
                <div key={skill} className="flex items-center justify-between p-3 bg-rose-500/5 border border-rose-500/20 rounded-lg">
                  <span className="text-rose-200 font-medium">{skill}</span>
                  <AlertCircle className="w-4 h-4 text-rose-400" />
                </div>
              ))}
            </div>
            
            <button className="w-full mt-6 py-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 rounded-xl text-sm font-bold transition-all border border-rose-500/30">
              Generate Upskilling Plan
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
