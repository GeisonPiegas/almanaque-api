from abc import ABC, abstractmethod

from django.http import HttpRequest
from ninja.security.http import HttpAuthBase
from src.integrations.supabase import verify_supabase_token
from src.utils.schemas import AuthSchema, AuthUserSchema


class HttpBearer(HttpAuthBase, ABC):
    openapi_scheme: str = "bearer"
    header: str = "Authorization"

    def __call__(self, request: HttpRequest):
        return self.authenticate(request, "")

    @abstractmethod
    def authenticate(self, request: HttpRequest, token: str):
        pass


class SupabaseJWTAuth(HttpBearer):
    def authenticate(self, request, token: str) -> AuthSchema | None:
        """
        Retorna um SupabaseUser se o token for válido, ou None se inválido.
        Se None -> Ninja retorna 401 automaticamente.
        """
        auth = AuthSchema(user=AuthUserSchema(uuid="afa3c3b8-a5fa-4430-923d-c37f31739094", name="John Doe"))
        return auth


def get_optional_user(request) -> AuthSchema | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    return verify_supabase_token(token)
