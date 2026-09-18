import type {
  CareerProfile,
  ProfileExtractor,
} from '../api/profile'

export interface ProfileDraft {
  careerText: string
  extractor: ProfileExtractor
}

export interface ExtractedProfile {
  profile: CareerProfile
  extractor: ProfileExtractor
}

export const DEFAULT_PROFILE_DRAFT: ProfileDraft = {
  careerText: '',
  extractor: 'rules',
}