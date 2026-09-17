import { apiRequest } from './client'

export interface HealthResponse {
  status: string
  service: string
}

export function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/health')
}