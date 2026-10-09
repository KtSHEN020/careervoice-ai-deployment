import type {
  AuthChangeEvent,
  Session,
} from '@supabase/supabase-js'

export type SessionEventAction =
  | 'ignore'
  | 'update'
  | 'reset'

export function classifySessionEvent(
  event: AuthChangeEvent,
  session: Session | null,
  currentUserId: string | null,
): SessionEventAction {
  if (event === 'SIGNED_OUT') {
    return 'reset'
  }

  if (
    event !== 'SIGNED_IN'
    && event !== 'TOKEN_REFRESHED'
  ) {
    return 'ignore'
  }

  // AuthPanel is responsible for authorizing new users.
  // A Supabase session alone does not grant CareerVoice access.
  if (currentUserId === null || session === null) {
    return 'ignore'
  }

  if (session.user.id !== currentUserId) {
    return 'reset'
  }

  return 'update'
}