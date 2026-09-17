import {
  createClient,
  type SupabaseClient,
} from '@supabase/supabase-js'

import { getSupabasePublicConfig } from '../config'

let supabaseClient: SupabaseClient | null = null

export function getSupabaseClient(): SupabaseClient {
  if (supabaseClient !== null) {
    return supabaseClient
  }

  const config = getSupabasePublicConfig()

  supabaseClient = createClient(
    config.url,
    config.publishableKey,
    {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: false,
      },
    },
  )

  return supabaseClient
}