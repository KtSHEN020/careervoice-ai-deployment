from types import SimpleNamespace

import pytest

from careervoice_ai_web_app.authentication import (
    AuthenticationError,
    AuthenticationSession,
    AuthenticationSessionExpiredError,
    InvalidLoginCodeError,
)
from careervoice_ai_web_app.supabase_authentication import (
    SupabaseAuthenticationService,
)
from careervoice_ai_web_app.user_models import AuthenticatedIdentity


def _response(
    *,
    email: str = "tester@example.com",
    subject: str = "auth-user-123",
    access_token: str = "access-token",
    refresh_token: str = "refresh-token",
    expires_at: int = 1_800_000_000,
) -> object:
    user = SimpleNamespace(
        id=subject,
        email=email,
    )

    session = SimpleNamespace(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )

    return SimpleNamespace(
        user=user,
        session=session,
    )


class FakeAuthClient:
    def __init__(self) -> None:
        self.otp_credentials: dict[str, object] | None = None
        self.verify_params: dict[str, object] | None = None
        self.refresh_token: str | None = None
        self.set_session_tokens: tuple[str, str] | None = None
        self.sign_out_options: dict[str, str] | None = None

        self.verify_response = _response()
        self.refresh_response = _response(
            access_token="refreshed-access-token",
            refresh_token="refreshed-refresh-token",
        )

        self.failures: dict[str, Exception] = {}

        self.access_token: str | None = None

        self.get_user_response = SimpleNamespace(
            user=SimpleNamespace(
                id="auth-user-123",
                email="tester@example.com",
            )
        )

    def _raise_if_configured(self, operation: str) -> None:
        failure = self.failures.get(operation)

        if failure is not None:
            raise failure

    def sign_in_with_otp(
        self,
        credentials: dict[str, object],
    ) -> object:
        self._raise_if_configured("sign_in_with_otp")
        self.otp_credentials = credentials
        return SimpleNamespace()

    def verify_otp(
        self,
        params: dict[str, object],
    ) -> object:
        self._raise_if_configured("verify_otp")
        self.verify_params = params
        return self.verify_response

    def get_user(
        self,
        jwt: str | None = None,
    ) -> object:
        self._raise_if_configured("get_user")
        self.access_token = jwt
        return self.get_user_response

    def refresh_session(
        self,
        refresh_token: str | None = None,
    ) -> object:
        self._raise_if_configured("refresh_session")
        self.refresh_token = refresh_token
        return self.refresh_response

    def set_session(
        self,
        access_token: str,
        refresh_token: str,
    ) -> object:
        self._raise_if_configured("set_session")
        self.set_session_tokens = (
            access_token,
            refresh_token,
        )
        return SimpleNamespace()

    def sign_out(
        self,
        options: dict[str, str] | None = None,
    ) -> object:
        self._raise_if_configured("sign_out")
        self.sign_out_options = options
        return None


def _service() -> tuple[
    SupabaseAuthenticationService,
    FakeAuthClient,
]:
    auth_client = FakeAuthClient()

    return (
        SupabaseAuthenticationService(auth_client),
        auth_client,
    )


def _session() -> AuthenticationSession:
    return AuthenticationSession(
        identity=AuthenticatedIdentity(
            provider="supabase",
            subject="auth-user-123",
            email="tester@example.com",
        ),
        access_token="access-token",
        refresh_token="refresh-token",
        expires_at=1_800_000_000,
    )


def test_authenticate_access_token_returns_identity() -> None:
    service, auth_client = _service()

    identity = service.authenticate_access_token(
        "  access-token  "
    )

    assert auth_client.access_token == "access-token"

    assert identity == AuthenticatedIdentity(
        provider="supabase",
        subject="auth-user-123",
        email="tester@example.com",
    )


