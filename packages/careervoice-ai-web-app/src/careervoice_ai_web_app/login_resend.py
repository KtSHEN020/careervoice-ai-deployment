"""Timing rules for resending email login codes."""

from __future__ import annotations

import math

OTP_RESEND_COOLDOWN_SECONDS = 60


def remaining_resend_seconds(
    sent_at: object,
    *,
    now: float,
) -> int:
    """Return whole seconds before another login code may be requested."""
    if (
        not isinstance(sent_at, (int, float))
        or isinstance(sent_at, bool)
    ):
        return 0

    elapsed = max(
        0.0,
        now - float(sent_at),
    )

    remaining = (
        OTP_RESEND_COOLDOWN_SECONDS
        - elapsed
    )

    return max(
        0,
        math.ceil(remaining),
    )