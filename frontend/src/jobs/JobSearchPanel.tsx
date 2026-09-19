import {
  useState,
  type FormEvent,
} from 'react'

import { ApiError } from '../api/client'
import {
  searchJobs,
  type JobSearchResponse,
} from '../api/jobs'
import type { CareerProfile } from '../api/profile'
import type { CareerVoiceSession } from '../auth/careervoice-session'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'
import {
  createJobSearchDraft,
  MAX_JOB_ROLES,
  MAX_RESULTS_PER_ROLE,
  normalizeSearchRoles,
} from './job-search-state'

interface JobSearchPanelProps {
  session: CareerVoiceSession
  profile: CareerProfile
  language: AppLanguage
  onSearchComplete: (
    result: JobSearchResponse,
  ) => void
}

function jobSearchErrorMessage(
  error: unknown,
  language: AppLanguage,
): string {
  const text =
    UI_TEXT[language].jobSearch.errors

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

    if (error.status === 503) {
      return text.unavailable
    }
  }

  return text.generic
}

export function JobSearchPanel({
  session,
  profile,
  language,
  onSearchComplete,
}: JobSearchPanelProps) {
  const text =
    UI_TEXT[language].jobSearch

  const [draft, setDraft] = useState(
    () => createJobSearchDraft(profile),
  )

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [errorMessage, setErrorMessage] =
    useState('')

  const [statusMessage, setStatusMessage] =
    useState('')

  const [resultCount, setResultCount] =
    useState<number | null>(null)

  function updateRole(
    index: number,
    value: string,
  ) {
    setDraft((current) => ({
      ...current,
      roles: current.roles.map(
        (role, roleIndex) =>
          roleIndex === index
            ? value
            : role,
      ),
    }))

    setResultCount(null)
  }

  function addRole() {
    if (
      draft.roles.length
      >= MAX_JOB_ROLES
    ) {
      return
    }

    setDraft((current) => ({
      ...current,
      roles: [
        ...current.roles,
        '',
      ],
    }))

    setResultCount(null)
  }

  function removeRole(
    indexToRemove: number,
  ) {
    setDraft((current) => ({
      ...current,
      roles: current.roles.filter(
        (_, index) =>
          index !== indexToRemove,
      ),
    }))

    setResultCount(null)
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setErrorMessage('')
    setStatusMessage('')
    setResultCount(null)

    const roles =
      normalizeSearchRoles(
        draft.roles,
      )

    if (roles.length === 0) {
      setErrorMessage(
        text.errors.noRoles,
      )
      return
    }

    if (roles.length > MAX_JOB_ROLES) {
      setErrorMessage(
        text.errors.tooManyRoles,
      )
      return
    }

    if (
      !Number.isInteger(
        draft.maxResultsPerRole,
      )
      || draft.maxResultsPerRole < 1
      || draft.maxResultsPerRole
        > MAX_RESULTS_PER_ROLE
    ) {
      setErrorMessage(
        text.errors.invalidResults,
      )
      return
    }

    setIsSubmitting(true)

    try {
      const result =
        await searchJobs(
          session.supabaseSession.access_token,
          {
            profile,
            roles,
            location:
              draft.location.trim()
                || null,
            max_results_per_role:
              draft.maxResultsPerRole,
            source: draft.source,
            output_language:
              language,
          },
        )

      setDraft((current) => ({
        ...current,
        roles: result.settings.roles,
        location:
          result.settings.location
          ?? '',
        maxResultsPerRole:
          result.settings
            .max_results_per_role,
        source:
          result.settings.source,
      }))

      setResultCount(
        result.jobs.length,
      )

      setStatusMessage(
        text.success,
      )

      onSearchComplete(result)
    } catch (error) {
      setErrorMessage(
        jobSearchErrorMessage(
          error,
          language,
        ),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="job-search-card">
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
        className="job-search-form"
        onSubmit={handleSubmit}
      >
        <fieldset
          className="job-search-fieldset"
          disabled={isSubmitting}
        >
          <legend>
            {text.roles}
          </legend>

          <p className="job-search-help">
            {text.rolesHelp}
          </p>

          <div className="job-role-list">
            {draft.roles.map(
              (role, index) => (
                <div
                  className="job-role-row"
                  key={index}
                >
                  <label
                    htmlFor={
                      `job-role-${index}`
                    }
                  >
                    {text.role}{' '}
                    {index + 1}
                  </label>

                  <div className="job-role-input-row">
                    <input
                      id={
                        `job-role-${index}`
                      }
                      type="text"
                      value={role}
                      onChange={(event) => {
                        updateRole(
                          index,
                          event.target.value,
                        )
                      }}
                    />

                    <button
                      className="secondary-button"
                      type="button"
                      onClick={() => {
                        removeRole(index)
                      }}
                    >
                      {text.removeRole}
                    </button>
                  </div>
                </div>
              ),
            )}
          </div>

          {draft.roles.length
            < MAX_JOB_ROLES && (
            <button
              className="secondary-button job-add-role-button"
              type="button"
              onClick={addRole}
            >
              {text.addRole}
            </button>
          )}
        </fieldset>

        <div className="job-search-settings">
          <div className="job-search-field">
            <label htmlFor="job-location">
              {text.location}
            </label>

            <input
              id="job-location"
              type="text"
              value={draft.location}
              disabled={isSubmitting}
              placeholder={
                text.locationPlaceholder
              }
              onChange={(event) => {
                setDraft((current) => ({
                  ...current,
                  location:
                    event.target.value,
                }))

                setResultCount(null)
              }}
            />

            <p className="job-search-help">
              {text.locationHelp}
            </p>
          </div>

          <div className="job-search-field">
            <label htmlFor="job-results-limit">
              {text.resultsPerRole}
            </label>

            <input
              id="job-results-limit"
              type="number"
              min={1}
              max={MAX_RESULTS_PER_ROLE}
              step={1}
              value={
                draft.maxResultsPerRole
              }
              disabled={isSubmitting}
              onChange={(event) => {
                setDraft((current) => ({
                  ...current,
                  maxResultsPerRole:
                    Number(
                      event.target.value,
                    ),
                }))

                setResultCount(null)
              }}
            />

            <p className="job-search-help">
              {text.resultsHelp}
            </p>
          </div>

          <div className="job-search-field">
            <label htmlFor="job-source">
              {text.source}
            </label>

            <select
              id="job-source"
              value={draft.source}
              disabled
            >
              <option value="adzuna">
                {text.adzuna}
              </option>
            </select>
          </div>
        </div>

        {statusMessage && (
          <p className="profile-message profile-message-success">
            {statusMessage}
          </p>
        )}

        {resultCount !== null && (
          <p className="job-search-result-count">
            <strong>
              {resultCount}
            </strong>
            {' '}
            {text.found}
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
            ? text.searching
            : text.search}
        </button>
      </form>
    </section>
  )
}