def test_authenticate_access_token_wraps_provider_failure() -> None:
    service, auth_client = _service()

    auth_client.failures["get_user"] = RuntimeError(
        "Invalid JWT"
    )

    with pytest.raises(
        AuthenticationError,
        match="invalid or expired",
    ):
        service.authenticate_access_token(
            "invalid-token"
        )


def test_authenticate_access_token_rejects_missing_user() -> None:
    service, auth_client = _service()

    auth_client.get_user_response = SimpleNamespace(
        user=None
    )

    with pytest.raises(
        AuthenticationError,
        match="invalid user",
    ):
        service.authenticate_access_token(
            "access-token"
        )


def test_request_login_code_disables_account_creation() -> None:
    service, auth_client = _service()

    service.request_login_code(
        "  Tester@Example.COM  "
    )

    assert auth_client.otp_credentials == {
        "email": "tester@example.com",
        "options": {
            "should_create_user": False,
        },
    }


def test_request_login_code_hides_provider_failure() -> None:
    service, auth_client = _service()

    auth_client.failures["sign_in_with_otp"] = RuntimeError(
        "User not found"
    )

    with pytest.raises(
        AuthenticationError,
        match="Unable to request a login code",
    ):
        service.request_login_code("unknown@example.com")


def test_verify_login_code_returns_careervoice_session() -> None:
    service, auth_client = _service()

    session = service.verify_login_code(
        email="Tester@Example.com",
        code=" 123456 ",
    )

    assert auth_client.verify_params == {
        "email": "tester@example.com",
        "token": "123456",
        "type": "email",
    }

    assert session.identity.provider == "supabase"
    assert session.identity.subject == "auth-user-123"
    assert session.identity.email == "tester@example.com"
    assert session.access_token == "access-token"
    assert session.refresh_token == "refresh-token"
    assert session.expires_at == 1_800_000_000


def test_verify_login_code_rejects_empty_code() -> None:
    service, _ = _service()

    with pytest.raises(
        InvalidLoginCodeError,
        match="cannot be empty",
    ):
        service.verify_login_code(
            email="tester@example.com",
            code="   ",
        )


def test_verify_login_code_wraps_provider_failure() -> None:
    service, auth_client = _service()

    auth_client.failures["verify_otp"] = RuntimeError(
        "Token expired"
    )

    with pytest.raises(
        InvalidLoginCodeError,
        match="invalid or expired",
    ):
        service.verify_login_code(
            email="tester@example.com",
            code="123456",
        )


def test_verify_login_code_rejects_mismatched_email() -> None:
    service, auth_client = _service()

    auth_client.verify_response = _response(
        email="someone-else@example.com"
    )

    with pytest.raises(
        AuthenticationError,
        match="does not match",
    ):
        service.verify_login_code(
            email="tester@example.com",
            code="123456",
        )


def test_refresh_session_uses_refresh_token() -> None:
    service, auth_client = _service()

    refreshed = service.refresh_session(
        _session()
    )

    assert auth_client.refresh_token == "refresh-token"
    assert refreshed.access_token == "refreshed-access-token"
    assert refreshed.refresh_token == "refreshed-refresh-token"


def test_refresh_session_requires_refresh_token() -> None:
    service, _ = _service()

    session = AuthenticationSession(
        identity=_session().identity,
        access_token="access-token",
    )

    with pytest.raises(
        AuthenticationSessionExpiredError,
        match="cannot be refreshed",
    ):
        service.refresh_session(session)


def test_refresh_session_wraps_provider_failure() -> None:
    service, auth_client = _service()

    auth_client.failures["refresh_session"] = RuntimeError(
        "Invalid refresh token"
    )

    with pytest.raises(
        AuthenticationSessionExpiredError,
        match="has expired",
    ):
        service.refresh_session(_session())


def test_sign_out_uses_current_session_only() -> None:
    service, auth_client = _service()

    service.sign_out(_session())

    assert auth_client.set_session_tokens == (
        "access-token",
        "refresh-token",
    )

    assert auth_client.sign_out_options == {
        "scope": "local",
    }