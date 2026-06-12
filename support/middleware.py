from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token: str):
    try:
        access = AccessToken(token)
        return User.objects.get(pk=access["user_id"])
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware:
    """Authentification WebSocket via ?token=<JWT>"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token_list = query.get("token", [])
        if token_list:
            scope["user"] = await get_user_from_token(token_list[0])
        elif scope.get("user") is None:
            scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send)


def JWTAuthMiddlewareStack(app):
    from channels.auth import AuthMiddlewareStack

    return JWTAuthMiddleware(AuthMiddlewareStack(app))
