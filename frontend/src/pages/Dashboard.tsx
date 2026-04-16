import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, TrendingUp, CheckCircle, Clock } from 'lucide-react';
import { useJobStore } from '../store/jobStore';
import { useAuthStore } from '../store/authStore';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const StatsCard = ({ title, value, icon: Icon, color, trend }: any) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="glass-card p-6"
  >
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-slate-400">{title}</p>
        <p className="text-3xl font-bold text-white mt-1">{value}</p>
      </div>
      <div className={`p-3 rounded-xl bg-${color}-500/20`}>
        <Icon className={`w-6 h-6 text-${color}-400`} />
      </div>
    </div>
    <div className="mt-4 flex items-center text-sm">
      <TrendingUp className="w-4 h-4 text-emerald-400 mr-1" />
      <span className="text-emerald-400 font-medium">{trend}</span>
      <span className="text-slate-500 ml-2">vs last week</span>
    </div>
  </motion.div>
);

export default function Dashboard() {
  const { user } = useAuthStore();
  const { matchedJobs, fetchMatchedJobs, isLoading } = useJobStore();

  useEffect(() => {
    fetchMatchedJobs();
  }, [fetchMatchedJobs]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 mt-1">Welcome back, {user?.full_name?.split(' ')[0]}! Here's your career pipeline.</p>
        </div>
        <button className="btn-primary">
          Upload Resume Update
        </button>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard title="AI Matched Jobs" value={matchedJobs.length} icon={Briefcase} color="primary" trend="+12%" />
        <StatsCard title="Applications Sent" value="14" icon={CheckCircle} color="emerald" trend="+3" />
        <StatsCard title="Pending Review" value="5" icon={Clock} color="amber" trend="-2" />
        <StatsCard title="Interviews" value="2" icon={TrendingUp} color="purple" trend="New!" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Top AI Matches For You</h2>
              <button className="text-primary-400 text-sm hover:underline">View all</button>
            </div>
            
            {isLoading ? (
               <div className="animate-pulse space-y-4">
                 {[1,2,3].map(i => (
                   <div key={i} className="h-24 bg-slate-800/50 rounded-xl"></div>
                 ))}
               </div>
             ) : (
              <div className="space-y-4">
                {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                {matchedJobs.slice(0, 3).map((match: any) => (
                  <div key={match.job.id} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-primary-500/50 transition-colors cursor-pointer flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-slate-200">{match.job.title}</h3>
                      <p className="text-sm text-slate-400">{match.job.company} • {match.job.location || 'Remote'}</p>
                    </div>
                    <div className="text-right">
                      <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {match.match_score}% Match
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Space */}
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-white mb-4">Skill Progress</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-300">React & Next.js</span>
                  <span className="text-primary-400">85%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary-600 to-indigo-400 w-[85%] rounded-full"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-300">FastAPI & Python</span>
                  <span className="text-primary-400">70%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary-600 to-indigo-400 w-[70%] rounded-full"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
