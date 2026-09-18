import type { CareerProfile } from '../api/profile'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'
import { EditableListField } from './EditableListField'

interface ProfileReviewPanelProps {
  profile: CareerProfile
  language: AppLanguage
  confirmed: boolean
  onChange: (
    profile: CareerProfile,
  ) => void
  onConfirm: () => void
}

type ListFieldKey =
  | 'target_roles'
  | 'skills'
  | 'preferred_locations'
  | 'preferred_work_types'
  | 'liked_areas'
  | 'disliked_areas'
  | 'hard_constraints'
  | 'career_goals'
  | 'notes'

export function ProfileReviewPanel({
  profile,
  language,
  confirmed,
  onChange,
  onConfirm,
}: ProfileReviewPanelProps) {
  const text =
    UI_TEXT[language].profileReview

  function updateListField(
    field: ListFieldKey,
    values: string[],
  ) {
    onChange({
      ...profile,
      [field]: values,
    })
  }

  function updateExperienceLevel(
    value: string,
  ) {
    const normalized =
      value.trim()

    onChange({
      ...profile,
      experience_level:
        normalized || null,
    })
  }

  const listFields: Array<{
    key: ListFieldKey
    label: string
    placeholder: string
  }> = [
    {
      key: 'target_roles',
      label: text.targetRoles,
      placeholder:
        text.placeholders.targetRoles,
    },
    {
      key: 'skills',
      label: text.skills,
      placeholder:
        text.placeholders.skills,
    },
    {
      key: 'preferred_locations',
      label: text.preferredLocations,
      placeholder:
        text.placeholders.preferredLocations,
    },
    {
      key: 'preferred_work_types',
      label: text.preferredWorkTypes,
      placeholder:
        text.placeholders.preferredWorkTypes,
    },
    {
      key: 'liked_areas',
      label: text.likedAreas,
      placeholder:
        text.placeholders.likedAreas,
    },
    {
      key: 'disliked_areas',
      label: text.dislikedAreas,
      placeholder:
        text.placeholders.dislikedAreas,
    },
    {
      key: 'hard_constraints',
      label: text.hardConstraints,
      placeholder:
        text.placeholders.hardConstraints,
    },
    {
      key: 'career_goals',
      label: text.careerGoals,
      placeholder:
        text.placeholders.careerGoals,
    },
    {
      key: 'notes',
      label: text.notes,
      placeholder:
        text.placeholders.notes,
    },
  ]

  return (
    <section className="profile-review-card">
      <div className="profile-section-heading">
        <div>
          <p className="profile-kicker">
            {text.kicker}
          </p>

          <h2>
            {text.title}
          </h2>
        </div>
      </div>

      <p className="profile-copy">
        {text.description}
      </p>

      <div className="profile-review-grid">
        <div className="profile-review-field">
          <label htmlFor="experience-level">
            {text.experienceLevel}
          </label>

          <input
            id="experience-level"
            type="text"
            value={
              profile.experience_level
              ?? ''
            }
            placeholder={
              text.placeholders
                .experienceLevel
            }
            onChange={(event) => {
              updateExperienceLevel(
                event.target.value,
              )
            }}
          />
        </div>

        {listFields.map((field) => (
          <EditableListField
            key={field.key}
            id={`profile-${field.key}`}
            label={field.label}
            values={
              profile[field.key]
            }
            placeholder={
              field.placeholder
            }
            addLabel={text.add}
            removeLabel={text.remove}
            onChange={(values) => {
              updateListField(
                field.key,
                values,
              )
            }}
          />
        ))}
      </div>

      <div className="profile-review-actions">
        <button
          className="primary-button"
          type="button"
          disabled={confirmed}
          onClick={onConfirm}
        >
          {confirmed
            ? text.confirmed
            : text.confirm}
        </button>

        {confirmed && (
          <p className="profile-message profile-message-success">
            {text.confirmationMessage}
          </p>
        )}
      </div>
    </section>
  )
}