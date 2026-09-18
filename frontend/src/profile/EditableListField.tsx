import {
  useState,
  type KeyboardEvent,
} from 'react'

interface EditableListFieldProps {
  id: string
  label: string
  values: string[]
  placeholder: string
  addLabel: string
  removeLabel: string
  onChange: (values: string[]) => void
}

export function EditableListField({
  id,
  label,
  values,
  placeholder,
  addLabel,
  removeLabel,
  onChange,
}: EditableListFieldProps) {
  const [draft, setDraft] = useState('')

  function addValue() {
    const value = draft.trim()

    if (!value) {
      return
    }

    const alreadyExists = values.some(
      (current) =>
        current.trim().toLocaleLowerCase()
        === value.toLocaleLowerCase(),
    )

    if (!alreadyExists) {
      onChange([
        ...values,
        value,
      ])
    }

    setDraft('')
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLInputElement>,
  ) {
    if (event.key !== 'Enter') {
      return
    }

    event.preventDefault()
    addValue()
  }

  function removeValue(
    indexToRemove: number,
  ) {
    onChange(
      values.filter(
        (_, index) =>
          index !== indexToRemove,
      ),
    )
  }

  return (
    <div className="profile-review-field">
      <label htmlFor={id}>
        {label}
      </label>

      {values.length > 0 && (
        <div className="profile-tag-list">
          {values.map(
            (value, index) => (
              <span
                className="profile-tag"
                key={`${value}-${index}`}
              >
                <span>
                  {value}
                </span>

                <button
                  type="button"
                  aria-label={
                    `${removeLabel}: ${value}`
                  }
                  onClick={() => {
                    removeValue(index)
                  }}
                >
                  ×
                </button>
              </span>
            ),
          )}
        </div>
      )}

      <div className="profile-list-input-row">
        <input
          id={id}
          type="text"
          value={draft}
          placeholder={placeholder}
          onChange={(event) => {
            setDraft(
              event.target.value,
            )
          }}
          onKeyDown={handleKeyDown}
        />

        <button
          className="secondary-button"
          type="button"
          onClick={addValue}
        >
          {addLabel}
        </button>
      </div>
    </div>
  )
}