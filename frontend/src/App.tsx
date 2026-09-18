import { useState } from 'react'

import './App.css'

import type { ProfileExtractionResponse } from './api/profile'
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
    usageRefreshKey,
    setUsageRefreshKey,
  ] = useState(0)

  const [signOutError, setSignOutError] =
    useState('')

  const text = UI_TEXT[language]

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

    setUsageRefreshKey(
      (current) => current + 1,
    )
  }

  async function handleSignOut() {
    setSignOutError('')

    try {
      await signOutCurrentSession()

      setCareerVoiceSession(null)
      setExtractedProfile(null)
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
              setCareerVoiceSession
            }
          />
        </section>
      </main>
    )
  }

  return (
    <main className="authenticated-shell">
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
      />

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
            <section className="profile-result-preview">
              <p className="profile-kicker">
                {text.app.profileExtracted}
              </p>

              <h2>
                {text.app.readyForReview}
              </h2>

              <p>
                {
                  extractedProfile.profile
                    .target_roles.length
                }
                {' '}
                {text.app.targetRoles}
                {' · '}
                {
                  extractedProfile.profile
                    .skills.length
                }
                {' '}
                {text.app.skillsIdentified}
              </p>
            </section>
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