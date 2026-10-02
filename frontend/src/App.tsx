import { useState } from 'react'

import './App.css'

import type {
  CareerProfile,
  ProfileExtractionResponse,
} from './api/profile'
import { signOutCurrentSession } from './auth/authentication'
import { AuthPanel } from './auth/AuthPanel'
import type { CareerVoiceSession } from './auth/careervoice-session'
import {
  loadAppLanguage,
  saveAppLanguage,
  UI_TEXT,
  type AppLanguage,
} from './i18n'
import { LanguageToggle } from './LanguageToggle'
import { AppSidebar } from './layout/AppSidebar'
import { ProfileInputPanel } from './profile/ProfileInputPanel'
import { ProfileReviewPanel } from './profile/ProfileReviewPanel'
import type {
  JobSearchResponse,
} from './api/jobs'
import { JobSearchPanel } from './jobs/JobSearchPanel'
import { JobResultsPanel } from './jobs/JobResultsPanel'
import type {
  RecommendationResponse,
} from './api/recommendations'
import { RecommendationPanel } from './recommendations/RecommendationPanel'
import {
  RecommendationResultsPanel,
} from './recommendations/RecommendationResultsPanel'
import type { AppStep } from './navigation/app-step'
import { AppTopbar } from './layout/AppTopbar'

