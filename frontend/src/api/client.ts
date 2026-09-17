import { API_BASE_URL } from '../config'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export interface ApiRequestOptions extends RequestInit {
  accessToken?: string
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  const {
    accessToken,
    headers,
    ...requestInit
  } = options

  const requestHeaders = new Headers(headers)

  requestHeaders.set('Accept', 'application/json')

  if (accessToken) {
    requestHeaders.set(
      'Authorization',
      `Bearer ${accessToken}`,
    )
  }

  const response = await fetch(
    `${API_BASE_URL}${normalizedPath}`,
    {
      ...requestInit,
      headers: requestHeaders,
    },
  )

  if (!response.ok) {
    throw new ApiError(
      `API request failed with status ${response.status}.`,
      response.status,
    )
  }

  return (await response.json()) as T
}