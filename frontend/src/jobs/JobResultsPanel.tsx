import type {
  NormalizedJob,
} from '../api/jobs'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'

interface JobResultsPanelProps {
  jobs: NormalizedJob[]
  language: AppLanguage
}

function isSafeListingUrl(
  value: string,
): boolean {
  try {
    const url = new URL(value)

    return (
      url.protocol === 'http:'
      || url.protocol === 'https:'
    )
  } catch {
    return false
  }
}

export function JobResultsPanel({
  jobs,
  language,
}: JobResultsPanelProps) {
  const text =
    UI_TEXT[language].jobResults

  return (
    <section className="job-results-card">
      <div className="job-results-heading">
        <div>
          <p className="profile-kicker">
            {text.kicker}
          </p>

          <h2>
            {text.title}
          </h2>
        </div>

        <p className="job-results-count">
          <strong>
            {jobs.length}
          </strong>
          {' '}
          {text.found}
        </p>
      </div>

      {jobs.length === 0 ? (
        <p className="job-results-empty">
          {text.empty}
        </p>
      ) : (
        <div className="job-results-list">
          {jobs.map((job) => {
            const sourceName =
              job.source.toLocaleLowerCase()
              === 'adzuna'
                ? text.adzuna
                : job.source

            return (
              <article
                className="job-result-item"
                key={
                  `${job.source}-${job.job_id}`
                }
              >
                <div className="job-result-header">
                  <div>
                    <h3>
                      {job.title}
                    </h3>

                    <p className="job-result-company">
                      {job.company}
                    </p>
                  </div>

                  <div className="job-result-badges">
                    <span className="job-result-badge">
                      {
                        text.workTypes[
                          job.work_type
                        ]
                      }
                    </span>

                    <span className="job-result-badge">
                      {
                        text.seniority[
                          job.seniority
                        ]
                      }
                    </span>
                  </div>
                </div>

                <div className="job-result-meta">
                  <span>
                    <strong>
                      {text.location}:
                    </strong>
                    {' '}
                    {job.location}
                  </span>

                  <span>
                    <strong>
                      {text.source}:
                    </strong>
                    {' '}
                    {sourceName}
                  </span>
                </div>

                {job.required_skills.length
                  > 0 && (
                  <div className="job-result-section">
                    <h4>
                      {text.requiredSkills}
                    </h4>

                    <div className="job-result-chip-list">
                      {job.required_skills.map(
                        (skill) => (
                          <span
                            className="job-result-chip"
                            key={skill}
                          >
                            {skill}
                          </span>
                        ),
                      )}
                    </div>
                  </div>
                )}

                <details className="job-result-details">
                  <summary>
                    {text.details}
                  </summary>

                  <div className="job-result-details-content">
                    <div className="job-result-section">
                      <h4>
                        {text.description}
                      </h4>

                      <p className="job-result-description">
                        {job.description}
                      </p>
                    </div>

                    {job.preferred_skills.length
                      > 0 && (
                      <div className="job-result-section">
                        <h4>
                          {text.preferredSkills}
                        </h4>

                        <div className="job-result-chip-list">
                          {job.preferred_skills.map(
                            (skill) => (
                              <span
                                className="job-result-chip"
                                key={skill}
                              >
                                {skill}
                              </span>
                            ),
                          )}
                        </div>
                      </div>
                    )}

                    {job.responsibilities.length
                      > 0 && (
                      <div className="job-result-section">
                        <h4>
                          {text.responsibilities}
                        </h4>

                        <ul className="job-result-list">
                          {job.responsibilities.map(
                            (
                              responsibility,
                              index,
                            ) => (
                              <li
                                key={
                                  `${responsibility}-${index}`
                                }
                              >
                                {responsibility}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}

                    {job.tags.length > 0 && (
                      <div className="job-result-section">
                        <h4>
                          {text.tags}
                        </h4>

                        <div className="job-result-chip-list">
                          {job.tags.map(
                            (tag) => (
                              <span
                                className="job-result-chip"
                                key={tag}
                              >
                                {tag}
                              </span>
                            ),
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </details>

                {isSafeListingUrl(
                  job.source_url,
                ) && (
                  <a
                    className="job-listing-link"
                    href={job.source_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {text.viewListing}
                  </a>
                )}
              </article>
            )
          })}
        </div>
      )}
    </section>
  )
}