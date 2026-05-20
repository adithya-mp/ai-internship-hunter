import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  UploadCloud, FileText, Trash2, Download, Plus, X, 
  Briefcase, Award, TrendingUp, CheckCircle, Clock, User, 
  Sparkles, Check, Loader2, AlertCircle
} from 'lucide-react';
import { useJobStore } from '../store/jobStore';
import { useAuthStore } from '../store/authStore';
import { useDocumentStore } from '../store/documentStore';
import { apiClient } from '../api/client';

// Custom HSL demand colors for recommendations
const demandColors: Record<string, string> = {
  High: 'from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30 HSL(142,70%,45%)',
  Medium: 'from-violet-500/20 to-indigo-500/20 text-indigo-400 border-indigo-500/30 HSL(250,70%,60%)',
  Low: 'from-slate-500/20 to-slate-700/20 text-slate-400 border-slate-700/30 HSL(215,15%,50%)',
};

export default function Dashboard() {
  const { user, updateProfile } = useAuthStore();
  const { matchedJobs, fetchMatchedJobs } = useJobStore();
  const { documents, loadDocuments, addDocument, deleteDocument } = useDocumentStore();

  // Active Tab for Profile Details Form
  const [activeFormTab, setActiveFormTab] = useState<'personal' | 'experience' | 'education' | 'projects'>('personal');
  
  // Custom skills matrix and recommendations states
  const [userSkills, setUserSkills] = useState<{ id: string; name: string; proficiency: number }[]>([]);
  const [recommendedSkills, setRecommendedSkills] = useState<any[]>([]);
  const [skillsLoading, setSkillsLoading] = useState(false);
  const [newSkillName, setNewSkillName] = useState('');
  const [isAddingCustomSkill, setIsAddingCustomSkill] = useState(false);

  // Form profile states (derived from user model)
  const [fullName, setFullName] = useState('');
  const [bio, setBio] = useState('');
  const [location, setLocation] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [targetQueries, setTargetQueries] = useState('');
  const [experiences, setExperiences] = useState<any[]>([]);
  const [educations, setEducations] = useState<any[]>([]);
  const [projectsList, setProjectsList] = useState<any[]>([]);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileSuccessMsg, setProfileSuccessMsg] = useState('');

  // Drag & drop file upload states
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  
  // Parsed Resume autofill states
  const [parsedData, setParsedData] = useState<any | null>(null);
  const [showAutofillModal, setShowAutofillModal] = useState(false);

  // Stats
  const applicationsCount = 14; // Mock stats
  const pendingCount = 5;
  const interviewsCount = 2;

  // Load baseline profile data
  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setBio(user.bio || '');
      const profile = user.profile_data || {};
      setLocation(profile.location || '');
      setTargetRole(profile.target_role || '');
      setTargetQueries(profile.target_queries || '');
      setExperiences(profile.experience || []);
      setEducations(profile.education || []);
      setProjectsList(profile.projects || []);
    }
  }, [user]);

  // Load all initial content
  useEffect(() => {
    fetchMatchedJobs();
    loadDocuments();
    fetchUserSkills();
  }, [fetchMatchedJobs, loadDocuments]);

  // Fetch Recommended Skills whenever Target Role or Current Skills change
  useEffect(() => {
    if (user) {
      fetchSkillRecommendations();
    }
  }, [user, userSkills]);

  const fetchUserSkills = async () => {
    try {
      const response = await apiClient.get('/skills');
      setUserSkills(response.data);
    } catch (error) {
      console.error('Error fetching skills:', error);
    }
  };

  const fetchSkillRecommendations = async () => {
    setSkillsLoading(true);
    try {
      const response = await apiClient.get('/skills/recommendations');
      setRecommendedSkills(response.data.recommendations || []);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    } finally {
      setSkillsLoading(false);
    }
  };

  // Add a skill to database
  const handleAddSkill = async (skillName: string, proficiency: number = 75, category: string = 'General') => {
    if (!skillName.trim()) return;
    try {
      await apiClient.post('/skills', {
        name: skillName.trim(),
        proficiency,
        category
      });
      setNewSkillName('');
      setIsAddingCustomSkill(false);
      await fetchUserSkills();
    } catch (error) {
      console.error('Failed to add skill:', error);
    }
  };

  // Delete a skill
  const handleDeleteSkill = async (skillId: string) => {
    try {
      await apiClient.delete(`/skills/${skillId}`);
      await fetchUserSkills();
    } catch (error) {
      console.error('Failed to delete skill:', error);
    }
  };

  // Handle local File Upload and Remote Parsing
  const processResumeFile = async (file: File) => {
    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
      setUploadError('Only PDF and DOCX files are allowed.');
      return;
    }
    setUploadError('');
    setIsUploading(true);

    try {
      // 1. Save locally in browser IndexedDB
      await addDocument(file, 'resume', file.name.split('.')[0]);

      // 2. Post to backend for AI structured extraction
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/upload/resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data && response.data.parsed_data) {
        setParsedData(response.data.parsed_data);
        setShowAutofillModal(true);
      }
    } catch (err: any) {
      console.error('Upload & parse failure:', err);
      setUploadError(err.response?.data?.detail || 'Failed to upload or parse resume.');
    } finally {
      setIsUploading(false);
    }
  };

  // Drag handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processResumeFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processResumeFile(e.target.files[0]);
    }
  };

  // Accept Parsed resume autofill
  const handleAutofillConfirm = async () => {
    if (!parsedData) return;
    
    setIsSavingProfile(true);
    try {
      // 1. Update personal profile details
      const profileData = {
        ...user?.profile_data,
        experience: parsedData.experience || [],
        education: parsedData.education || [],
        projects: parsedData.projects || [],
      };
      
      await updateProfile({
        full_name: fullName || user?.full_name,
        profile_data: profileData
      });

      // 2. Insert all parsed skills to DB
      if (parsedData.skills && parsedData.skills.length > 0) {
        for (const skill of parsedData.skills) {
          const alreadyHas = userSkills.some(s => s.name.toLowerCase() === skill.toLowerCase());
          if (!alreadyHas) {
            try {
              await apiClient.post('/skills', {
                name: skill,
                proficiency: 75,
                category: 'Parsed'
              });
            } catch (err) {
              console.error(`Failed to seed parsed skill ${skill}:`, err);
            }
          }
        }
      }

      await fetchUserSkills();
      await fetchMatchedJobs();
      setShowAutofillModal(false);
      setParsedData(null);
      setProfileSuccessMsg('Profile details successfully auto-populated from resume!');
      setTimeout(() => setProfileSuccessMsg(''), 5000);
    } catch (err) {
      console.error('Error autofilling:', err);
    } finally {
      setIsSavingProfile(false);
    }
  };

  // Profile Save handler
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingProfile(true);
    setProfileSuccessMsg('');
    try {
      const updatedProfileData = {
        ...user?.profile_data,
        location,
        target_role: targetRole,
        target_queries: targetQueries,
        experience: experiences,
        education: educations,
        projects: projectsList
      };

      await updateProfile({
        full_name: fullName,
        bio,
        profile_data: updatedProfileData
      });

      setProfileSuccessMsg('Profile updated and job match embeddings recalculated!');
      await fetchMatchedJobs(); // Refresh matched jobs list
      setTimeout(() => setProfileSuccessMsg(''), 5000);
    } catch (error) {
      console.error('Failed to save profile:', error);
    } finally {
      setIsSavingProfile(false);
    }
  };

  // Helper experience/education/project mutators
  const addExperienceItem = () => {
    setExperiences([...experiences, { title: '', company: '', duration: '', bullets: [''] }]);
  };
  const updateExperienceItem = (index: number, key: string, value: any) => {
    const list = [...experiences];
    list[index][key] = value;
    setExperiences(list);
  };
  const removeExperienceItem = (index: number) => {
    setExperiences(experiences.filter((_, i) => i !== index));
  };

  const addEducationItem = () => {
    setEducations([...educations, { degree: '', institution: '', year: '' }]);
  };
  const updateEducationItem = (index: number, key: string, value: string) => {
    const list = [...educations];
    list[index][key] = value;
    setEducations(list);
  };
  const removeEducationItem = (index: number) => {
    setEducations(educations.filter((_, i) => i !== index));
  };

  const addProjectItem = () => {
    setProjectsList([...projectsList, { name: '', description: '' }]);
  };
  const updateProjectItem = (index: number, key: string, value: string) => {
    const list = [...projectsList];
    list[index][key] = value;
    setProjectsList(list);
  };
  const removeProjectItem = (index: number) => {
    setProjectsList(projectsList.filter((_, i) => i !== index));
  };

  // File Download Helpers
  const downloadLocalFile = (doc: any) => {
    if (!doc.fileData) return;
    const link = document.createElement('a');
    link.href = doc.fileData;
    link.download = doc.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary-400 via-indigo-300 to-purple-400">
            Control Center
          </h1>
          <p className="text-slate-400 mt-1">
            Hi, {user?.full_name?.split(' ')[0] || 'User'}! Upload, customize, and let AI build your application pipeline.
          </p>
        </div>
      </div>

      {/* Stats Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 border-l-4 border-primary-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-400">AI Job Matches</p>
              <p className="text-3xl font-bold text-white mt-1">{matchedJobs.length}</p>
            </div>
            <div className="p-3 rounded-xl bg-primary-500/10 text-primary-400">
              <Briefcase className="w-6 h-6" />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-6 border-l-4 border-emerald-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-400">Applications Sent</p>
              <p className="text-3xl font-bold text-white mt-1">{applicationsCount}</p>
            </div>
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400">
              <CheckCircle className="w-6 h-6" />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-6 border-l-4 border-amber-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-400">Pending Review</p>
              <p className="text-3xl font-bold text-white mt-1">{pendingCount}</p>
            </div>
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400">
              <Clock className="w-6 h-6" />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-400">Interviews</p>
              <p className="text-3xl font-bold text-white mt-1">{interviewsCount}</p>
            </div>
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400">
              <TrendingUp className="w-6 h-6" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Grid Layout (Upload Zone, Form and Recs) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left 2 Columns: Resume Zone, Profile Form & Documents */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Drag & Drop Zone */}
          <div className="glass-card p-6 relative overflow-hidden">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-primary-400" />
              Upload Resume (PDF/DOCX)
            </h2>
            
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all ${
                isDragActive 
                  ? 'border-primary-500 bg-primary-500/5' 
                  : 'border-slate-700 bg-slate-900/40 hover:border-slate-600'
              }`}
            >
              {isUploading ? (
                <div className="flex flex-col items-center py-4">
                  <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
                  <p className="text-slate-300 font-medium mt-3">Uploading & Parsing resume with Gemini AI...</p>
                  <p className="text-xs text-slate-500 mt-1">This will automatically extract your skills and history</p>
                </div>
              ) : (
                <>
                  <UploadCloud className="w-12 h-12 text-slate-400 mb-3" />
                  <p className="text-slate-200 font-medium text-center">
                    Drag and drop your resume here, or <label className="text-primary-400 hover:text-primary-300 cursor-pointer underline">browse files<input type="file" className="hidden" accept=".pdf,.docx" onChange={handleFileChange} /></label>
                  </p>
                  <p className="text-xs text-slate-500 mt-1.5">Supports PDF and DOCX (Max 10MB)</p>
                </>
              )}
            </div>

            {uploadError && (
              <div className="mt-3 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center gap-2 text-rose-300 text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>{uploadError}</span>
              </div>
            )}
          </div>

          {/* Profile Form Control Section */}
          <div className="glass-card p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <User className="w-5 h-5 text-primary-400" />
                Inline Profile Details Form
              </h2>
              {profileSuccessMsg && (
                <span className="text-emerald-400 text-sm font-semibold flex items-center gap-1.5">
                  <Check className="w-4 h-4 bg-emerald-500/20 rounded-full p-0.5" />
                  {profileSuccessMsg}
                </span>
              )}
            </div>

            {/* Collapsible Tabs for Profile Forms */}
            <div className="flex border-b border-slate-700/60 mb-6 overflow-x-auto whitespace-nowrap">
              <button
                onClick={() => setActiveFormTab('personal')}
                className={`px-4 py-2 font-semibold text-sm border-b-2 transition-all ${
                  activeFormTab === 'personal'
                    ? 'border-primary-500 text-primary-400 bg-primary-500/5'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                1. General Info
              </button>
              <button
                onClick={() => setActiveFormTab('experience')}
                className={`px-4 py-2 font-semibold text-sm border-b-2 transition-all ${
                  activeFormTab === 'experience'
                    ? 'border-primary-500 text-primary-400 bg-primary-500/5'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                2. Experience ({experiences.length})
              </button>
              <button
                onClick={() => setActiveFormTab('education')}
                className={`px-4 py-2 font-semibold text-sm border-b-2 transition-all ${
                  activeFormTab === 'education'
                    ? 'border-primary-500 text-primary-400 bg-primary-500/5'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                3. Education ({educations.length})
              </button>
              <button
                onClick={() => setActiveFormTab('projects')}
                className={`px-4 py-2 font-semibold text-sm border-b-2 transition-all ${
                  activeFormTab === 'projects'
                    ? 'border-primary-500 text-primary-400 bg-primary-500/5'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                4. Projects ({projectsList.length})
              </button>
            </div>

            <form onSubmit={handleSaveProfile} className="space-y-6">
              
              {/* Tab 1: Personal Info */}
              {activeFormTab === 'personal' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Full Name</label>
                      <input 
                        type="text" 
                        value={fullName} 
                        onChange={(e) => setFullName(e.target.value)} 
                        className="input-field" 
                        placeholder="John Doe" 
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Location</label>
                      <input 
                        type="text" 
                        value={location} 
                        onChange={(e) => setLocation(e.target.value)} 
                        className="input-field" 
                        placeholder="Mumbai, India" 
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Target Internship Role</label>
                      <input 
                        type="text" 
                        value={targetRole} 
                        onChange={(e) => setTargetRole(e.target.value)} 
                        className="input-field" 
                        placeholder="Frontend Engineer Intern" 
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Target Search Queries (comma-separated)</label>
                      <input 
                        type="text" 
                        value={targetQueries} 
                        onChange={(e) => setTargetQueries(e.target.value)} 
                        className="input-field" 
                        placeholder="React developer, Software engineer intern" 
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Bio / Career Pitch</label>
                    <textarea 
                      value={bio} 
                      onChange={(e) => setBio(e.target.value)} 
                      rows={3} 
                      className="input-field resize-none" 
                      placeholder="Passionate builder aiming to solve user scale challenges..." 
                    />
                  </div>
                </div>
              )}

              {/* Tab 2: Work Experience */}
              {activeFormTab === 'experience' && (
                <div className="space-y-6">
                  {experiences.map((exp, index) => (
                    <div key={index} className="p-4 bg-slate-900/50 border border-slate-700/60 rounded-xl space-y-4 relative">
                      <button 
                        type="button" 
                        onClick={() => removeExperienceItem(index)}
                        className="absolute right-4 top-4 text-slate-500 hover:text-rose-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <h4 className="text-sm font-bold text-slate-300">Position #{index + 1}</h4>
                      
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div className="sm:col-span-1">
                          <label className="block text-xs text-slate-400 mb-1">Role Title</label>
                          <input 
                            type="text" 
                            value={exp.title || ''} 
                            onChange={(e) => updateExperienceItem(index, 'title', e.target.value)}
                            className="input-field py-1 px-3 text-sm" 
                            placeholder="Software Intern" 
                          />
                        </div>
                        <div className="sm:col-span-1">
                          <label className="block text-xs text-slate-400 mb-1">Company</label>
                          <input 
                            type="text" 
                            value={exp.company || ''} 
                            onChange={(e) => updateExperienceItem(index, 'company', e.target.value)}
                            className="input-field py-1 px-3 text-sm" 
                            placeholder="Acme Corp" 
                          />
                        </div>
                        <div className="sm:col-span-1">
                          <label className="block text-xs text-slate-400 mb-1">Duration</label>
                          <input 
                            type="text" 
                            value={exp.duration || ''} 
                            onChange={(e) => updateExperienceItem(index, 'duration', e.target.value)}
                            className="input-field py-1 px-3 text-sm" 
                            placeholder="Jan 2024 - Apr 2024" 
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs text-slate-400 mb-1">Bullet Achievements (newline separated)</label>
                        <textarea 
                          rows={2}
                          value={Array.isArray(exp.bullets) ? exp.bullets.join('\n') : exp.bullets || ''}
                          onChange={(e) => updateExperienceItem(index, 'bullets', e.target.value.split('\n'))}
                          className="input-field py-1 px-3 text-sm resize-none" 
                          placeholder="Built responsive admin panel using React.&#10;Optimized queries increasing load speeds by 25%." 
                        />
                      </div>
                    </div>
                  ))}
                  
                  <button 
                    type="button" 
                    onClick={addExperienceItem}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    Add Work Experience
                  </button>
                </div>
              )}

              {/* Tab 3: Education */}
              {activeFormTab === 'education' && (
                <div className="space-y-6">
                  {educations.map((edu, index) => (
                    <div key={index} className="p-4 bg-slate-900/50 border border-slate-700/60 rounded-xl space-y-4 relative">
                      <button 
                        type="button" 
                        onClick={() => removeEducationItem(index)}
                        className="absolute right-4 top-4 text-slate-500 hover:text-rose-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <h4 className="text-sm font-bold text-slate-300">Degree #{index + 1}</h4>
                      
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-xs text-slate-400 mb-1">Degree Name</label>
                          <input 
                            type="text" 
                            value={edu.degree || ''} 
                            onChange={(e) => updateEducationItem(index, 'degree', e.target.value)}
                            className="input-field py-1 px-3 text-sm" 
                            placeholder="B.Tech Computer Science" 
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-slate-400 mb-1">Institution</label>
                          <input 
                            type="text" 
                            value={edu.institution || ''} 
                            onChange={(e) => updateEducationItem(index, 'institution', e.target.value)}
                            className="input-field py-1 px-3 text-sm" 
                            placeholder="IIT Bombay" 
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-slate-400 mb-1">Graduation Year / Range</label>
                          <input 
                            type="text" 
                            value={edu.year || ''} 
                            onChange={(e) => updateEducationItem(index, 'year', e.target.value)}
                            className="input-field py-1 px-3 text-sm" 
                            placeholder="2022 - 2026" 
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  <button 
                    type="button" 
                    onClick={addEducationItem}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    Add Education Record
                  </button>
                </div>
              )}

              {/* Tab 4: Projects */}
              {activeFormTab === 'projects' && (
                <div className="space-y-6">
                  {projectsList.map((proj, index) => (
                    <div key={index} className="p-4 bg-slate-900/50 border border-slate-700/60 rounded-xl space-y-4 relative">
                      <button 
                        type="button" 
                        onClick={() => removeProjectItem(index)}
                        className="absolute right-4 top-4 text-slate-500 hover:text-rose-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <h4 className="text-sm font-bold text-slate-300">Project #{index + 1}</h4>
                      
                      <div className="space-y-3">
                        <div>
                          <label className="block text-xs text-slate-400 mb-1">Project Name</label>
                          <input 
                            type="text" 
                            value={proj.name || ''} 
                            onChange={(e) => updateProjectItem(index, 'name', e.target.value)}
                            className="input-field py-1 px-3 text-sm" 
                            placeholder="E-commerce Analytics Tool" 
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-slate-400 mb-1">Brief Description</label>
                          <textarea 
                            rows={2}
                            value={proj.description || ''} 
                            onChange={(e) => updateProjectItem(index, 'description', e.target.value)}
                            className="input-field py-1 px-3 text-sm resize-none" 
                            placeholder="Built using React and Node.js. Serves 500+ active matching operations per hour." 
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  <button 
                    type="button" 
                    onClick={addProjectItem}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    Add Project Detail
                  </button>
                </div>
              )}

              {/* Form Action */}
              <div className="pt-4 border-t border-slate-700/40 flex justify-end">
                <button
                  type="submit"
                  disabled={isSavingProfile}
                  className="btn-primary flex items-center gap-1.5 disabled:opacity-50"
                >
                  {isSavingProfile ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving & Recalculating Matches...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Save & Regenerate Match Embeddings
                    </>
                  )}
                </button>
              </div>

            </form>
          </div>

          {/* Local Documents Table */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary-400" />
              Document Vault (Local IndexedDB Storage)
            </h2>
            
            {documents.length === 0 ? (
              <div className="py-8 text-center bg-slate-900/30 rounded-xl border border-slate-800 text-slate-500 text-sm">
                No local documents uploaded. Drop a file in the zone above.
              </div>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/20">
                <table className="w-full text-left border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 font-semibold uppercase text-xs">
                      <th className="p-4">Document Label</th>
                      <th className="p-4">Filename</th>
                      <th className="p-4">Date Uploaded</th>
                      <th className="p-4">Size</th>
                      <th className="p-4 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-slate-850/40 transition-colors">
                        <td className="p-4 font-bold text-slate-100">{doc.label}</td>
                        <td className="p-4 font-mono text-xs text-slate-400">{doc.name}</td>
                        <td className="p-4 text-slate-400">{doc.uploadDate}</td>
                        <td className="p-4 text-slate-400">{Math.round(doc.size / 1024)} KB</td>
                        <td className="p-4">
                          <div className="flex justify-center items-center gap-2">
                            <button
                              onClick={() => downloadLocalFile(doc)}
                              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all"
                              title="Download document File"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => deleteDocument(doc.id)}
                              className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-950 hover:text-rose-400 text-slate-400 transition-all"
                              title="Delete permanently"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>

        {/* Right 1 Column: Skill Progress Matrix & Gemini Recommendations */}
        <div className="space-y-8">
          
          {/* Skill matrix progress */}
          <div className="glass-card p-6 border-t-2 border-primary-500">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Award className="w-5 h-5 text-primary-400" />
                Active Skill Matrix
              </h2>
              <button 
                onClick={() => setIsAddingCustomSkill(prev => !prev)}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 py-1 px-2.5 rounded-lg font-semibold flex items-center gap-1 transition-all"
              >
                {isAddingCustomSkill ? 'Cancel' : 'Add custom +'}
              </button>
            </div>

            {/* Custom skill add zone */}
            <AnimatePresence>
              {isAddingCustomSkill && (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mb-6 p-4 rounded-lg bg-slate-900 border border-slate-800 space-y-3 overflow-hidden"
                >
                  <label className="text-xs text-slate-400 block">Skill Name</label>
                  <input
                    type="text"
                    value={newSkillName}
                    onChange={(e) => setNewSkillName(e.target.value)}
                    className="input-field py-1 px-3 text-sm"
                    placeholder="e.g. Next.js, Kubernetes"
                  />
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => handleAddSkill(newSkillName, 75, 'Manual')}
                      className="px-3 py-1.5 bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold rounded-md transition-all shadow-md shadow-primary-500/20"
                    >
                      Add Skill
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {userSkills.length === 0 ? (
              <p className="text-slate-500 text-sm py-4 text-center">No skills registered yet. Enter them or upload a resume!</p>
            ) : (
              <div className="space-y-4">
                {userSkills.map((sk) => (
                  <div key={sk.id} className="group relative">
                    <div className="flex justify-between text-sm mb-1 items-center">
                      <span className="text-slate-300 font-medium">{sk.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-primary-400 font-bold text-xs">{sk.proficiency}%</span>
                        <button
                          onClick={() => handleDeleteSkill(sk.id)}
                          className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-0.5 rounded transition-all"
                          title="Delete skill"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                    {/* Visual HSL dynamic styled matching/progress bars */}
                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-primary-600 to-indigo-400 rounded-full transition-all duration-500" 
                        style={{ width: `${sk.proficiency}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Gemini-Powered Skill Recommendations */}
          <div className="glass-card p-6 border-t-2 border-indigo-500">
            <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              Gemini Skill Recommendations
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              AI-derived learning opportunities based on your target role: <strong className="text-slate-300">{targetRole || 'Software Engineering'}</strong>
            </p>

            {skillsLoading ? (
              <div className="flex flex-col justify-center items-center py-12 gap-3">
                <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                <span className="text-xs text-slate-400">Consulting Gemini for skill matching...</span>
              </div>
            ) : recommendedSkills.length === 0 ? (
              <p className="text-slate-500 text-sm py-4 text-center">No recommendations. Please fill out a Target Role!</p>
            ) : (
              <div className="space-y-4">
                {recommendedSkills.map((rec, i) => {
                  const hasSkill = userSkills.some(s => s.name.toLowerCase() === rec.name.toLowerCase());
                  const demandClass = demandColors[rec.demand] || demandColors.Medium;
                  
                  return (
                    <motion.div
                      key={i}
                      whileHover={{ scale: 1.01 }}
                      className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col gap-3 group relative overflow-hidden"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex flex-col">
                          <span className="font-bold text-slate-200 text-sm">{rec.name}</span>
                          <span className="text-[10px] text-slate-500 font-semibold">{rec.category || 'General'}</span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] uppercase font-extrabold tracking-wider px-2 py-0.5 rounded-full border ${demandClass.split(' ').slice(0, -1).join(' ')}`}>
                            {rec.demand} Demand
                          </span>
                          
                          {hasSkill ? (
                            <span className="p-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" title="Already added">
                              <Check className="w-3.5 h-3.5" />
                            </span>
                          ) : (
                            <button
                              onClick={() => handleAddSkill(rec.name, 50, rec.category || 'Recommended')}
                              className="p-1 rounded-lg bg-slate-800 hover:bg-primary-600 text-slate-300 hover:text-white transition-all border border-slate-700 hover:border-transparent"
                              title="Add to skill list"
                            >
                              <Plus className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </div>

                      <p className="text-xs text-slate-400 leading-relaxed font-medium">
                        {rec.explanation}
                      </p>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </div>

        </div>

      </div>

      {/* Parsed Resume Autofill Confirmation Dialog Modal */}
      <AnimatePresence>
        {showAutofillModal && parsedData && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowAutofillModal(false)}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            />
            
            {/* Modal Box */}
            <motion.div 
              initial={{ scale: 0.95, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.95, y: 20, opacity: 0 }}
              className="glass-card w-full max-w-2xl max-h-[85vh] flex flex-col relative overflow-hidden z-10 border border-slate-700"
            >
              {/* Modal Header */}
              <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/60">
                <div className="flex items-center gap-2 text-primary-400">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-lg font-bold text-white">We successfully parsed your Resume!</h3>
                </div>
                <button 
                  onClick={() => setShowAutofillModal(false)} 
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Scrollable Content preview */}
              <div className="p-6 overflow-y-auto space-y-6 flex-1 text-sm leading-relaxed">
                <p className="text-slate-300 font-medium">
                  We found structured details in your file. Would you like to auto-populate your ApplyIQ profile with these details? This will update your matching score and recommend precise internships.
                </p>

                {/* Skills Detected */}
                {parsedData.skills && parsedData.skills.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Parsed Skills ({parsedData.skills.length})</h4>
                    <div className="flex flex-wrap gap-2">
                      {parsedData.skills.map((sk: string) => (
                        <span key={sk} className="px-2.5 py-1 bg-slate-800 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium">
                          {sk}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Experience Detected */}
                {parsedData.experience && parsedData.experience.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Parsed History</h4>
                    <div className="space-y-2.5">
                      {parsedData.experience.map((exp: any, i: number) => (
                        <div key={i} className="p-3 bg-slate-900/50 border border-slate-800/80 rounded-lg">
                          <p className="font-bold text-slate-200">{exp.title} <span className="text-slate-400 font-normal">at</span> {exp.company}</p>
                          <p className="text-xs text-slate-500 font-semibold">{exp.duration}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Education Detected */}
                {parsedData.education && parsedData.education.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Parsed Education</h4>
                    <div className="space-y-2">
                      {parsedData.education.map((edu: any, i: number) => (
                        <div key={i} className="p-3 bg-slate-900/50 border border-slate-800/80 rounded-lg">
                          <p className="font-bold text-slate-200">{edu.degree}</p>
                          <p className="text-xs text-slate-400">{edu.institution} • {edu.year}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Projects Detected */}
                {parsedData.projects && parsedData.projects.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Parsed Projects</h4>
                    <div className="space-y-2">
                      {parsedData.projects.map((proj: any, i: number) => (
                        <div key={i} className="p-3 bg-slate-900/50 border border-slate-800/80 rounded-lg">
                          <p className="font-bold text-slate-200">{proj.name}</p>
                          <p className="text-xs text-slate-400">{proj.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Modal Actions */}
              <div className="p-6 bg-slate-900/60 border-t border-slate-800 flex justify-end gap-3">
                <button
                  onClick={() => setShowAutofillModal(false)}
                  className="px-4 py-2 border border-slate-700 rounded-lg text-slate-300 font-semibold hover:bg-slate-800 transition-colors text-sm"
                >
                  No, Keep Current Profile
                </button>
                <button
                  onClick={handleAutofillConfirm}
                  disabled={isSavingProfile}
                  className="btn-primary flex items-center gap-1.5 text-sm"
                >
                  {isSavingProfile ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Importing Details...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4" />
                      Yes, Auto-populate Profile
                    </>
                  )}
                </button>
              </div>

            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}

