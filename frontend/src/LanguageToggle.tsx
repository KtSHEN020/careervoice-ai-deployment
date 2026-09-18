import type { AppLanguage } from './i18n'
import { UI_TEXT } from './i18n'

interface LanguageToggleProps {
  language: AppLanguage
  onChange: (language: AppLanguage) => void
}

export function LanguageToggle({
  language,
  onChange,
}: LanguageToggleProps) {
  const text = UI_TEXT[language]

  return (
    <div
      className="language-toggle"
      role="group"
      aria-label={text.language.select}
    >
      <button
        type="button"
        className={
          language === 'en'
            ? 'language-button language-button-active'
            : 'language-button'
        }
        aria-pressed={language === 'en'}
        onClick={() => {
          onChange('en')
        }}
      >
        ENG
      </button>

      <button
        type="button"
        className={
          language === 'zh-CN'
            ? 'language-button language-button-active'
            : 'language-button'
        }
        aria-pressed={language === 'zh-CN'}
        onClick={() => {
          onChange('zh-CN')
        }}
      >
        简体中文
      </button>
    </div>
  )
}