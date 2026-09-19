import type {
  RecommendationScorer,
} from '../api/recommendations'

export const DEFAULT_RECOMMENDATION_COUNT = 5
export const MAX_RECOMMENDATIONS = 10

export interface RecommendationDraft {
  scorer: RecommendationScorer
  maxResults: number
  excludeRejected: boolean
}

export function createRecommendationDraft(
  availableJobs: number,
): RecommendationDraft {
  return {
    scorer: 'rules',
    maxResults: Math.min(
      DEFAULT_RECOMMENDATION_COUNT,
      availableJobs,
      MAX_RECOMMENDATIONS,
    ),
    excludeRejected: false,
  }
}