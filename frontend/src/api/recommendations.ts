import { apiRequest } from './client'
import type {
  NormalizedJob,
} from './jobs'
import type {
  CareerProfile,
  OutputLanguage,
} from './profile'

export type RecommendationScorer =
  | 'rules'
  | 'llm'

export interface RecommendationRequest {
  profile: CareerProfile
  jobs: NormalizedJob[]
  scorer: RecommendationScorer
  max_results: number
  exclude_rejected: boolean
  output_language: OutputLanguage
}

export interface RecommendationSettings {
  scorer: RecommendationScorer
  max_results: number
  exclude_rejected: boolean
}

export interface RecommendationItem {
  job_id: string
  title: string
  company: string

  match_score: number

  recommendation_level: string

  reasons: string[]
  missing_skills: string[]
  penalties: string[]
  uncertainties: string[]

  is_rejected_by_constraints: boolean

  scoring_method: RecommendationScorer

  score_breakdown: Record<
    string,
    unknown
  >

  matched_details: Record<
    string,
    unknown
  >

  [key: string]: unknown
}

export interface RecommendationResponse {
  settings: RecommendationSettings

  recommendations: RecommendationItem[]

  total_jobs_scored: number

  total_jobs_scored_with_llm:
    | number
    | null

  llm_candidate_limit:
    | number
    | null

  total_recommendations_returned: number

  scoring_method: RecommendationScorer

  output_language: OutputLanguage
}

export function generateRecommendations(
  accessToken: string,
  request: RecommendationRequest,
): Promise<RecommendationResponse> {
  return apiRequest<RecommendationResponse>(
    '/api/v1/recommendations',
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