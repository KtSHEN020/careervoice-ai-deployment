import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from 'react'

import type { Session } from '@supabase/supabase-js'

import { ApiError } from '../api/client'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'
import {
  requestEmailOtp,
  signOutCurrentSession,
  verifyEmailOtp,
} from './authentication'
import {
  resolveCareerVoiceSession,
  type CareerVoiceSession,
} from './careervoice-session'
import { getCurrentSession } from './session'

const OTP_RESEND_COOLDOWN_SECONDS = 60

interface AuthPanelProps {
  language: AppLanguage
  onSessionChange: (
    session: CareerVoiceSession | null,
  ) => void
}

type AuthStage =
  | 'checking'
  | 'email'
  | 'code'
  | 'denied'
  | 'unavailable'

type AuthError =
  | 'expired'
  | 'initialize'
  | 'sendCode'
  | 'verifyCode'
  | 'denied'
  | 'unavailable'
  | 'verifyAccount'
  | 'signOut'
  | null

function authorizationError(
  error: unknown,
): Exclude<
  AuthError,
  'initialize'
  | 'sendCode'
  | 'verifyCode'
  | 'signOut'
  | null
> {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return 'expired'
    }

    if (error.status === 403) {
      return 'denied'
    }

    if (error.status === 503) {
      return 'unavailable'
    }
  }

  return 'verifyAccount'
}

