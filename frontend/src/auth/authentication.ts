import type { Session } from '@supabase/supabase-js'

import { getSupabaseClient } from './supabase'

function normalizeEmail(email: string): string {
  const normalizedEmail = email.trim().toLowerCase()

  if (!normalizedEmail) {
    throw new Error('Email is required.')
  }

  return normalizedEmail
}

function normalizeOtp(code: string): string {
  const normalizedCode = code.trim()

  if (!normalizedCode) {
    throw new Error('Verification code is required.')
  }

  return normalizedCode
}

export async function requestEmailOtp(email: string): Promise<void> {
  const supabase = getSupabaseClient()
  const normalizedEmail = normalizeEmail(email)

  const { error } = await supabase.auth.signInWithOtp({
    email: normalizedEmail,
    options: {
      shouldCreateUser: false,
    },
  })

  if (error) {
    throw error
  }
}

export async function verifyEmailOtp(
  email: string,
  code: string,
): Promise<Session> {
  const supabase = getSupabaseClient()

  const normalizedEmail = normalizeEmail(email)
  const normalizedCode = normalizeOtp(code)

  const { data, error } = await supabase.auth.verifyOtp({
    email: normalizedEmail,
    token: normalizedCode,
    type: 'email',
  })

  if (error) {
    throw error
  }

  if (data.session === null) {
    throw new Error(
      'Authentication succeeded without creating a session.',
    )
  }

  return data.session
}

export async function signOutCurrentSession(): Promise<void> {
  const supabase = getSupabaseClient()

  const { error } = await supabase.auth.signOut({
    scope: 'local',
  })

  if (error) {
    throw error
  }
}