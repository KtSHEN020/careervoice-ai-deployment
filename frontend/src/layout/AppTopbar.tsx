import type { CareerVoiceSession } from '../auth/careervoice-session'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'
import { LanguageToggle } from '../LanguageToggle'

interface AppTopbarProps {
  session: CareerVoiceSession
  language: AppLanguage
  signOutError: string
  onLanguageChange: (
    language: AppLanguage,
  ) => void
  onSignOut: () => void
}

export function AppTopbar({
  session,
  language,
  signOutError,
  onLanguageChange,
  onSignOut,
}: AppTopbarProps) {
  const text = UI_TEXT[language]

  return (
    <header className="app-topbar">
      <div className="app-topbar-intro">
        <p className="app-topbar-brand">
          CareerVoice AI
        </p>

        <p className="app-topbar-description">
          {text.app.productSummary}
        </p>
      </div>

      <div className="app-topbar-actions">
        <LanguageToggle
          language={language}
          onChange={onLanguageChange}
        />

        <details className="account-menu">
          <summary className="account-menu-trigger">
            {text.sidebar.account}
          </summary>

          <div className="account-menu-panel">
            <p className="account-menu-label">
              {text.auth.signedInAs}
            </p>

            <p className="account-menu-email">
              {session.user.email}
            </p>

            <button
              className="secondary-button account-sign-out"
              type="button"
              onClick={onSignOut}
            >
              {text.app.signOut}
            </button>

            {signOutError && (
              <p className="auth-message auth-message-error">
                {signOutError}
              </p>
            )}
          </div>
        </details>
      </div>
    </header>
  )
}