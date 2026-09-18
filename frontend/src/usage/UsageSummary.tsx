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
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'

interface UsageSummaryProps {
  session: CareerVoiceSession
  refreshKey: number
  language: AppLanguage
}

type UsageState =
  | 'loading'
  | 'ready'
  | 'error'

function usageErrorMessage(
  error: unknown,
  language: AppLanguage,
): string {
  const text =
    UI_TEXT[language].usage.errors

  if (error instanceof ApiError) {
    if (error.status === 401) {
      return text.expired
    }

    if (error.status === 403) {
      return text.denied
    }

    if (error.status === 503) {
      return text.unavailable
    }
  }

  return text.generic
}

export function UsageSummary({
  session,
  refreshKey,
  language,
}: UsageSummaryProps) {
  const text =
    UI_TEXT[language].usage

  const [state, setState] =
    useState<UsageState>('loading')

  const [usage, setUsage] =
    useState<DailyUsage | null>(null)

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

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
          usageErrorMessage(
            error,
            language,
          ),
        )

        setState('error')
      }
    }

    void loadUsage()

    return () => {
      active = false
    }
  }, [
    session,
    refreshKey,
    language,
  ])

  if (state === 'loading') {
    return (
      <section className="usage-card">
        <p className="usage-status">
          {text.loading}
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
            {text.title}
          </p>

          <h2>
            {usage.remaining_ai_units}{' '}
            {text.remaining}
          </h2>
        </div>

        <p className="usage-total">
          {usage.ai_units_used}
          {' / '}
          {usage.daily_ai_unit_limit}
          {' '}
          {text.used}
        </p>
      </div>

      <div className="usage-details">
        <p>
          <strong>
            {usage.ai_profile_extractions}
          </strong>
          {' '}
          {text.profileExtractions}
        </p>

        <p>
          <strong>
            {usage.voice_transcriptions}
          </strong>
          {' '}
          {text.voiceTranscriptions}
        </p>

        <p>
          <strong>
            {usage.document_recognitions}
          </strong>
          {' '}
          {text.documentRecognitions}
        </p>

        <p>
          <strong>
            {usage.ai_ranking_runs}
          </strong>
          {' '}
          {text.rankingRuns}
        </p>

        <p>
          <strong>
            {usage.job_searches}
          </strong>
          {' '}
          {text.jobSearches}
        </p>
      </div>
    </section>
  )
}