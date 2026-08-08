"""Runtime capability checks for the CareerVoice AI web application."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class CapabilityStatus:
    """Availability of external capabilities used by the web application."""

    openai_available: bool
    adzuna_available: bool

    @property
    def ai_features_available(self) -> bool:
        """Return whether AI-assisted features can be used."""
        return self.openai_available

    @property
    def job_collection_available(self) -> bool:
        """Return whether live job collection can be used."""
        return self.adzuna_available


def get_capability_status(
    environment: Mapping[str, str] | None = None,
) -> CapabilityStatus:
    """Determine which externally configured capabilities are available."""
    if environment is None:
        load_dotenv()
        env = os.environ
    else:
        env = environment

    openai_available = bool(
        env.get("OPENAI_API_KEY", "").strip()
    )

    adzuna_available = bool(
        env.get("ADZUNA_APP_ID", "").strip()
        and env.get("ADZUNA_APP_KEY", "").strip()
    )

    return CapabilityStatus(
        openai_available=openai_available,
        adzuna_available=adzuna_available,
    )