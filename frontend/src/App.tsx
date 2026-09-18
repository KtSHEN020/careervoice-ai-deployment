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
    usageRefreshKey,
    setUsageRefreshKey,
  ] = useState(0)

  const [signOutError, setSignOutError] =
    useState('')

  const [
    sidebarOpen,
    setSidebarOpen,
  ] = useState(true)

  const text = UI_TEXT[language]

  function handleSessionChange(
    session: CareerVoiceSession | null,
  ) {
    setCareerVoiceSession(session)

    if (session !== null) {
      setSidebarOpen(true)
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
  }

  function handleProfileConfirm() {
    setProfileConfirmed(true)
  }

  async function handleSignOut() {
    setSignOutError('')

    try {
      await signOutCurrentSession()

      setCareerVoiceSession(null)
      setExtractedProfile(null)
      setProfileConfirmed(false)
      setSidebarOpen(true)
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

  return (
    <main
      className={
        sidebarOpen
          ? 'authenticated-shell'
          : 'authenticated-shell authenticated-shell-sidebar-closed'
      }
    >
      {sidebarOpen && (
        <AppSidebar
          session={careerVoiceSession}
          language={language}
          usageRefreshKey={
            usageRefreshKey
          }
          signOutError={signOutError}
          onLanguageChange={
            handleLanguageChange
          }
          onSignOut={() => {
            void handleSignOut()
          }}
          onClose={() => {
            setSidebarOpen(false)
          }}
        />
      )}

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
        <div className="hero">
          <p className="eyebrow">
            CareerVoice AI
          </p>

          <h1>
            {text.app.headline}
          </h1>

          <p className="hero-description">
            {text.app.description}
          </p>

          <ProfileInputPanel
            session={careerVoiceSession}
            language={language}
            onProfileExtracted={
              handleProfileExtracted
            }
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

          <div className="workflow">
            <div className="workflow-step">
              <span className="step-number">
                1
              </span>

              <div>
                <h2>
                  {
                    text.app
                      .workflowProfileTitle
                  }
                </h2>

                <p>
                  {
                    text.app
                      .workflowProfileDescription
                  }
                </p>
              </div>
            </div>

            <div className="workflow-step">
              <span className="step-number">
                2
              </span>

              <div>
                <h2>
                  {
                    text.app
                      .workflowJobsTitle
                  }
                </h2>

                <p>
                  {
                    text.app
                      .workflowJobsDescription
                  }
                </p>
              </div>
            </div>

            <div className="workflow-step">
              <span className="step-number">
                3
              </span>

              <div>
                <h2>
                  {
                    text.app
                      .workflowRecommendationsTitle
                  }
                </h2>

                <p>
                  {
                    text.app
                      .workflowRecommendationsDescription
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default App