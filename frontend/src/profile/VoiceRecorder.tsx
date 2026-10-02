import {
  useEffect,
  useRef,
  useState,
} from 'react'

import { ApiError } from '../api/client'
import {
  transcribeVoiceRecording,
} from '../api/profile'
import type { CareerVoiceSession } from '../auth/careervoice-session'
import {
  UI_TEXT,
  type AppLanguage,
} from '../i18n'

interface VoiceRecorderProps {
  session: CareerVoiceSession
  language: AppLanguage
  transcript: string
  disabled: boolean
  onTranscriptChange: (
    transcript: string,
  ) => void
  onUsageChanged: () => void
}

const VOICE_MEDIA_TYPES = [
  'audio/mp4;codecs=mp4a.40.2',
  'audio/mp4',
  'audio/webm;codecs=opus',
  'audio/webm',
]

function preferredVoiceMediaType(): string | null {
  if (
    typeof MediaRecorder === 'undefined'
  ) {
    return null
  }

  return (
    VOICE_MEDIA_TYPES.find(
      (mediaType) =>
        MediaRecorder.isTypeSupported(
          mediaType,
        ),
    )
    ?? null
  )
}

function recordingFilename(
  mediaType: string,
): string {
  const normalizedMediaType =
    mediaType
      .toLowerCase()
      .split(';', 1)[0]

  if (normalizedMediaType === 'audio/mp4') {
    return 'career-voice.mp4'
  }

  if (
    normalizedMediaType
    === 'audio/webm'
  ) {
    return 'career-voice.webm'
  }

  return 'career-voice.audio'
}

function transcriptionErrorMessage(
  error: unknown,
  language: AppLanguage,
): string {
  const errors =
    UI_TEXT[language].profile.voiceErrors

  if (error instanceof ApiError) {
    if (error.status === 401) {
      return errors.expired
    }

    if (error.status === 403) {
      return errors.denied
    }

    if (error.status === 413) {
      return errors.tooLarge
    }

    if (error.status === 422) {
      return errors.invalid
    }

    if (error.status === 429) {
      return errors.quota
    }

    if (error.status === 503) {
      return errors.unavailable
    }
  }

  return errors.generic
}

