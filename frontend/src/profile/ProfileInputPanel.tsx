import {
  useState,
  type FormEvent,
} from 'react'

import { ApiError } from '../api/client'
import {
  extractCareerProfile,
  type ProfileExtractionResponse,
} from '../api/profile'
import type { CareerVoiceSession } from '../auth/careervoice-session'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'
import {
  DEFAULT_PROFILE_DRAFT,
  type ProfileDraft,
} from './profile-state'

interface ProfileInputPanelProps {
  session: CareerVoiceSession
  language: AppLanguage
  onProfileExtracted: (
    result: ProfileExtractionResponse,
  ) => void
}

const MAX_CAREER_TEXT_CHARACTERS = 12_000

function extractionErrorMessage(
  error: unknown,
  language: AppLanguage,
): string {
  const text =
    UI_TEXT[language].profile.errors

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

export function ProfileInputPanel({
  session,
  language,
  onProfileExtracted,
}: ProfileInputPanelProps) {
  const text =
    UI_TEXT[language].profile

  const [draft, setDraft] =
    useState<ProfileDraft>(
      DEFAULT_PROFILE_DRAFT,
    )

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [errorMessage, setErrorMessage] =
    useState('')

  const [statusMessage, setStatusMessage] =
    useState('')

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setErrorMessage('')
    setStatusMessage('')

    const careerText =
      draft.careerText.trim()

    if (!careerText) {
      setErrorMessage(
        text.errors.empty,
      )
      return
    }

    setIsSubmitting(true)

    try {
      const result =
        await extractCareerProfile(
          session.supabaseSession.access_token,
          {
            career_preference_text:
              careerText,
            extractor:
              draft.extractor,
            output_language:
              language,
          },
        )

      onProfileExtracted(result)

      setStatusMessage(
        text.success,
      )
    } catch (error) {
      setErrorMessage(
        extractionErrorMessage(
          error,
          language,
        ),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="profile-input-card">
      <div className="profile-section-heading">
        <div>
          <p className="profile-kicker">
            {text.step}
          </p>

          <h2>
            {text.title}
          </h2>
        </div>
      </div>

      <p className="profile-copy">
        {text.description}
      </p>

      <form
        className="profile-form"
        onSubmit={handleSubmit}
      >
        <label htmlFor="career-information">
          {text.information}
        </label>

        <textarea
          id="career-information"
          name="career-information"
          rows={9}
          maxLength={
            MAX_CAREER_TEXT_CHARACTERS
          }
          value={draft.careerText}
          disabled={isSubmitting}
          placeholder={text.placeholder}
          onChange={(event) => {
            setDraft((current) => ({
              ...current,
              careerText:
                event.target.value,
            }))
          }}
          required
        />

        <div className="profile-character-count">
          {draft.careerText.length.toLocaleString()}
          {' / '}
          {MAX_CAREER_TEXT_CHARACTERS.toLocaleString()}
        </div>

        <div className="profile-options">
          <div className="profile-field">
            <label htmlFor="extractor">
              {text.extractionMethod}
            </label>

            <select
              id="extractor"
              value={draft.extractor}
              disabled={isSubmitting}
              onChange={(event) => {
                setDraft((current) => ({
                  ...current,
                  extractor:
                    event.target.value ===
                    'llm'
                      ? 'llm'
                      : 'rules',
                }))
              }}
            >
              <option value="rules">
                {text.standard}
              </option>

              <option value="llm">
                {text.aiAssisted}
              </option>
            </select>
          </div>
        </div>

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
            ? text.extracting
            : text.extract}
        </button>
      </form>
    </section>
  )
}