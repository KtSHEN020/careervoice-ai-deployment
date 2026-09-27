import type { CareerVoiceSession } from '../auth/careervoice-session'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'
import type { AppStep } from '../navigation/app-step'
import { UsageSummary } from '../usage/UsageSummary'

interface AppSidebarProps {
  session: CareerVoiceSession
  language: AppLanguage
  usageRefreshKey: number
  isOpen: boolean
  activeStep: AppStep
  profileComplete: boolean
  jobsComplete: boolean
  matchesComplete: boolean
  canOpenJobs: boolean
  canOpenMatches: boolean
  onStepChange: (
    step: AppStep,
  ) => void
  onClose: () => void
}

export function AppSidebar({
  session,
  language,
  usageRefreshKey,
  isOpen,
  activeStep,
  profileComplete,
  jobsComplete,
  matchesComplete,
  canOpenJobs,
  canOpenMatches,
  onStepChange,
  onClose,
}: AppSidebarProps) {
  const text = UI_TEXT[language]

  return (
    <aside
      className="app-sidebar"
      hidden={!isOpen}
    >
      <div className="sidebar-header">
        <div className="sidebar-section-title">
          {text.sidebar.navigation}
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

      <nav
        className="sidebar-navigation"
        aria-label={text.sidebar.navigation}
      >
        <button
          className={
            activeStep === 'profile'
              ? 'sidebar-nav-item sidebar-nav-item-active'
              : 'sidebar-nav-item'
          }
          type="button"
          aria-current={
            activeStep === 'profile'
              ? 'step'
              : undefined
          }
          onClick={() => {
            onStepChange('profile')
          }}
        >
          <span className="sidebar-nav-number">
            {profileComplete ? '✓' : '1'}
          </span>

          <span>
            {text.sidebar.profile}
          </span>
        </button>

        <button
          className={
            activeStep === 'jobs'
              ? 'sidebar-nav-item sidebar-nav-item-active'
              : 'sidebar-nav-item'
          }
          type="button"
          disabled={!canOpenJobs}
          aria-current={
            activeStep === 'jobs'
              ? 'step'
              : undefined
          }
          onClick={() => {
            onStepChange('jobs')
          }}
        >
          <span className="sidebar-nav-number">
            {jobsComplete ? '✓' : '2'}
          </span>

          <span>
            {text.sidebar.jobs}
          </span>
        </button>

        <button
          className={
            activeStep === 'matches'
              ? 'sidebar-nav-item sidebar-nav-item-active'
              : 'sidebar-nav-item'
          }
          type="button"
          disabled={!canOpenMatches}
          aria-current={
            activeStep === 'matches'
              ? 'step'
              : undefined
          }
          onClick={() => {
            onStepChange('matches')
          }}
        >
          <span className="sidebar-nav-number">
            {matchesComplete ? '✓' : '3'}
          </span>

          <span>
            {text.sidebar.matches}
          </span>
        </button>
      </nav>

      <div className="sidebar-divider" />

      <UsageSummary
        session={session}
        refreshKey={usageRefreshKey}
        language={language}
      />
    </aside>
  )
}