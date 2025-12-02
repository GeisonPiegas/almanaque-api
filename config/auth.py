from ninja.security.http import HttpBearer
from src.integrations.supabase import verify_supabase_token
from src.utils.schemas import AuthSchema


class SupabaseJWTAuth(HttpBearer):
    def authenticate(self, request, token: str) -> AuthSchema | None:
        """
        Retorna um SupabaseUser se o token for válido, ou None se inválido.
        Se None -> Ninja retorna 401 automaticamente.
        """
        return verify_supabase_token(token)


def get_optional_user(request) -> AuthSchema | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    return verify_supabase_token(token)