export function VoiceRecorder({
  session,
  language,
  transcript,
  disabled,
  onTranscriptChange,
  onUsageChanged,
}: VoiceRecorderProps) {
  const text =
    UI_TEXT[language].profile

  const mediaRecorderRef =
    useRef<MediaRecorder | null>(null)

  const mediaStreamRef =
    useRef<MediaStream | null>(null)

  const chunksRef =
    useRef<Blob[]>([])

  const [
    audioBlob,
    setAudioBlob,
  ] = useState<Blob | null>(null)

  const [
    audioUrl,
    setAudioUrl,
  ] = useState('')

  const [
    isRecording,
    setIsRecording,
  ] = useState(false)

  const [
    isTranscribing,
    setIsTranscribing,
  ] = useState(false)

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

  useEffect(() => {
    if (!audioUrl) {
        return
    }

    return () => {
        URL.revokeObjectURL(
        audioUrl,
        )
    }
    }, [audioUrl])

  useEffect(() => {
    return () => {
        const recorder =
        mediaRecorderRef.current

        if (
        recorder !== null
        && recorder.state !== 'inactive'
        ) {
        recorder.stop()
        }

        mediaStreamRef.current
        ?.getTracks()
        .forEach((track) => {
            track.stop()
        })
    }
    }, [])

  function replaceAudioUrl(
    blob: Blob,
  ) {
    setAudioUrl(
      URL.createObjectURL(blob),
    )
  }

  async function handleStartRecording() {
    setErrorMessage('')

    if (
      !navigator.mediaDevices
      || !navigator.mediaDevices.getUserMedia
      || typeof MediaRecorder
        === 'undefined'
    ) {
      setErrorMessage(
        text.voiceErrors.unsupported,
      )

      return
    }

    const mediaType =
      preferredVoiceMediaType()

    if (mediaType === null) {
      setErrorMessage(
        text.voiceErrors.unsupported,
      )

      return
    }

    try {
      const stream =
        await navigator.mediaDevices
            .getUserMedia({
            audio: true,
            })

      mediaStreamRef.current =
      stream

      chunksRef.current = []

      setAudioUrl('')
      setAudioBlob(null)
      onTranscriptChange('')

      const recorder =
        new MediaRecorder(
          stream,
          {
            mimeType: mediaType,
          },
        )

      mediaRecorderRef.current =
        recorder

      recorder.addEventListener(
        'dataavailable',
        (event) => {
          if (event.data.size > 0) {
            chunksRef.current.push(
              event.data,
            )
          }
        },
      )

      recorder.addEventListener(
        'stop',
        () => {
          const blob =
            new Blob(
              chunksRef.current,
              {
                type:
                  recorder.mimeType
                  || mediaType,
              },
            )

          mediaStreamRef.current
            ?.getTracks()
            .forEach((track) => {
              track.stop()
            })

          mediaStreamRef.current =
            null

          mediaRecorderRef.current =
            null

          setAudioBlob(blob)
          replaceAudioUrl(blob)
          setIsRecording(false)
        },
      )

      recorder.start()
      setIsRecording(true)
    } catch {
      setErrorMessage(
        text.voiceErrors.microphone,
      )
    }
  }

  function handleStopRecording() {
    const recorder =
      mediaRecorderRef.current

    if (
      recorder !== null
      && recorder.state !== 'inactive'
    ) {
      recorder.stop()
    }
  }

  async function handleTranscribe() {
    if (audioBlob === null) {
      setErrorMessage(
        text.voiceErrors.noRecording,
      )

      return
    }

    setErrorMessage('')
    setIsTranscribing(true)

    try {
      const mediaType =
        audioBlob.type

      const result =
        await transcribeVoiceRecording(
          session.supabaseSession
            .access_token,
          {
            recording: audioBlob,
            filename:
              recordingFilename(
                mediaType,
              ),
            output_language:
              language,
          },
        )

      onTranscriptChange(
        result.text,
      )

      onUsageChanged()
    } catch (error) {
      setErrorMessage(
        transcriptionErrorMessage(
          error,
          language,
        ),
      )
    } finally {
      setIsTranscribing(false)
    }
  }

  return (
    <div className="profile-field">
      <span className="profile-field-label">
        {text.voiceRecording}
      </span>

      <p className="profile-help">
        {text.voiceHelp}
      </p>

      <div className="voice-recording-actions">
        {!isRecording ? (
          <button
            className="secondary-button"
            type="button"
            disabled={
              disabled
              || isTranscribing
            }
            onClick={() => {
              void handleStartRecording()
            }}
          >
            {text.startRecording}
          </button>
        ) : (
          <button
            className="secondary-button"
            type="button"
            onClick={
              handleStopRecording
            }
          >
            {text.stopRecording}
          </button>
        )}

        {isRecording && (
          <span
            className="voice-recording-status"
            role="status"
          >
            {text.recording}
          </span>
        )}
      </div>

      {audioUrl && (
        <>
          <audio
            className="voice-recording-player"
            controls
            src={audioUrl}
          />

          <button
            className="secondary-button voice-transcribe-button"
            type="button"
            disabled={
              disabled
              || isRecording
              || isTranscribing
            }
            onClick={() => {
              void handleTranscribe()
            }}
          >
            {isTranscribing
              ? text.transcribingVoice
              : text.transcribeVoice}
          </button>
        </>
      )}

      {errorMessage && (
        <p
          className="profile-message profile-message-error"
          role="alert"
        >
          {errorMessage}
        </p>
      )}

      <label htmlFor="voice-transcript">
        {text.voiceTranscript}
      </label>

      <textarea
        id="voice-transcript"
        name="voice-transcript"
        rows={7}
        value={transcript}
        maxLength={12_000}
        disabled={
          disabled
          || isTranscribing
        }
        placeholder={
          text.voiceTranscriptPlaceholder
        }
        onChange={(event) => {
          onTranscriptChange(
            event.target.value,
          )
        }}
      />

      <div className="profile-character-count">
        {transcript.length.toLocaleString()}
        {' / '}
        {(12_000) .toLocaleString()}
      </div>
    </div>
  )
}