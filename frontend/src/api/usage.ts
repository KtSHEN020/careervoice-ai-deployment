import { apiRequest } from './client'

export interface DailyUsage {
  usage_date: string
  daily_ai_unit_limit: number
  ai_units_used: number
  remaining_ai_units: number
  ai_profile_extractions: number
  voice_transcriptions: number
  document_recognitions: number
  ai_ranking_runs: number
  job_searches: number
}

export function getDailyUsage(
  accessToken: string,
): Promise<DailyUsage> {
  return apiRequest<DailyUsage>(
    '/api/v1/usage',
    {
      accessToken,
    },
  )
}