export function AuthPanel({
  language,
  onSessionChange,
}: AuthPanelProps) {
  const text = UI_TEXT[language].auth

  const [stage, setStage] =
    useState<AuthStage>('checking')

  const [email, setEmail] =
    useState('')

  const [code, setCode] =
    useState('')

  const [
    pendingSession,
    setPendingSession,
  ] = useState<Session | null>(null)

  const [
    isSubmitting,
    setIsSubmitting,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<AuthError>(null)

  const [
    codeSent,
    setCodeSent,
  ] = useState(false)

  const [
    resendCooldown,
    setResendCooldown,
  ] = useState(0)

  function errorMessage(): string {
    if (error === null) {
      return ''
    }

    if (error === 'expired') {
      return text.errors.expired
    }

    if (error === 'initialize') {
      return text.errors.initialize
    }

    if (error === 'sendCode') {
      return text.errors.sendCode
    }

    if (error === 'verifyCode') {
      return text.errors.verifyCode
    }

    if (error === 'denied') {
      return text.errors.denied
    }

    if (error === 'unavailable') {
      return text.errors.unavailable
    }

    if (error === 'signOut') {
      return text.errors.signOut
    }

    return text.errors.verifyAccount
  }

  const authorizeSession = useCallback(
    async (
      supabaseSession: Session,
    ) => {
      setPendingSession(
        supabaseSession,
      )

      setError(null)

      try {
        const careerVoiceSession =
          await resolveCareerVoiceSession(
            supabaseSession,
          )

        setPendingSession(null)

        onSessionChange(
          careerVoiceSession,
        )
      } catch (authorizationFailure) {
        const nextError =
          authorizationError(
            authorizationFailure,
          )

        setError(nextError)

        if (nextError === 'expired') {
          try {
            await signOutCurrentSession()
          } catch {
            // The local session is already unusable.
            // Continue back to the login screen.
          }

          setPendingSession(null)
          setStage('email')
          onSessionChange(null)
          return
        }

        if (nextError === 'denied') {
          setStage('denied')
          onSessionChange(null)
          return
        }

        setStage('unavailable')
        onSessionChange(null)
      }
    },
    [onSessionChange],
  )

  useEffect(() => {
    let active = true

    async function restoreSession() {
      try {
        const session =
          await getCurrentSession()

        if (!active) {
          return
        }

        if (session === null) {
          setStage('email')
          onSessionChange(null)
          return
        }

        await authorizeSession(
          session,
        )
      } catch {
        if (!active) {
          return
        }

        setError('initialize')
        setStage('email')
        onSessionChange(null)
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

  useEffect(() => {
    if (resendCooldown <= 0) {
      return
    }

    const timer = window.setTimeout(() => {
      setResendCooldown(
        (current) =>
          Math.max(0, current - 1),
      )
    }, 1000)

    return () => {
      window.clearTimeout(timer)
    }
  }, [resendCooldown])

  async function handleRequestCode(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setError(null)
    setCodeSent(false)

    const normalizedEmail =
      email.trim()

    if (!normalizedEmail) {
      setError('sendCode')
      return
    }

    setIsSubmitting(true)

    try {
      await requestEmailOtp(
        normalizedEmail,
      )

      setEmail(normalizedEmail)
      setCode('')
      setCodeSent(true)
      setResendCooldown(
        OTP_RESEND_COOLDOWN_SECONDS,
      )
      setStage('code')
    } catch {
      setError('sendCode')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleVerifyCode(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setError(null)

    const normalizedCode =
      code.trim()

    if (!normalizedCode) {
      setError('verifyCode')
      return
    }

    setIsSubmitting(true)

    try {
      const session =
        await verifyEmailOtp(
          email,
          normalizedCode,
        )

      await authorizeSession(
        session,
      )
    } catch {
      setError('verifyCode')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleResendCode() {
    if (
      isSubmitting
      || resendCooldown > 0
    ) {
      return
    }

    setError(null)
    setCodeSent(false)
    setIsSubmitting(true)

    try {
      await requestEmailOtp(email)

      setCode('')
      setCodeSent(true)

      setResendCooldown(
        OTP_RESEND_COOLDOWN_SECONDS,
      )
    } catch {
      setError('sendCode')
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleDifferentEmail() {
    setEmail('')
    setCode('')
    setCodeSent(false)
    setResendCooldown(0)
    setPendingSession(null)
    setError(null)
    setStage('email')
  }

  async function handleRetry() {
    setError(null)
    setIsSubmitting(true)

    try {
      let session =
        pendingSession

      if (session === null) {
        session =
          await getCurrentSession()
      }

      if (session === null) {
        setStage('email')
        onSessionChange(null)
        return
      }

      await authorizeSession(
        session,
      )
    } catch {
      setError('verifyAccount')
      setStage('unavailable')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleSignOut() {
    setError(null)
    setIsSubmitting(true)

    try {
      await signOutCurrentSession()

      setPendingSession(null)
      setEmail('')
      setCode('')
      setCodeSent(false)
      setResendCooldown(0)
      setStage('email')

      onSessionChange(null)
    } catch {
      setError('signOut')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (stage === 'checking') {
    return (
      <section className="auth-card">
        <p className="auth-status">
          {text.checking}
        </p>
      </section>
    )
  }

  if (stage === 'email') {
    return (
      <section className="auth-card">
        <p className="auth-kicker">
          {text.privateTesting}
        </p>

        <h2>
          {text.signInTitle}
        </h2>

        <p className="auth-copy">
          {text.approvedEmail}
        </p>

        <form
          className="auth-form"
          onSubmit={
            handleRequestCode
          }
        >
          <div className="auth-field">
            <label htmlFor="auth-email">
              {text.email}
            </label>

            <input
              id="auth-email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              disabled={isSubmitting}
              onChange={(event) => {
                setEmail(
                  event.target.value,
                )
              }}
              required
            />
          </div>

          {error !== null && (
            <p className="auth-message auth-message-error">
              {errorMessage()}
            </p>
          )}

          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? text.sending
              : text.sendCode}
          </button>
        </form>
      </section>
    )
  }

  if (stage === 'code') {
    return (
      <section className="auth-card">
        <p className="auth-kicker">
          {text.verification}
        </p>

        <h2>
          {text.enterCode}
        </h2>

        <p className="auth-copy">
          {text.codeSentTo}
          {' '}
          <strong>
            {email}
          </strong>
        </p>

        {codeSent && (
          <p className="auth-message auth-message-success">
            {text.codeSent}
          </p>
        )}

        <form
          className="auth-form"
          onSubmit={
            handleVerifyCode
          }
        >
          <div className="auth-field">
            <label htmlFor="auth-code">
              {text.code}
            </label>

            <input
              id="auth-code"
              name="code"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              value={code}
              disabled={isSubmitting}
              onChange={(event) => {
                setCode(
                  event.target.value,
                )
              }}
              required
            />
          </div>

          {error !== null && (
            <p className="auth-message auth-message-error">
              {errorMessage()}
            </p>
          )}

          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? text.verifying
              : text.verify}
          </button>
        </form>

        <div className="auth-resend-section">
          <div className="auth-resend-row">
            <span>
              {text.didntReceiveCode}
            </span>

            <button
              className="secondary-button"
              type="button"
              disabled={
                isSubmitting
                || resendCooldown > 0
              }
              onClick={() => {
                void handleResendCode()
              }}
            >
              {isSubmitting
                ? text.resending
                : text.resendCode}
            </button>
          </div>

          {resendCooldown > 0 && (
            <p className="auth-resend-note">
              {text.resendAvailableIn}
              {' '}
              {resendCooldown}
              {' '}
              {text.seconds}
            </p>
          )}

          <button
            className="secondary-button"
            type="button"
            disabled={isSubmitting}
            onClick={
              handleDifferentEmail
            }
          >
            {text.differentEmail}
          </button>
        </div>
      </section>
    )
  }

  if (stage === 'denied') {
    return (
      <section className="auth-card">
        <p className="auth-kicker">
          {text.accessUnavailable}
        </p>

        <h2>
          {text.accessNotEnabled}
        </h2>

        <p className="auth-message auth-message-error">
          {errorMessage()}
        </p>

        <button
          className="secondary-button"
          type="button"
          disabled={isSubmitting}
          onClick={() => {
            void handleSignOut()
          }}
        >
          {isSubmitting
            ? text.signingOut
            : text.signOut}
        </button>
      </section>
    )
  }

  return (
    <section className="auth-card">
      <p className="auth-kicker">
        {text.serviceUnavailable}
      </p>

      <h2>
        {text.verifyFailedTitle}
      </h2>

      {error !== null && (
        <p className="auth-message auth-message-error">
          {errorMessage()}
        </p>
      )}

      <div className="auth-actions">
        <button
          className="primary-button"
          type="button"
          disabled={isSubmitting}
          onClick={() => {
            void handleRetry()
          }}
        >
          {isSubmitting
            ? text.tryingAgain
            : text.tryAgain}
        </button>

        <button
          className="secondary-button"
          type="button"
          disabled={isSubmitting}
          onClick={() => {
            void handleSignOut()
          }}
        >
          {text.signOut}
        </button>
      </div>
    </section>
  )
}