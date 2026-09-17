import type { Session } from '@supabase/supabase-js'

import { getSupabaseClient } from './supabase'

export async function getCurrentSession(): Promise<Session | null> {
  const supabase = getSupabaseClient()

  const { data, error } = await supabase.auth.getSession()

  if (error) {
    throw error
  }

  return data.session
}