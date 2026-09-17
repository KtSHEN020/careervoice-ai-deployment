import { API_BASE_URL } from '../config'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  const response = await fetch(`${API_BASE_URL}${normalizedPath}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...init?.headers,
    },
  })

  if (!response.ok) {
    throw new ApiError(
      `API request failed with status ${response.status}.`,
      response.status,
    )
  }

  return (await response.json()) as T
}