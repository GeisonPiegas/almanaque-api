from ninja.security import HttpBearer
from src.integrations.supabase import SupabaseUser, verify_supabase_token


class SupabaseJWTAuth(HttpBearer):
    def authenticate(self, request, token: str) -> SupabaseUser | None:
        """
        Retorna um SupabaseUser se o token for válido, ou None se inválido.
        Se None -> Ninja retorna 401 automaticamente.
        """
        user = verify_supabase_token(token)
        return user
