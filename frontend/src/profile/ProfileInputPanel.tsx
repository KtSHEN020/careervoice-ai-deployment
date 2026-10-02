import {
  useRef,
  useState,
  type FormEvent,
} from 'react'

import { ApiError } from '../api/client'
import {
  extractCareerProfile,
  extractCareerProfileFromDocument,
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

type ProfileInputMode =
  | 'text'
  | 'document'

const MAX_CAREER_TEXT_CHARACTERS = 12_000
const MAX_ADDITIONAL_PREFERENCES_CHARACTERS =
  4_000
const MAX_DOCUMENT_BYTES =
  5 * 1024 * 1024

function extractionErrorMessage(
  error: unknown,
  language: AppLanguage,
  inputMode: ProfileInputMode,
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

    if (error.status === 413) {
      return text.documentTooLarge
    }

    if (error.status === 422) {
      return inputMode === 'document'
        ? text.documentInvalid
        : text.invalid
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

  const documentInputRef =
    useRef<HTMLInputElement>(null)

  const [draft, setDraft] =
    useState<ProfileDraft>(
      DEFAULT_PROFILE_DRAFT,
    )

  const [
    inputMode,
    setInputMode,
  ] = useState<ProfileInputMode>('text')

  const [
    documentFile,
    setDocumentFile,
  ] = useState<File | null>(null)

  const [
    additionalPreferences,
    setAdditionalPreferences,
  ] = useState('')

  const [
    allowImageRecognition,
    setAllowImageRecognition,
  ] = useState(false)

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [errorMessage, setErrorMessage] =
    useState('')

  const [statusMessage, setStatusMessage] =
    useState('')

  const selectedDocumentIsPdf =
    documentFile?.name
      .toLowerCase()
      .endsWith('.pdf')
    ?? false

  function handleInputModeChange(
    nextMode: ProfileInputMode,
  ) {
    setInputMode(nextMode)
    setErrorMessage('')
    setStatusMessage('')
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setErrorMessage('')
    setStatusMessage('')

    if (inputMode === 'text') {
      const careerText =
        draft.careerText.trim()

      if (!careerText) {
        setErrorMessage(
          text.errors.empty,
        )

        return
      }
    } else {
      if (documentFile === null) {
        setErrorMessage(
          text.errors.documentMissing,
        )

        return
      }

      if (
        documentFile.size
        > MAX_DOCUMENT_BYTES
      ) {
        setErrorMessage(
          text.errors.documentTooLarge,
        )

        return
      }
    }

    setIsSubmitting(true)

    try {
      const accessToken =
        session.supabaseSession.access_token

      const result =
        inputMode === 'text'
          ? await extractCareerProfile(
              accessToken,
              {
                career_preference_text:
                  draft.careerText.trim(),
                extractor:
                  draft.extractor,
                output_language:
                  language,
              },
            )
          : await extractCareerProfileFromDocument(
              accessToken,
              {
                document:
                  documentFile as File,
                extractor:
                  draft.extractor,
                output_language:
                  language,
                additional_preferences:
                  additionalPreferences.trim(),
                allow_image_recognition:
                  allowImageRecognition,
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
          inputMode,
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
        <fieldset className="profile-input-mode">
          <legend>
            {text.inputMethod}
          </legend>

          <div className="profile-input-mode-buttons">
            <button
              className={
                inputMode === 'text'
                  ? 'profile-input-mode-button profile-input-mode-button-active'
                  : 'profile-input-mode-button'
              }
              type="button"
              aria-pressed={
                inputMode === 'text'
              }
              disabled={isSubmitting}
              onClick={() => {
                handleInputModeChange(
                  'text',
                )
              }}
            >
              {text.textInput}
            </button>

            <button
              className={
                inputMode === 'document'
                  ? 'profile-input-mode-button profile-input-mode-button-active'
                  : 'profile-input-mode-button'
              }
              type="button"
              aria-pressed={
                inputMode === 'document'
              }
              disabled={isSubmitting}
              onClick={() => {
                handleInputModeChange(
                  'document',
                )
              }}
            >
              {text.documentInput}
            </button>
          </div>
        </fieldset>

        {inputMode === 'text' ? (
          <>
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
          </>
        ) : (
          <>
            <div className="profile-field">
              <span className="profile-field-label">
                {text.document}
              </span>

              <input
                ref={documentInputRef}
                id="career-document"
                name="career-document"
                className="profile-file-input"
                type="file"
                accept=".txt,.pdf,.docx"
                disabled={isSubmitting}
                onChange={(event) => {
                  const file =
                    event.target.files?.[0]
                    ?? null

                  setDocumentFile(file)

                  if (
                    !file?.name
                      .toLowerCase()
                      .endsWith('.pdf')
                  ) {
                    setAllowImageRecognition(
                      false,
                    )
                  }

                  setErrorMessage('')
                  setStatusMessage('')
                }}
              />

              <div className="profile-file-control">
                <button
                  className="secondary-button profile-file-button"
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => {
                    documentInputRef.current?.click()
                  }}
                >
                  {text.chooseFile}
                </button>

                <span
                  className={
                    documentFile === null
                      ? 'profile-file-name profile-file-name-empty'
                      : 'profile-file-name'
                  }
                >
                  {documentFile?.name
                    ?? text.noFileSelected}
                </span>
              </div>

              <p className="profile-help">
                {text.documentHelp}
              </p>
            </div>

            <div className="profile-field">
              <label htmlFor="additional-preferences">
                {text.additionalPreferences}
              </label>

              <textarea
                id="additional-preferences"
                name="additional-preferences"
                rows={5}
                maxLength={
                  MAX_ADDITIONAL_PREFERENCES_CHARACTERS
                }
                value={
                  additionalPreferences
                }
                disabled={isSubmitting}
                placeholder={
                  text.additionalPreferencesPlaceholder
                }
                onChange={(event) => {
                  setAdditionalPreferences(
                    event.target.value,
                  )
                }}
              />

              <div className="profile-character-count">
                {additionalPreferences.length.toLocaleString()}
                {' / '}
                {MAX_ADDITIONAL_PREFERENCES_CHARACTERS.toLocaleString()}
              </div>
            </div>

            {selectedDocumentIsPdf && (
              <label className="profile-checkbox">
                <input
                  type="checkbox"
                  checked={
                    allowImageRecognition
                  }
                  disabled={isSubmitting}
                  onChange={(event) => {
                    setAllowImageRecognition(
                      event.target.checked,
                    )
                  }}
                />

                <span>
                  <strong>
                    {text.imageRecognition}
                  </strong>

                  <span className="profile-checkbox-help">
                    {text.imageRecognitionHelp}
                  </span>
                </span>
              </label>
            )}
          </>
        )}

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
          <p
            className="profile-message profile-message-success"
            role="status"
          >
            {statusMessage}
          </p>
        )}

        {errorMessage && (
          <p
            className="profile-message profile-message-error"
            role="alert"
          >
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