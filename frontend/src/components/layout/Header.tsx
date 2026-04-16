import { Bell, Search, User as UserIcon } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export default function Header() {
  const user = useAuthStore((state) => state.user);

  return (
    <header className="h-20 bg-dark-bg/80 backdrop-blur-lg border-b border-dark-border px-8 flex items-center justify-between sticky top-0 z-10">
      <div className="flex-1 flex max-w-2xl">
        <div className="relative w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search jobs, resumes, skills..."
            className="w-full bg-slate-800/50 border border-slate-700/50 rounded-full pl-12 pr-4 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:bg-slate-800 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center space-x-6 ml-8">
        <button className="relative p-2 text-slate-400 hover:text-slate-200 transition-colors">
          <Bell className="w-6 h-6" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary-500 rounded-full border border-dark-bg"></span>
        </button>

        <div className="flex items-center space-x-3 pl-6 border-l border-dark-border">
          <div className="text-right hidden md:block">
            <p className="text-sm font-semibold text-slate-200">{user?.full_name}</p>
            <p className="text-xs text-primary-400">Pro Member</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center border-2 border-primary-500/20">
            <UserIcon className="w-5 h-5 text-slate-300" />
          </div>
        </div>
      </div>
    </header>
  );
}
