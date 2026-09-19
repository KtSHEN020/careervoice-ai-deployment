import {
  useState,
  type FormEvent,
} from 'react'

import { ApiError } from '../api/client'
import type {
  NormalizedJob,
} from '../api/jobs'
import type {
  CareerProfile,
} from '../api/profile'
import {
  generateRecommendations,
  type RecommendationResponse,
} from '../api/recommendations'
import type { CareerVoiceSession } from '../auth/careervoice-session'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'
import {
  createRecommendationDraft,
  MAX_RECOMMENDATIONS,
} from './recommendation-state'

interface RecommendationPanelProps {
  session: CareerVoiceSession
  profile: CareerProfile
  jobs: NormalizedJob[]
  language: AppLanguage
  onComplete: (
    result: RecommendationResponse,
  ) => void
  onInvalidated: () => void
}

function recommendationErrorMessage(
  error: unknown,
  language: AppLanguage,
): string {
  const text =
    UI_TEXT[language].recommendations.errors

  if (error instanceof ApiError) {
    if (error.status === 401) {
      return text.expired
    }

    if (error.status === 403) {
      return text.denied
    }

    if (error.status === 422) {
      return text.invalid
    }

    if (error.status === 429) {
      return text.quota
    }

    if (error.status === 503) {
      return text.unavailable
    }
  }

  return text.generic
}

export function RecommendationPanel({
  session,
  profile,
  jobs,
  language,
  onComplete,
  onInvalidated,
}: RecommendationPanelProps) {
  const text =
    UI_TEXT[language].recommendations

  const maximumAvailableRecommendations =
    Math.min(
      MAX_RECOMMENDATIONS,
      jobs.length,
    )

  const recommendationOptions =
    Array.from(
      {
        length:
          maximumAvailableRecommendations,
      },
      (_, index) => index + 1,
    )

  const [draft, setDraft] = useState(
    () =>
      createRecommendationDraft(
        jobs.length,
      ),
  )

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [errorMessage, setErrorMessage] =
    useState('')

  const [statusMessage, setStatusMessage] =
    useState('')

  function invalidateResult() {
    setStatusMessage('')
    onInvalidated()
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setErrorMessage('')
    setStatusMessage('')
    onInvalidated()

    if (
      !Number.isInteger(draft.maxResults)
      || draft.maxResults < 1
      || draft.maxResults > MAX_RECOMMENDATIONS
      || draft.maxResults > jobs.length
    ) {
      setErrorMessage(
        text.errors.invalidResults,
      )
      return
    }

    setIsSubmitting(true)

    try {
      const result =
        await generateRecommendations(
          session.supabaseSession.access_token,
          {
            profile,
            jobs,
            scorer: draft.scorer,
            max_results:
              draft.maxResults,
            exclude_rejected:
              draft.excludeRejected,
            output_language:
              language,
          },
        )

      setDraft({
        scorer:
          result.settings.scorer,
        maxResults:
          result.settings.max_results,
        excludeRejected:
          result.settings.exclude_rejected,
      })

      setStatusMessage(
        text.success,
      )

      onComplete(result)
    } catch (error) {
      setErrorMessage(
        recommendationErrorMessage(
          error,
          language,
        ),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="recommendation-card">
      <p className="profile-kicker">
        {text.kicker}
      </p>

      <h2>
        {text.title}
      </h2>

      <p className="profile-copy">
        {text.description}
      </p>

      <form
        className="recommendation-form"
        onSubmit={handleSubmit}
      >
        <div className="recommendation-field">
          <label htmlFor="recommendation-scorer">
            {text.rankingMethod}
          </label>

          <select
            id="recommendation-scorer"
            value={draft.scorer}
            disabled={isSubmitting}
            onChange={(event) => {
              setDraft((current) => ({
                ...current,
                scorer:
                  event.target.value === 'llm'
                    ? 'llm'
                    : 'rules',
              }))

              invalidateResult()
            }}
          >
            <option value="rules">
              {text.standard}
            </option>

            <option value="llm">
              {text.aiAssisted}
            </option>
          </select>

          <p className="recommendation-help">
            {draft.scorer === 'llm'
              ? text.aiHelp
              : text.standardHelp}
          </p>
        </div>

        <div className="recommendation-field">
          <label htmlFor="recommendation-limit">
            {text.maxResults}
          </label>

          <select
            id="recommendation-limit"
            value={draft.maxResults}
            disabled={isSubmitting}
            onChange={(event) => {
                setDraft((current) => ({
                  ...current,
                  maxResults: Number(
                    event.target.value,
                  ),
                }))

                invalidateResult()
              }}
            >
              {recommendationOptions.map(
                (value) => (
                  <option
                    key={value}
                    value={value}
                  >
                    {value}
                  </option>
                ),
              )}
            </select>

          <p className="recommendation-help">
            {text.availableJobs}
            {': '}
            {jobs.length}
            {'. '}
            {text.maximumRecommendations}
            {': '}
            {maximumAvailableRecommendations}
            {'.'}
          </p>
        </div>

        <label className="recommendation-checkbox">
          <input
            type="checkbox"
            checked={
              draft.excludeRejected
            }
            disabled={isSubmitting}
            onChange={(event) => {
              setDraft((current) => ({
                ...current,
                excludeRejected:
                  event.target.checked,
              }))

              invalidateResult()
            }}
          />

          <span>
            <strong>
              {text.excludeRejected}
            </strong>

            <span className="recommendation-checkbox-help">
              {text.excludeRejectedHelp}
            </span>
          </span>
        </label>

        {statusMessage && (
          <p className="profile-message profile-message-success">
            {statusMessage}
          </p>
        )}

        {errorMessage && (
          <p className="profile-message profile-message-error">
            {errorMessage}
          </p>
        )}

        <button
          className="primary-button"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting
            ? text.generating
            : text.generate}
        </button>
      </form>
    </section>
  )
}