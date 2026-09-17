const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'

function normalizeBaseUrl(value: string): string {
  const normalizedValue = value.trim()

  if (!normalizedValue) {
    return DEFAULT_API_BASE_URL
  }

  return normalizedValue.replace(/\/+$/, '')
}

function requirePublicEnvironmentValue(
  name: string,
  value: string | undefined,
): string {
  const normalizedValue = value?.trim()

  if (!normalizedValue) {
    throw new Error(`${name} is not configured.`)
  }

  return normalizedValue
}

export const API_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL,
)

export interface SupabasePublicConfig {
  url: string
  publishableKey: string
}

export function getSupabasePublicConfig(): SupabasePublicConfig {
  return {
    url: requirePublicEnvironmentValue(
      'VITE_SUPABASE_URL',
      import.meta.env.VITE_SUPABASE_URL,
    ),
    publishableKey: requirePublicEnvironmentValue(
      'VITE_SUPABASE_PUBLISHABLE_KEY',
      import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY,
    ),
  }
}