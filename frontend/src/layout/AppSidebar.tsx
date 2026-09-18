import type { CareerVoiceSession } from '../auth/careervoice-session'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'
import { LanguageToggle } from '../LanguageToggle'
import { UsageSummary } from '../usage/UsageSummary'

interface AppSidebarProps {
  session: CareerVoiceSession
  language: AppLanguage
  usageRefreshKey: number
  signOutError: string
  onLanguageChange: (
    language: AppLanguage,
  ) => void
  onSignOut: () => void
  onClose: () => void
}

export function AppSidebar({
  session,
  language,
  usageRefreshKey,
  signOutError,
  onLanguageChange,
  onSignOut,
  onClose,
}: AppSidebarProps) {
  const text = UI_TEXT[language]

  return (
    <aside className="app-sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand">
          CareerVoice AI
        </div>

        <button
          className="sidebar-toggle-button"
          type="button"
          aria-label={text.sidebar.hide}
          title={text.sidebar.hide}
          onClick={onClose}
        >
          ×
        </button>
      </div>

      <LanguageToggle
        language={language}
        onChange={onLanguageChange}
      />

      <div className="sidebar-account">
        <p className="sidebar-label">
          {text.auth.signedInAs}
        </p>

        <p className="sidebar-email">
          {session.user.email}
        </p>

        <button
          className="secondary-button sidebar-sign-out"
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

      <div className="sidebar-divider" />

      <UsageSummary
        session={session}
        refreshKey={usageRefreshKey}
        language={language}
      />
    </aside>
  )
}