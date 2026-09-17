import { apiRequest } from './client'

export interface CurrentUser {
  id: string
  email: string
  enabled: boolean
}

export function getCurrentUser(
  accessToken: string,
): Promise<CurrentUser> {
  return apiRequest<CurrentUser>(
    '/api/v1/me',
    {
      accessToken,
    },
  )
}