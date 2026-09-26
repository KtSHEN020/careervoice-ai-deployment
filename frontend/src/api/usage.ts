import { apiRequest } from './client'

interface DailyUsageBase {
  usage_date: string
  daily_ai_unit_limit: number
  ai_units_used: number
  ai_profile_extractions: number
  voice_transcriptions: number
  document_recognitions: number
  ai_ranking_runs: number
  job_searches: number
}

export type DailyUsage =
  | (DailyUsageBase & {
      ai_quota_exempt: true
      remaining_ai_units: null
    })
  | (DailyUsageBase & {
      ai_quota_exempt: false
      remaining_ai_units: number
    })

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