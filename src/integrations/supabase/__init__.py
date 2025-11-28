import os
from datetime import datetime, timezone

import jwt
from jwt import InvalidTokenError

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
SUPABASE_JWT_AUDIENCE = os.environ.get("SUPABASE_JWT_AUDIENCE", "authenticated")


class SupabaseUser:
    def __init__(self, user_id: str, raw_claims: dict):
        self.id = user_id
        self.claims = raw_claims

    def __repr__(self):
        return f"<SupabaseUser id={self.id}>"


def verify_supabase_token(token: str) -> SupabaseUser | None:
    """
    Valida o JWT emitido pelo Supabase.
    Retorna SupabaseUser se ok, ou None se inválido.
    """
    if not SUPABASE_JWT_SECRET:
        raise RuntimeError("SUPABASE_JWT_SECRET não configurado no ambiente")

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],  # Supabase antigo usa HS256 com JWT_SECRET
            audience=SUPABASE_JWT_AUDIENCE,  # se não usar 'aud', pode remover
            options={"verify_aud": False},  # desliga se seu token não tiver 'aud'
        )
    except InvalidTokenError:
        return None

    # Verificação de expiração manual (se quiser garantir)
    exp = payload.get("exp")
    if exp is not None:
        now = datetime.now(timezone.UTC).timestamp()
        if now > exp:
            return None

    # No Supabase, normalmente o ID do user está em 'sub'
    user_id = payload.get("sub")
    if not user_id:
        return None

    return SupabaseUser(user_id=user_id, raw_claims=payload)