function App() {
  const [language, setLanguage] =
    useState<AppLanguage>(
      loadAppLanguage,
    )

  const [
    careerVoiceSession,
    setCareerVoiceSession,
  ] = useState<CareerVoiceSession | null>(
    null,
  )

  const [
    extractedProfile,
    setExtractedProfile,
  ] =
    useState<ProfileExtractionResponse | null>(
      null,
    )

  const [
    profileConfirmed,
    setProfileConfirmed,
  ] = useState(false)

  const [
    jobSearchResult,
    setJobSearchResult,
  ] = useState<JobSearchResponse | null>(
    null,
  )

  const [
    recommendationResult,
    setRecommendationResult,
  ] =
    useState<RecommendationResponse | null>(
      null,
    )

  const [
    usageRefreshKey,
    setUsageRefreshKey,
  ] = useState(0)

  const [signOutError, setSignOutError] =
    useState('')

  const [
    sidebarOpen,
    setSidebarOpen,
  ] = useState(true)

  const [
  activeStep,
  setActiveStep,
] = useState<AppStep>('profile')

  const text = UI_TEXT[language]

  function handleSessionChange(
    session: CareerVoiceSession | null,
  ) {
    setCareerVoiceSession(session)

    if (session !== null) {
      setSidebarOpen(true)
      setActiveStep('profile')
    }
  }

  function handleLanguageChange(
    nextLanguage: AppLanguage,
  ) {
    setLanguage(nextLanguage)
    saveAppLanguage(nextLanguage)
    setSignOutError('')
  }

  function handleProfileExtracted(
    result: ProfileExtractionResponse,
  ) {
    setExtractedProfile(result)
    setProfileConfirmed(false)
    setJobSearchResult(null)
    setRecommendationResult(null)
    setActiveStep('profile')

    setUsageRefreshKey(
      (current) => current + 1,
    )
  }

  function handleProfileChange(
    profile: CareerProfile,
  ) {
    setExtractedProfile(
      (current) => {
        if (current === null) {
          return null
        }

        return {
          ...current,
          profile,
        }
      },
    )

    setProfileConfirmed(false)
    setJobSearchResult(null)
    setRecommendationResult(null)
    setActiveStep('profile')
  }

  function handleJobSearchComplete(
    result: JobSearchResponse,
  ) {
    setJobSearchResult(result)
    setRecommendationResult(null)

    setUsageRefreshKey(
      (current) => current + 1,
    )
  }

  function handleRecommendationComplete(
    result: RecommendationResponse,
  ) {
    setRecommendationResult(result)

    setUsageRefreshKey(
      (current) => current + 1,
    )
  }

  function handleProfileConfirm() {
    setProfileConfirmed(true)
  }

  async function handleSignOut() {
    setSignOutError('')
    setActiveStep('profile')

    try {
      await signOutCurrentSession()

      setCareerVoiceSession(null)
      setExtractedProfile(null)
      setProfileConfirmed(false)
      setJobSearchResult(null)
      setSidebarOpen(true)
      setRecommendationResult(null)
    } catch {
      setSignOutError(
        text.app.signOutError,
      )
    }
  }

  if (careerVoiceSession === null) {
    return (
      <main className="auth-page">
        <section className="auth-page-content">
          <LanguageToggle
            language={language}
            onChange={handleLanguageChange}
          />

          <h1 className="auth-page-title">
            CareerVoice AI
          </h1>

          <AuthPanel
            language={language}
            onSessionChange={
              handleSessionChange
            }
          />
        </section>
      </main>
    )
  }

  const canOpenJobs =
    extractedProfile !== null
    && profileConfirmed

  const canOpenMatches =
    jobSearchResult !== null
    && jobSearchResult.jobs.length > 0

  return (
    <main
      className={
        sidebarOpen
          ? 'authenticated-shell'
          : 'authenticated-shell authenticated-shell-sidebar-closed'
      }
    >
      <AppSidebar
        session={careerVoiceSession}
        language={language}
        usageRefreshKey={
          usageRefreshKey
        }
        isOpen={sidebarOpen}
        activeStep={activeStep}
        profileComplete={profileConfirmed}
        jobsComplete={
          jobSearchResult !== null
        }
        matchesComplete={
          recommendationResult !== null
        }
        canOpenJobs={canOpenJobs}
        canOpenMatches={canOpenMatches}
        onStepChange={setActiveStep}
        onClose={() => {
          setSidebarOpen(false)
        }}
      />

      {!sidebarOpen && (
        <button
          className="sidebar-open-button"
          type="button"
          aria-label={text.sidebar.show}
          title={text.sidebar.show}
          onClick={() => {
            setSidebarOpen(true)
          }}
        >
          ☰
        </button>
      )}

      {sidebarOpen && (
        <button
          className="sidebar-overlay"
          type="button"
          aria-label={text.sidebar.hide}
          onClick={() => {
            setSidebarOpen(false)
          }}
        />
      )}

      <section className="app-content">
        <AppTopbar
          session={careerVoiceSession}
          language={language}
          signOutError={signOutError}
          onLanguageChange={
            handleLanguageChange
          }
          onSignOut={() => {
            void handleSignOut()
          }}
        />

        <div className="hero">
          <h1 className="sr-only">
            CareerVoice AI
          </h1>

          {activeStep === 'profile' && (
            <>
              <ProfileInputPanel
                session={careerVoiceSession}
                language={language}
                onProfileExtracted={
                  handleProfileExtracted
                }
                onUsageChanged={() => {
                  setUsageRefreshKey(
                    (current) => current + 1,
                  )
                }}
              />

              {extractedProfile !== null && (
                <ProfileReviewPanel
                  profile={
                    extractedProfile.profile
                  }
                  language={language}
                  confirmed={
                    profileConfirmed
                  }
                  onChange={
                    handleProfileChange
                  }
                  onConfirm={
                    handleProfileConfirm
                  }
                />
              )}

              <nav
                className="step-navigation step-navigation-next-only"
                aria-label={text.sidebar.navigation}
              >
                <button
                  className="primary-button step-navigation-button"
                  type="button"
                  disabled={!canOpenJobs}
                  onClick={() => {
                    setActiveStep('jobs')
                  }}
                >
                  {text.navigation.nextToJobs}
                </button>
              </nav>
            </>
          )}

          {activeStep === 'jobs'
            && canOpenJobs
            && extractedProfile !== null && (
            <>
              <JobSearchPanel
                session={careerVoiceSession}
                profile={
                  extractedProfile.profile
                }
                language={language}
                onSearchComplete={
                  handleJobSearchComplete
                }
                onSearchInvalidated={() => {
                  setJobSearchResult(null)
                  setRecommendationResult(null)
                }}
              />

              {jobSearchResult !== null && (
                <JobResultsPanel
                  jobs={jobSearchResult.jobs}
                  language={language}
                />
              )}

              <nav
                className="step-navigation"
                aria-label={text.sidebar.navigation}
              >
                <button
                  className="secondary-button step-navigation-button"
                  type="button"
                  onClick={() => {
                    setActiveStep('profile')
                  }}
                >
                  {text.navigation.backToProfile}
                </button>

                <button
                  className="primary-button step-navigation-button"
                  type="button"
                  disabled={!canOpenMatches}
                  onClick={() => {
                    setActiveStep('matches')
                  }}
                >
                  {text.navigation.nextToMatches}
                </button>
              </nav>
            </>
          )}

          {activeStep === 'matches'
            && canOpenMatches
            && extractedProfile !== null
            && jobSearchResult !== null && (
            <>
              <RecommendationPanel
                session={careerVoiceSession}
                profile={
                  extractedProfile.profile
                }
                jobs={
                  jobSearchResult.jobs
                }
                language={language}
                onComplete={
                  handleRecommendationComplete
                }
                onInvalidated={() => {
                  setRecommendationResult(null)
                }}
              />

              {recommendationResult !== null && (
                <RecommendationResultsPanel
                  result={recommendationResult}
                  language={language}
                />
              )}

              <nav
                className="step-navigation"
                aria-label={text.sidebar.navigation}
              >
                <button
                  className="secondary-button step-navigation-button"
                  type="button"
                  onClick={() => {
                    setActiveStep('jobs')
                  }}
                >
                  {text.navigation.backToJobs}
                </button>
              </nav>
            </>
          )}
        </div>
      </section>
    </main>
  )
}

export default App