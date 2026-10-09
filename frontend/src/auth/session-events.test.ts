import type { Session } from '@supabase/supabase-js'

import {
  describe,
  expect,
  it,
} from 'vitest'

import { classifySessionEvent } from './session-events'

function sessionForUser(
  userId: string,
): Session {
  return {
    access_token: 'test-token',
    user: {
      id: userId,
    },
  } as Session
}

describe('Supabase session event classification', () => {
  it('updates the current user after token refresh', () => {
    expect(
      classifySessionEvent(
        'TOKEN_REFRESHED',
        sessionForUser('user-1'),
        'user-1',
      ),
    ).toBe('update')
  })

  it('updates an existing session after same-user sign-in', () => {
    expect(
      classifySessionEvent(
        'SIGNED_IN',
        sessionForUser('user-1'),
        'user-1',
      ),
    ).toBe('update')
  })

  it('resets the application after sign-out', () => {
    expect(
      classifySessionEvent(
        'SIGNED_OUT',
        null,
        'user-1',
      ),
    ).toBe('reset')
  })

  it('resets the application when the identity changes', () => {
    expect(
      classifySessionEvent(
        'SIGNED_IN',
        sessionForUser('user-2'),
        'user-1',
      ),
    ).toBe('reset')
  })

  it('rejects a refreshed session belonging to another user', () => {
    expect(
      classifySessionEvent(
        'TOKEN_REFRESHED',
        sessionForUser('user-2'),
        'user-1',
      ),
    ).toBe('reset')
  })

  it('does not bypass CareerVoice authorization', () => {
    expect(
      classifySessionEvent(
        'SIGNED_IN',
        sessionForUser('user-1'),
        null,
      ),
    ).toBe('ignore')
  })

  it('ignores initial session events', () => {
    expect(
      classifySessionEvent(
        'INITIAL_SESSION',
        sessionForUser('user-1'),
        'user-1',
      ),
    ).toBe('ignore')
  })
})