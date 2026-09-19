import type { JobSource } from '../api/jobs'
import type { CareerProfile } from '../api/profile'

export const MAX_JOB_ROLES = 3
export const DEFAULT_RESULTS_PER_ROLE = 5
export const MAX_RESULTS_PER_ROLE = 10

export interface JobSearchDraft {
  roles: string[]
  location: string
  maxResultsPerRole: number
  source: JobSource
}

function uniqueNonEmptyValues(
  values: string[],
): string[] {
  const result: string[] = []
  const seen = new Set<string>()

  for (const value of values) {
    const cleaned = value.trim()

    if (!cleaned) {
      continue
    }

    const normalized =
      cleaned.toLocaleLowerCase()

    if (seen.has(normalized)) {
      continue
    }

    seen.add(normalized)
    result.push(cleaned)
  }

  return result
}

export function createJobSearchDraft(
  profile: CareerProfile,
): JobSearchDraft {
  const roles = uniqueNonEmptyValues(
    profile.target_roles,
  ).slice(0, MAX_JOB_ROLES)

  const location =
    profile.preferred_locations.find(
      (value) => value.trim(),
    )?.trim() ?? ''

  return {
    roles,
    location,
    maxResultsPerRole:
      DEFAULT_RESULTS_PER_ROLE,
    source: 'adzuna',
  }
}

export function normalizeSearchRoles(
  roles: string[],
): string[] {
  return uniqueNonEmptyValues(
    roles,
  ).slice(0, MAX_JOB_ROLES)
}