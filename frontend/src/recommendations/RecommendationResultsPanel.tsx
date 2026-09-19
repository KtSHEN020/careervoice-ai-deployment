import type {
  RecommendationItem,
  RecommendationResponse,
} from '../api/recommendations'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'

interface RecommendationResultsPanelProps {
  result: RecommendationResponse
  language: AppLanguage
}

function formatScore(
  score: number,
  language: AppLanguage,
): string {
  return new Intl.NumberFormat(
    language,
    {
      maximumFractionDigits: 2,
    },
  ).format(score)
}

interface RecommendationItemCardProps {
  recommendation: RecommendationItem
  rank: number
  language: AppLanguage
}

function RecommendationItemCard({
  recommendation,
  rank,
  language,
}: RecommendationItemCardProps) {
  const text =
    UI_TEXT[language].recommendationResults

  const scoringMethod =
    recommendation.scoring_method === 'llm'
      ? text.aiAssisted
      : text.standard

  return (
    <article
      className={
        recommendation
          .is_rejected_by_constraints
          ? 'recommendation-result-item recommendation-result-rejected'
          : 'recommendation-result-item'
      }
    >
      <div className="recommendation-result-header">
        <div>
          <p className="recommendation-rank">
            {text.rank}
            {' '}
            {rank}
          </p>

          <h3>
            {recommendation.title}
          </h3>

          <p className="recommendation-company">
            {recommendation.company}
          </p>
        </div>

        <div className="recommendation-score-block">
          <span className="recommendation-score">
            {formatScore(
              recommendation.match_score,
              language,
            )}
          </span>

          <span className="recommendation-score-label">
            {text.matchScore}
          </span>
        </div>
      </div>

      <div className="recommendation-meta">
        {recommendation.recommendation_level && (
          <span className="recommendation-level">
            {
              recommendation
                .recommendation_level
            }
          </span>
        )}

        <span>
          <strong>
            {text.rankingMethod}:
          </strong>
          {' '}
          {scoringMethod}
        </span>
      </div>

      {recommendation
        .is_rejected_by_constraints && (
        <div className="recommendation-constraint-warning">
          <strong>
            {text.constraintConflict}
          </strong>

          <span>
            {
              text.constraintConflictDescription
            }
          </span>
        </div>
      )}

      {recommendation.reasons.length > 0 && (
        <section className="recommendation-result-section">
          <h4>
            {text.reasons}
          </h4>

          <ul>
            {recommendation.reasons.map(
              (reason, index) => (
                <li
                  key={`${reason}-${index}`}
                >
                  {reason}
                </li>
              ),
            )}
          </ul>
        </section>
      )}

      {recommendation.missing_skills.length
        > 0 && (
        <section className="recommendation-result-section">
          <h4>
            {text.missingSkills}
          </h4>

          <div className="recommendation-chip-list">
            {recommendation.missing_skills.map(
              (skill, index) => (
                <span
                  className="recommendation-chip"
                  key={`${skill}-${index}`}
                >
                  {skill}
                </span>
              ),
            )}
          </div>
        </section>
      )}

      {recommendation.penalties.length > 0 && (
        <details className="recommendation-details">
          <summary>
            {text.penalties}
          </summary>

          <ul>
            {recommendation.penalties.map(
              (penalty, index) => (
                <li
                  key={`${penalty}-${index}`}
                >
                  {penalty}
                </li>
              ),
            )}
          </ul>
        </details>
      )}

      {recommendation.uncertainties.length
        > 0 && (
        <details className="recommendation-details">
          <summary>
            {text.uncertainties}
          </summary>

          <ul>
            {recommendation.uncertainties.map(
              (uncertainty, index) => (
                <li
                  key={`${uncertainty}-${index}`}
                >
                  {uncertainty}
                </li>
              ),
            )}
          </ul>
        </details>
      )}
    </article>
  )
}

export function RecommendationResultsPanel({
  result,
  language,
}: RecommendationResultsPanelProps) {
  const text =
    UI_TEXT[language].recommendationResults

  const scoringMethod =
    result.scoring_method === 'llm'
      ? text.aiAssisted
      : text.standard

  return (
    <section className="recommendation-results-card">
      <div className="recommendation-results-heading">
        <div>
          <p className="profile-kicker">
            {text.kicker}
          </p>

          <h2>
            {text.title}
          </h2>
        </div>

        <p className="recommendation-results-count">
          <strong>
            {
              result
                .total_recommendations_returned
            }
          </strong>
          {' '}
          {text.returned}
        </p>
      </div>

      <div className="recommendation-results-summary">
        <span>
          <strong>
            {text.jobsScored}:
          </strong>
          {' '}
          {result.total_jobs_scored}
        </span>

        <span>
          <strong>
            {text.rankingMethod}:
          </strong>
          {' '}
          {scoringMethod}
        </span>

        {result.total_jobs_scored_with_llm
          !== null && (
          <span>
            <strong>
              {text.jobsScoredWithAi}:
            </strong>
            {' '}
            {
              result
                .total_jobs_scored_with_llm
            }
          </span>
        )}
      </div>

      {result.recommendations.length === 0 ? (
        <p className="recommendation-results-empty">
          {text.empty}
        </p>
      ) : (
        <div className="recommendation-results-list">
          {result.recommendations.map(
            (recommendation, index) => (
              <RecommendationItemCard
                key={
                  `${recommendation.job_id}-${index}`
                }
                recommendation={
                  recommendation
                }
                rank={index + 1}
                language={language}
              />
            ),
          )}
        </div>
      )}
    </section>
  )
}