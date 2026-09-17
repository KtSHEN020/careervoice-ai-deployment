import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from 'react'
import type { Session } from '@supabase/supabase-js'

import { ApiError } from '../api/client'
import type { CurrentUser } from '../api/me'
import {
  resolveCareerVoiceSession,
  type CareerVoiceSession,
} from './careervoice-session'
import {
  requestEmailOtp,
  signOutCurrentSession,
  verifyEmailOtp,
} from './authentication'
import { getCurrentSession } from './session'

type AuthStage =
  | 'loading'
  | 'email'
  | 'otp'
  | 'authenticated'
  | 'denied'
  | 'unavailable'

interface AuthPanelProps {
  onSessionChange: (
    session: CareerVoiceSession | null,
  ) => void
}

function getSessionEmail(session: Session | null): string {
  return session?.user.email ?? ''
}

function authorizationMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return 'Your sign-in session is no longer valid. Please sign in again.'
    }

    if (error.status === 403) {
      return 'This account is not currently approved to use CareerVoice.'
    }

    if (error.status === 503) {
      return 'CareerVoice is temporarily unavailable. Please try again shortly.'
    }
  }

  return 'CareerVoice could not verify your account. Please try again.'
}

export function AuthPanel({
  onSessionChange,
}: AuthPanelProps) {
  const [stage, setStage] = useState<AuthStage>('loading')

  const [session, setSession] = useState<Session | null>(null)
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)

  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')

  const [errorMessage, setErrorMessage] = useState('')
  const [statusMessage, setStatusMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const authorizeSession = useCallback(
    async (
        authenticatedSession: Session,
    ): Promise<boolean> => {
        try {
        const careerVoiceSession =
            await resolveCareerVoiceSession(
            authenticatedSession,
            )

        setSession(
            careerVoiceSession.supabaseSession,
        )
        setCurrentUser(
            careerVoiceSession.user,
        )
        setEmail(
            careerVoiceSession.user.email,
        )
        setErrorMessage('')
        setStage('authenticated')

        onSessionChange(
            careerVoiceSession,
        )

        return true
        } catch (error) {
        setSession(authenticatedSession)
        setCurrentUser(null)
        setErrorMessage(
            authorizationMessage(error),
        )

        onSessionChange(null)

        if (error instanceof ApiError) {
            if (error.status === 401) {
            await signOutCurrentSession()

            setSession(null)
            setEmail('')
            setCode('')
            setStage('email')

            return false
            }

            if (error.status === 403) {
            setStage('denied')
            return false
            }

            if (error.status === 503) {
            setStage('unavailable')
            return false
            }
        }

        setStage('unavailable')
        return false
        }
    },
    [onSessionChange],
    )

  useEffect(() => {
    let active = true

    async function restoreSession() {
      try {
        const restoredSession = await getCurrentSession()

        if (!active) {
          return
        }

        if (restoredSession === null) {
            onSessionChange(null)
            setStage('email')
            return
        }

        setSession(restoredSession)
        setEmail(getSessionEmail(restoredSession))

        await authorizeSession(restoredSession)
      } catch {
        if (!active) {
          return
        }

        setErrorMessage(
          'Authentication could not be initialized. Please refresh and try again.',
        )
        setStage('email')
      }
    }

    void restoreSession()

    return () => {
      active = false
    }
    }, [
        authorizeSession,
        onSessionChange,
    ])

  async function handleRequestCode(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setErrorMessage('')
    setStatusMessage('')
    setIsSubmitting(true)

    try {
      await requestEmailOtp(email)

      setStatusMessage(
        'A verification code has been sent to your email.',
      )
      setStage('otp')
    } catch {
      setErrorMessage(
        'A verification code could not be sent. Check the email address and try again.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleVerifyCode(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setErrorMessage('')
    setStatusMessage('')
    setIsSubmitting(true)

    try {
      const authenticatedSession = await verifyEmailOtp(
        email,
        code,
      )

      setSession(authenticatedSession)

      const authorized = await authorizeSession(
        authenticatedSession,
      )

      if (authorized) {
        setCode('')
      }
    } catch {
      setErrorMessage(
        'The verification code could not be confirmed. Check the code and try again.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleSignOut() {
    setErrorMessage('')
    setStatusMessage('')
    setIsSubmitting(true)

    try {
      await signOutCurrentSession()

      onSessionChange(null)

      setSession(null)
      setCurrentUser(null)
      setEmail('')
      setCode('')
      setStage('email')
    } catch {
      setErrorMessage(
        'Sign out failed. Please try again.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleRetryAuthorization() {
    if (session === null) {
      setStage('email')
      return
    }

    setErrorMessage('')
    setIsSubmitting(true)

    try {
      await authorizeSession(session)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (stage === 'loading') {
    return (
      <section className="auth-card" aria-live="polite">
        <p className="auth-status">
          Checking your session…
        </p>
      </section>
    )
  }

  if (stage === 'authenticated') {
    return (
      <section className="auth-card">
        <div className="auth-heading">
          <div>
            <p className="auth-kicker">
              Signed in
            </p>
            <h2>Welcome back</h2>
          </div>
        </div>

        <p className="auth-copy">
          You are signed in as{' '}
          <strong>
            {currentUser?.email ?? getSessionEmail(session)}
          </strong>.
        </p>

        {errorMessage && (
          <p className="auth-message auth-message-error">
            {errorMessage}
          </p>
        )}

        <button
          className="secondary-button"
          type="button"
          disabled={isSubmitting}
          onClick={() => {
            void handleSignOut()
          }}
        >
          {isSubmitting ? 'Signing out…' : 'Sign out'}
        </button>
      </section>
    )
  }

  if (stage === 'denied') {
    return (
      <section className="auth-card">
        <div className="auth-heading">
          <div>
            <p className="auth-kicker">
              Access unavailable
            </p>
            <h2>CareerVoice access is not enabled</h2>
          </div>
        </div>

        <p className="auth-copy">
          {errorMessage}
        </p>

        <button
          className="secondary-button"
          type="button"
          disabled={isSubmitting}
          onClick={() => {
            void handleSignOut()
          }}
        >
          {isSubmitting ? 'Signing out…' : 'Sign out'}
        </button>
      </section>
    )
  }

  if (stage === 'unavailable') {
    return (
      <section className="auth-card">
        <div className="auth-heading">
          <div>
            <p className="auth-kicker">
              Service unavailable
            </p>
            <h2>We could not verify your CareerVoice account</h2>
          </div>
        </div>

        <p className="auth-copy">
          {errorMessage}
        </p>

        <div className="auth-actions">
          <button
            className="primary-button"
            type="button"
            disabled={isSubmitting}
            onClick={() => {
              void handleRetryAuthorization()
            }}
          >
            {isSubmitting ? 'Trying again…' : 'Try again'}
          </button>

          <button
            className="secondary-button"
            type="button"
            disabled={isSubmitting}
            onClick={() => {
              void handleSignOut()
            }}
          >
            Sign out
          </button>
        </div>
      </section>
    )
  }

  if (stage === 'otp') {
    return (
      <section className="auth-card">
        <div className="auth-heading">
          <div>
            <p className="auth-kicker">
              Email verification
            </p>
            <h2>Enter your verification code</h2>
          </div>
        </div>

        <p className="auth-copy">
          We sent a verification code to{' '}
          <strong>{email}</strong>.
        </p>

        <form
          className="auth-form"
          onSubmit={handleVerifyCode}
        >
          <label htmlFor="verification-code">
            Verification code
          </label>

          <input
            id="verification-code"
            name="verification-code"
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            value={code}
            disabled={isSubmitting}
            onChange={(event) => {
              setCode(event.target.value)
            }}
            required
          />

          {statusMessage && (
            <p className="auth-message auth-message-success">
              {statusMessage}
            </p>
          )}

          {errorMessage && (
            <p className="auth-message auth-message-error">
              {errorMessage}
            </p>
          )}

          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Verifying…' : 'Verify code'}
          </button>

          <button
            className="text-button"
            type="button"
            disabled={isSubmitting}
            onClick={() => {
              setCode('')
              setErrorMessage('')
              setStatusMessage('')
              setStage('email')
            }}
          >
            Use a different email
          </button>
        </form>
      </section>
    )
  }

  return (
    <section className="auth-card">
      <div className="auth-heading">
        <div>
          <p className="auth-kicker">
            Private testing
          </p>
          <h2>Sign in to CareerVoice</h2>
        </div>
      </div>

      <p className="auth-copy">
        Enter your approved email address to receive a verification code.
      </p>

      <form
        className="auth-form"
        onSubmit={handleRequestCode}
      >
        <label htmlFor="email">
          Email address
        </label>

        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          disabled={isSubmitting}
          onChange={(event) => {
            setEmail(event.target.value)
          }}
          required
        />

        {errorMessage && (
          <p className="auth-message auth-message-error">
            {errorMessage}
          </p>
        )}

        <button
          className="primary-button"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Sending…' : 'Send verification code'}
        </button>
      </form>
    </section>
  )
}