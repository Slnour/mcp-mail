"""Inbound authorisation: restrict the server to specific GitHub accounts.

FastMCP's GitHubProvider proves *that* a caller holds a valid GitHub identity,
not that the identity is one we want. Without the check below, anyone with a
GitHub account could read the owner's health data.
"""

from __future__ import annotations

import logging

from fastmcp.exceptions import AuthorizationError
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class GitHubAllowlistMiddleware(Middleware):
    """Reject every message from a GitHub login outside the allowlist."""

    def __init__(self, allowed_logins: list[str]) -> None:
        # Compared case-insensitively: GitHub logins are case-preserving but
        # case-insensitive, so "PilarJ" and "pilarj" are the same account.
        self._allowed = {login.casefold() for login in allowed_logins}
        if not self._allowed:
            logger.warning(
                "ALLOWED_GITHUB_LOGINS is empty — every request will be denied."
            )

    async def on_message(self, context: MiddlewareContext, call_next):
        token = get_access_token()
        if token is None:
            raise AuthorizationError("Not authenticated.")

        login = (token.claims or {}).get("login")
        if not login or login.casefold() not in self._allowed:
            logger.warning("Denied GitHub login: %r", login)
            raise AuthorizationError("This account is not allowed to use this server.")

        return await call_next(context)
