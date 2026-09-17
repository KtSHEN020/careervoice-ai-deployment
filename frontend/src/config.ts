const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'

function normalizeBaseUrl(value: string): string {
  const normalizedValue = value.trim()

  if (!normalizedValue) {
    return DEFAULT_API_BASE_URL
  }

  return normalizedValue.replace(/\/+$/, '')
}

export const API_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL,
)