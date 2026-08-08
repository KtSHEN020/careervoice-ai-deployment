from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

DEFAULT_SESSION_ROOT = Path("runtime/sessions")


def _normalize_session_id(value: str) -> str:
    """
    Validate and normalize a session identifier as a UUID.

    Requiring UUID identifiers prevents path traversal values such as
    '../other-directory' from being used as session directory names.
    """
    try:
        return str(UUID(value))
    except (AttributeError, TypeError, ValueError) as error:
        raise ValueError("session_id must be a valid UUID.") from error


@dataclass(frozen=True)
class SessionWorkspace:
    """
    File workspace owned by one web application session.
    """

    session_id: str
    root_dir: Path = DEFAULT_SESSION_ROOT

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "session_id",
            _normalize_session_id(self.session_id),
        )
        object.__setattr__(self, "root_dir", Path(self.root_dir))

    @classmethod
    def create(
        cls,
        *,
        root_dir: str | Path = DEFAULT_SESSION_ROOT,
    ) -> SessionWorkspace:
        """
        Create a workspace with a new unique session identifier.
        """
        workspace = cls(
            session_id=str(uuid4()),
            root_dir=Path(root_dir),
        )
        workspace.ensure_exists()
        return workspace

    @classmethod
    def from_session_id(
        cls,
        session_id: str,
        *,
        root_dir: str | Path = DEFAULT_SESSION_ROOT,
    ) -> SessionWorkspace:
        """
        Open or recreate the workspace for an existing session identifier.
        """
        workspace = cls(
            session_id=session_id,
            root_dir=Path(root_dir),
        )
        workspace.ensure_exists()
        return workspace

    @property
    def directory(self) -> Path:
        """Return the session-specific directory."""
        return self.root_dir / self.session_id

    @property
    def profile_input_path(self) -> Path:
        """Return the text input path used by Repo 1."""
        return self.directory / "profile_input.txt"

    @property
    def profile_path(self) -> Path:
        """Return the structured career profile path."""
        return self.directory / "career_profile.json"

    @property
    def jobs_output_path(self) -> Path:
        """Return the collected jobs path."""
        return self.directory / "jobs.json"

    @property
    def recommendations_output_path(self) -> Path:
        """Return the recommendation output path."""
        return self.directory / "recommendations.json"

    @property
    def generated_paths(self) -> tuple[Path, ...]:
        """Return all files generated during one web workflow."""
        return (
            self.profile_input_path,
            self.profile_path,
            self.jobs_output_path,
            self.recommendations_output_path,
        )

    def ensure_exists(self) -> Path:
        """Create the session directory when it does not exist."""
        self.directory.mkdir(parents=True, exist_ok=True)
        return self.directory

    def clear(self) -> None:
        """
        Remove only this session's workspace.

        The resolved-path check prevents deletion outside the configured
        session root.
        """
        if not self.directory.exists():
            return

        resolved_root = self.root_dir.resolve()
        resolved_directory = self.directory.resolve()

        if resolved_directory.parent != resolved_root:
            raise RuntimeError(
                "Refusing to remove a directory outside the session root."
            )

        shutil.rmtree(self.directory)