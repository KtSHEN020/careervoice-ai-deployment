import { apiRequest } from './client'
import type {
  CareerProfile,
  OutputLanguage,
} from './profile'

export type JobSource = 'adzuna'

export type WorkType =
  | 'remote'
  | 'hybrid'
  | 'onsite'
  | 'unknown'

export type Seniority =
  | 'intern'
  | 'junior'
  | 'mid'
  | 'senior'
  | 'lead'
  | 'unknown'

export interface NormalizedJob {
  job_id: string
  title: string
  company: string
  location: string
  work_type: WorkType
  seniority: Seniority
  description: string
  required_skills: string[]
  preferred_skills: string[]
  responsibilities: string[]
  tags: string[]
  source: string
  source_url: string
  collected_at: string
}

export interface JobSearchRequest {
  profile: CareerProfile
  roles: string[]
  location: string | null
  max_results_per_role: number
  source: JobSource
  output_language: OutputLanguage
}

export interface JobSearchSettings {
  roles: string[]
  location: string | null
  max_results_per_role: number
  source: JobSource
}

export interface JobSearchResponse {
  settings: JobSearchSettings
  jobs: NormalizedJob[]
  output_language: OutputLanguage
}

export function searchJobs(
  accessToken: string,
  request: JobSearchRequest,
): Promise<JobSearchResponse> {
  return apiRequest<JobSearchResponse>(
    '/api/v1/jobs/search',
    {
      method: 'POST',
      accessToken,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    },
  )
}