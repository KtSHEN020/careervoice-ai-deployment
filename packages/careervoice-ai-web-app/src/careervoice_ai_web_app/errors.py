from __future__ import annotations


class OrchestrationError(RuntimeError):
    """A web-safe error raised when Repo 4 cannot complete a workflow stage."""

    def __init__(
        self,
        *,
        stage: str,
        user_message: str,
        technical_details: str | None = None,
    ) -> None:
        self.stage = stage
        self.user_message = user_message
        self.technical_details = technical_details
        super().__init__(user_message)