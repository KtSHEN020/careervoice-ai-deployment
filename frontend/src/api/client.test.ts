import type { Session } from '@supabase/supabase-js'

import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest'

import { getCurrentSession } from '../auth/session'
import { ApiError, apiRequest } from './client'

vi.mock('../auth/session', () => ({
  getCurrentSession: vi.fn(),
}))

function sessionWithToken(accessToken: string): Session {
  return {
    access_token: accessToken,
  } as Session
}

function stubSuccessfulFetch() {
  const fetchMock = vi.fn<typeof fetch>().mockImplementation(
    async () =>
      new Response(
        JSON.stringify({ ok: true }),
        {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
      ),
  )

  vi.stubGlobal('fetch', fetchMock)

  return fetchMock
}

beforeEach(() => {
  vi.clearAllMocks()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('apiRequest authentication', () => {
  it('uses the current token instead of a stale token', async () => {
    const fetchMock = stubSuccessfulFetch()

    vi.mocked(getCurrentSession).mockResolvedValue(
      sessionWithToken('refreshed-token'),
    )

    await apiRequest('/api/v1/me', {
      accessToken: 'expired-token',
    })

    expect(fetchMock).toHaveBeenCalledOnce()

    const headers = new Headers(
      fetchMock.mock.calls[0]?.[1]?.headers,
    )

    expect(headers.get('Authorization')).toBe(
      'Bearer refreshed-token',
    )
  })

  it('retrieves the current token for every request', async () => {
    const fetchMock = stubSuccessfulFetch()

    vi.mocked(getCurrentSession)
      .mockResolvedValueOnce(
        sessionWithToken('first-token'),
      )
      .mockResolvedValueOnce(
        sessionWithToken('second-token'),
      )

    await apiRequest('/api/v1/usage', {
      accessToken: 'original-token',
    })

    await apiRequest('/api/v1/usage', {
      accessToken: 'original-token',
    })

    expect(fetchMock).toHaveBeenCalledTimes(2)

    const firstHeaders = new Headers(
      fetchMock.mock.calls[0]?.[1]?.headers,
    )

    const secondHeaders = new Headers(
      fetchMock.mock.calls[1]?.[1]?.headers,
    )

    expect(firstHeaders.get('Authorization')).toBe(
      'Bearer first-token',
    )

    expect(secondHeaders.get('Authorization')).toBe(
      'Bearer second-token',
    )
  })

  it('rejects authenticated requests without a session', async () => {
    const fetchMock = stubSuccessfulFetch()

    vi.mocked(getCurrentSession).mockResolvedValue(null)

    await expect(
      apiRequest('/api/v1/usage', {
        accessToken: 'expired-token',
      }),
    ).rejects.toMatchObject({
      name: 'ApiError',
      status: 401,
    } satisfies Partial<ApiError>)

    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('allows unauthenticated requests', async () => {
    const fetchMock = stubSuccessfulFetch()

    await apiRequest('/health')

    expect(getCurrentSession).not.toHaveBeenCalled()
    expect(fetchMock).toHaveBeenCalledOnce()

    const headers = new Headers(
      fetchMock.mock.calls[0]?.[1]?.headers,
    )

    expect(headers.has('Authorization')).toBe(false)
  })

  it('preserves multipart uploads without forcing Content-Type', async () => {
    const fetchMock = stubSuccessfulFetch()

    vi.mocked(getCurrentSession).mockResolvedValue(
      sessionWithToken('current-token'),
    )

    const formData = new FormData()
    formData.append('output_language', 'en')

    await apiRequest('/api/v1/profile/transcribe-voice', {
      method: 'POST',
      accessToken: 'old-token',
      body: formData,
    })

    const requestOptions = fetchMock.mock.calls[0]?.[1]
    const headers = new Headers(requestOptions?.headers)

    expect(requestOptions?.body).toBe(formData)
    expect(headers.has('Content-Type')).toBe(false)
    expect(headers.get('Authorization')).toBe(
      'Bearer current-token',
    )
  })
})