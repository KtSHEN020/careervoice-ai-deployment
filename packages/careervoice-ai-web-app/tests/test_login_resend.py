from careervoice_ai_web_app.login_resend import (
    OTP_RESEND_COOLDOWN_SECONDS,
    remaining_resend_seconds,
)


def test_no_previous_request_allows_resend() -> None:
    assert (
        remaining_resend_seconds(
            None,
            now=100.0,
        )
        == 0
    )


def test_resend_cooldown_starts_at_sixty_seconds() -> None:
    assert (
        remaining_resend_seconds(
            100.0,
            now=100.0,
        )
        == OTP_RESEND_COOLDOWN_SECONDS
    )


def test_resend_cooldown_counts_down() -> None:
    assert (
        remaining_resend_seconds(
            100.0,
            now=118.2,
        )
        == 42
    )


def test_resend_allowed_after_sixty_seconds() -> None:
    assert (
        remaining_resend_seconds(
            100.0,
            now=160.0,
        )
        == 0
    )


def test_invalid_saved_timestamp_does_not_block_resend() -> None:
    assert (
        remaining_resend_seconds(
            "invalid",
            now=100.0,
        )
        == 0
    )


def test_future_timestamp_uses_full_cooldown() -> None:
    assert (
        remaining_resend_seconds(
            200.0,
            now=100.0,
        )
        == OTP_RESEND_COOLDOWN_SECONDS
    )