import { useEffect, useState } from 'react'

import './App.css'
import { getHealth } from './api/health'
import { getCurrentSession } from './auth/session'
import { AuthPanel } from './auth/AuthPanel'
import type { CareerVoiceSession } from './auth/careervoice-session'
import { UsageSummary } from './usage/UsageSummary'

type ServiceStatus = 'checking' | 'connected' | 'unavailable'

function App() {
  const [serviceStatus, setServiceStatus] =
    useState<ServiceStatus>('checking')
  const [
    careerVoiceSession,
    setCareerVoiceSession,
  ] = useState<CareerVoiceSession | null>(null)

  useEffect(() => {
    let active = true

    async function checkService() {
      try {
        const health = await getHealth()

        if (health.status !== 'ok') {
          if (active) {
            setServiceStatus('unavailable')
          }

          return
        }

        await getCurrentSession()

        if (active) {
          setServiceStatus('connected')
        }
      } catch {
        if (active) {
          setServiceStatus('unavailable')
        }
      }
    }

    void checkService()

    return () => {
      active = false
    }
  }, [])

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="top-line">
          <p className="eyebrow">CareerVoice AI</p>

          <p
            className={`service-status service-status-${serviceStatus}`}
            aria-live="polite"
          >
            {serviceStatus === 'checking' && 'Connecting…'}
            {serviceStatus === 'connected' && 'Service ready'}
            {serviceStatus === 'unavailable' && 'Service unavailable'}
          </p>
        </div>

        <h1>Find roles that fit your career goals</h1>

        <p className="hero-description">
          Build your career profile, search for relevant jobs, and get
          personalized recommendations based on your skills and preferences.
        </p>

        <AuthPanel
          onSessionChange={setCareerVoiceSession}
        />

        {careerVoiceSession !== null && (
          <UsageSummary
            session={careerVoiceSession}
          />
        )}

        <div className="workflow">
          <div className="workflow-step">
            <span className="step-number">1</span>
            <div>
              <h2>Build your career profile</h2>
              <p>Tell us about your skills, preferences, and career goals.</p>
            </div>
          </div>

          <div className="workflow-step">
            <span className="step-number">2</span>
            <div>
              <h2>Search for jobs</h2>
              <p>Search across the roles and locations you are interested in.</p>
            </div>
          </div>

          <div className="workflow-step">
            <span className="step-number">3</span>
            <div>
              <h2>Get personalized recommendations</h2>
              <p>
                Compare jobs using match explanations, missing skills, and
                preference-aware scoring.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default App