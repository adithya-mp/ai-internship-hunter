import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

const MOCK_ACCOUNTS = [
  {
    name: 'Adithya M',
    email: 'adithya.m@example.com',
    avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=120',
    role: 'Full Stack Intern'
  },
  {
    name: 'Aarya Sharma',
    email: 'aarya.sharma@example.com',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=120',
    role: 'Frontend Developer'
  },
  {
    name: 'Demo Candidate',
    email: 'candidate.demo@example.com',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=120',
    role: 'Software Engineer Intern'
  }
];

export default function SignIn() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showOAuthModal, setShowOAuthModal] = useState(false);
  const [oauthProvider, setOauthProvider] = useState<'google' | 'linkedin' | null>(null);
  const [oauthStep, setOauthStep] = useState<'connecting' | 'select' | 'authenticating'>('connecting');
  const [selectedMockUser, setSelectedMockUser] = useState<typeof MOCK_ACCOUNTS[0] | null>(null);

  const { login, oauthLogin, isLoading, error } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch {
      // Error handled in store
    }
  };

  const handleOAuthClick = (provider: 'google' | 'linkedin') => {
    setOauthProvider(provider);
    setShowOAuthModal(true);
    setOauthStep('connecting');
    setSelectedMockUser(null);
    
    // Simulate connection lag
    setTimeout(() => {
      setOauthStep('select');
    }, 1200);
  };

  const handleSelectAccount = async (account: typeof MOCK_ACCOUNTS[0]) => {
    setSelectedMockUser(account);
    setOauthStep('authenticating');
    
    try {
      // Simulate OAuth token verification
      setTimeout(async () => {
        try {
          await oauthLogin(
            oauthProvider || 'google',
            account.email,
            account.name,
            account.avatar
          );
          setShowOAuthModal(false);
          navigate('/dashboard');
        } catch (err) {
          setOauthStep('select');
        }
      }, 1500);
    } catch (err) {
      setOauthStep('select');
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-[-10%] left-[-10%] w-[45%] h-[45%] bg-primary-900/30 blur-[130px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[45%] h-[45%] bg-indigo-900/30 blur-[130px] rounded-full pointer-events-none"></div>
      
      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 text-center">
        {/* App Logo */}
        <div className="inline-flex items-center justify-center space-x-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-primary-500/20">
            <span className="text-white font-extrabold text-2xl">A</span>
          </div>
          <span className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-indigo-400">
            ApplyIQ
          </span>
        </div>
        
        <h2 className="text-center text-4xl font-extrabold text-white tracking-tight">
          Welcome back
        </h2>
        <p className="mt-2 text-center text-sm text-slate-400">
          Sign in to access your AI internship automation dashboard
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="glass-card py-8 px-4 shadow sm:rounded-2xl sm:px-10">
          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 bg-red-900/30 border border-red-500/50 rounded-lg text-red-200 text-sm animate-shake">
                {error}
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-slate-300">Email address</label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field pl-10"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300">Password</label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-10"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input 
                  id="remember-me" 
                  type="checkbox" 
                  className="h-4 w-4 bg-slate-900 border-slate-700 rounded text-primary-500 focus:ring-primary-500" 
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-400 cursor-pointer">
                  Remember me
                </label>
              </div>
              <div className="text-sm">
                <a href="#" className="font-medium text-primary-400 hover:text-primary-300">
                  Forgot password?
                </a>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 focus:ring-offset-slate-900 transition-all disabled:opacity-50"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
              {!isLoading && <ArrowRight className="ml-2 w-4 h-4" />}
            </button>
          </form>

          {/* Divider */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-800" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-dark-card text-slate-400">Or continue with</span>
              </div>
            </div>

            {/* OAuth Buttons */}
            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => handleOAuthClick('google')}
                className="w-full inline-flex justify-center items-center py-2.5 px-4 border border-slate-700 rounded-lg shadow-sm bg-slate-800/40 text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
              >
                <svg className="w-5 h-5 text-red-400 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.136 4.114-3.4 0-6.159-2.759-6.159-6.159s2.759-6.159 6.159-6.159c1.5 0 2.863.545 3.924 1.442l3.05-3.05C18.995 1.954 15.82 1 12.24 1 6.033 1 12.24 6.033 1 12.24s5.033 11.24 11.24 11.24c5.897 0 10.74-4.257 11.24-10.122h-11.24z" />
                </svg>
                <span>Google</span>
              </button>

              <button
                type="button"
                onClick={() => handleOAuthClick('linkedin')}
                className="w-full inline-flex justify-center items-center py-2.5 px-4 border border-slate-700 rounded-lg shadow-sm bg-slate-800/40 text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
              >
                <svg className="w-5 h-5 text-blue-400 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
                <span>LinkedIn</span>
              </button>
            </div>
          </div>

          <div className="mt-8 text-center text-sm text-slate-400">
            Don't have an account?{' '}
            <Link to="/signup" className="font-medium text-primary-400 hover:text-primary-300 transition-colors">
              Create an account
            </Link>
          </div>
        </div>
      </div>

      {/* Minimal Footer */}
      <div className="mt-12 text-center text-xs text-slate-500 relative z-10 flex justify-center space-x-4">
        <a href="#" className="hover:text-slate-400">Privacy Policy</a>
        <span>&bull;</span>
        <a href="#" className="hover:text-slate-400">Terms of Service</a>
        <span>&bull;</span>
        <a href="#" className="hover:text-slate-400">Contact Support</a>
      </div>

      {/* Simulated OAuth Modal Overlay */}
      {showOAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="glass-card max-w-md w-full p-6 border-slate-700 shadow-2xl relative overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
                <h3 className="text-lg font-bold text-white">
                  OAuth Secure Sandbox
                </h3>
              </div>
              <button 
                onClick={() => setShowOAuthModal(false)}
                className="text-slate-400 hover:text-white transition-colors text-sm"
              >
                Cancel
              </button>
            </div>

            {/* Connecting State */}
            {oauthStep === 'connecting' && (
              <div className="py-8 flex flex-col items-center justify-center text-center space-y-4">
                <div className="relative w-16 h-16 flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-4 border-slate-800"></div>
                  <div className="absolute inset-0 rounded-full border-4 border-primary-500 border-t-transparent animate-spin"></div>
                  {oauthProvider === 'google' ? (
                    <svg className="w-6 h-6 text-red-400" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.136 4.114-3.4 0-6.159-2.759-6.159-6.159s2.759-6.159 6.159-6.159c1.5 0 2.863.545 3.924 1.442l3.05-3.05C18.995 1.954 15.82 1 12.24 1 6.033 1 12.24 6.033 1 12.24s5.033 11.24 11.24 11.24c5.897 0 10.74-4.257 11.24-10.122h-11.24z" />
                    </svg>
                  ) : (
                    <svg className="w-6 h-6 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                  )}
                </div>
                <div>
                  <h4 className="font-bold text-white">Connecting to {oauthProvider === 'google' ? 'Google' : 'LinkedIn'} API</h4>
                  <p className="text-sm text-slate-400 mt-1">Establishing handshakes with simulation server...</p>
                </div>
              </div>
            )}

            {/* Selection State */}
            {oauthStep === 'select' && (
              <div className="space-y-4">
                <div>
                  <h4 className="font-bold text-white text-base">Select an account</h4>
                  <p className="text-sm text-slate-400 mt-0.5">Choose a mock profile to sign in to <span className="text-primary-400 font-semibold">ApplyIQ</span></p>
                </div>

                <div className="space-y-2 mt-4 max-h-[250px] overflow-y-auto pr-1">
                  {MOCK_ACCOUNTS.map((account) => (
                    <button
                      key={account.email}
                      onClick={() => handleSelectAccount(account)}
                      className="w-full flex items-center p-3 rounded-xl border border-slate-800 bg-slate-900/30 hover:bg-slate-800 hover:border-slate-700 text-left transition-all"
                    >
                      <img 
                        src={account.avatar} 
                        alt={account.name} 
                        className="w-10 h-10 rounded-full border border-slate-700 object-cover" 
                      />
                      <div className="ml-3 flex-1 min-w-0">
                        <p className="font-bold text-slate-200 text-sm truncate">{account.name}</p>
                        <p className="text-xs text-slate-400 truncate">{account.email}</p>
                      </div>
                      <div className="ml-2 text-right">
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                          {account.role}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>

                <p className="text-[11px] text-slate-500 mt-4 leading-relaxed">
                  ApplyIQ Sandbox uses mock user records to skip configuration of active API client secrets. Personal details will map to this chosen profile.
                </p>
              </div>
            )}

            {/* Authenticating State */}
            {oauthStep === 'authenticating' && selectedMockUser && (
              <div className="py-8 flex flex-col items-center justify-center text-center space-y-4">
                <img 
                  src={selectedMockUser.avatar} 
                  alt={selectedMockUser.name} 
                  className="w-16 h-16 rounded-full border-2 border-primary-500 object-cover animate-pulse" 
                />
                <div className="relative">
                  <div className="animate-bounce h-2 w-2 bg-primary-500 rounded-full inline-block mx-0.5"></div>
                  <div className="animate-bounce h-2 w-2 bg-primary-500 rounded-full inline-block mx-0.5 [animation-delay:0.2s]"></div>
                  <div className="animate-bounce h-2 w-2 bg-primary-500 rounded-full inline-block mx-0.5 [animation-delay:0.4s]"></div>
                </div>
                <div>
                  <h4 className="font-bold text-white">Authenticating as {selectedMockUser.name}</h4>
                  <p className="text-sm text-slate-400 mt-1">Generating JWT session tokens and syncing profile stores...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
