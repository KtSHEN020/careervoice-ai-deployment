import {
  useEffect,
  useState,
} from 'react'

import { ApiError } from '../api/client'
import {
  getDailyUsage,
  type DailyUsage,
} from '../api/usage'
import type { CareerVoiceSession } from '../auth/careervoice-session'

interface UsageSummaryProps {
  session: CareerVoiceSession
}

type UsageState =
  | 'loading'
  | 'ready'
  | 'error'

function usageErrorMessage(
  error: unknown,
): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return 'Your session has expired. Please sign in again.'
    }

    if (error.status === 403) {
      return 'Your account does not currently have access to usage information.'
    }

    if (error.status === 503) {
      return 'Usage information is temporarily unavailable.'
    }
  }

  return 'Usage information could not be loaded.'
}

export function UsageSummary({
  session,
}: UsageSummaryProps) {
  const [state, setState] =
    useState<UsageState>('loading')

  const [usage, setUsage] =
    useState<DailyUsage | null>(null)

  const [errorMessage, setErrorMessage] =
    useState('')

  useEffect(() => {
    let active = true

    async function loadUsage() {
      setState('loading')
      setErrorMessage('')

      try {
        const result = await getDailyUsage(
          session.supabaseSession.access_token,
        )

        if (!active) {
          return
        }

        setUsage(result)
        setState('ready')
      } catch (error) {
        if (!active) {
          return
        }

        setUsage(null)
        setErrorMessage(
          usageErrorMessage(error),
        )
        setState('error')
      }
    }

    void loadUsage()

    return () => {
      active = false
    }
  }, [session])

  if (state === 'loading') {
    return (
      <section className="usage-card">
        <p className="usage-status">
          Loading today's usage…
        </p>
      </section>
    )
  }

  if (
    state === 'error'
    || usage === null
  ) {
    return (
      <section className="usage-card">
        <p className="usage-message-error">
          {errorMessage}
        </p>
      </section>
    )
  }

  return (
    <section className="usage-card">
      <div className="usage-heading">
        <div>
          <p className="usage-kicker">
            Today's AI usage
          </p>

          <h2>
            {usage.remaining_ai_units}{' '}
            units remaining
          </h2>
        </div>

        <p className="usage-total">
          {usage.ai_units_used}
          {' / '}
          {usage.daily_ai_unit_limit}
          {' used'}
        </p>
      </div>

      <div className="usage-details">
        <p>
          <strong>
            {usage.ai_profile_extractions}
          </strong>
          {' AI profile extractions'}
        </p>

        <p>
          <strong>
            {usage.voice_transcriptions}
          </strong>
          {' voice transcriptions'}
        </p>

        <p>
          <strong>
            {usage.document_recognitions}
          </strong>
          {' document recognitions'}
        </p>

        <p>
          <strong>
            {usage.ai_ranking_runs}
          </strong>
          {' AI ranking runs'}
        </p>

        <p>
          <strong>
            {usage.job_searches}
          </strong>
          {' job searches'}
        </p>
      </div>
    </section>
  )
}