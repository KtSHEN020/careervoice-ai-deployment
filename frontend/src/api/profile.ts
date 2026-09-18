import { apiRequest } from './client'

export type ProfileExtractor = 'rules' | 'llm'
export type OutputLanguage = 'en' | 'zh-CN'

export interface CareerProfile {
  target_roles: string[]
  skills: string[]
  experience_level: string | null
  preferred_locations: string[]
  preferred_work_types: string[]
  liked_areas: string[]
  disliked_areas: string[]
  hard_constraints: string[]
  career_goals: string[]
  notes: string[]
}

export interface ProfileExtractionRequest {
  career_preference_text: string
  extractor: ProfileExtractor
  output_language: OutputLanguage
}

export interface ProfileExtractionResponse {
  profile: CareerProfile
  extractor: ProfileExtractor
  output_language: OutputLanguage
}

export function extractCareerProfile(
  accessToken: string,
  request: ProfileExtractionRequest,
): Promise<ProfileExtractionResponse> {
  return apiRequest<ProfileExtractionResponse>(
    '/api/v1/profile/extract',
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