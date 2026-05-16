export type ExtensionSettings = {
  backendUrl: string;
  openaiApiKey: string;
  openaiModel: string;
  embeddingModel: string;
};

export type JobInput = {
  source: string;
  job_title: string;
  company_name: string;
  location?: string | null;
  job_url?: string | null;
  job_description: string;
  employment_type?: string | null;
  seniority?: string | null;
  posted_date?: string | null;
  page_contacts?: ContactInfo[];
};

export type ParsedResumeProfile = {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  education: Array<{ school: string; degree?: string | null; graduation_date?: string | null }>;
  skills: Record<string, string[]>;
  experience: Array<{ company: string; title: string; bullets: string[] }>;
  projects: Array<{ name: string; description?: string | null; technologies: string[] }>;
  parser_notes: string[];
};

export type ResumeUploadResponse = {
  resume_id: string;
  name?: string | null;
  parsed_profile: ParsedResumeProfile;
};

export type ScoreBreakdown = {
  skills: number;
  experience: number;
  seniority: number;
  domain: number;
  education: number;
};

export type FitScore = {
  overall: number;
  recommendation: string;
  breakdown: ScoreBreakdown;
  matching_skills: string[];
  missing_skills: string[];
  strengths: string[];
  risks: string[];
};

export type SourceLink = {
  title: string;
  url: string;
};

export type CompanyInfo = {
  name: string;
  summary?: string | null;
  industry?: string | null;
  website?: string | null;
  careers_url?: string | null;
  linkedin_url?: string | null;
  public_emails: string[];
  email_pattern?: string | null;
  email_domain?: string | null;
  email_pattern_confidence: number;
  email_pattern_reason?: string | null;
  h1b_data_url?: string | null;
  h1b_summary?: string | null;
  recruiter_search_urls: SourceLink[];
  notes: string[];
  sources: SourceLink[];
};

export type ContactInfo = {
  id?: string | null;
  name: string;
  title?: string | null;
  profile_url?: string | null;
  email?: string | null;
  email_type?: string | null;
  confidence: number;
  confidence_reason?: string | null;
  sources: SourceLink[];
};

export type AnalyzeJobResponse = {
  analysis_id: string;
  job_id: string;
  fit_score: FitScore;
  company: CompanyInfo;
  contacts: ContactInfo[];
};

export type OutreachResponse = {
  outreach_id?: string | null;
  subject?: string | null;
  body: string;
};
