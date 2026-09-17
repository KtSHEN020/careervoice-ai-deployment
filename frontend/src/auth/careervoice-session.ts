import type { Session } from '@supabase/supabase-js'

import {
  getCurrentUser,
  type CurrentUser,
} from '../api/me'

export interface CareerVoiceSession {
  supabaseSession: Session
  user: CurrentUser
}

export async function resolveCareerVoiceSession(
  session: Session,
): Promise<CareerVoiceSession> {
  const user = await getCurrentUser(
    session.access_token,
  )

  return {
    supabaseSession: session,
    user,
  }
}