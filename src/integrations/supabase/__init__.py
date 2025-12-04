import os
from datetime import datetime

import jwt
from django.utils.timezone import timezone
from jwt import InvalidTokenError

from src.apps.users.services import get_user
from src.utils.schemas import AuthSchema, AuthUserSchema

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
SUPABASE_JWT_AUDIENCE = os.environ.get("SUPABASE_JWT_AUDIENCE", "authenticated")


def verify_supabase_token(token: str) -> AuthSchema | None:
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
            algorithms=["HS256"],
            audience=SUPABASE_JWT_AUDIENCE,
            options={"verify_aud": False},
        )
    except InvalidTokenError:
        return None

    exp = payload.get("exp")
    if exp is not None:
        now = datetime.now(timezone.utc).timestamp()
        if now > exp:
            return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user_metadata = payload.get("user_metadata", {})
    user = get_user(
        user_id,
        user_metadata.get("full_name", None),
        user_metadata.get("email", None),
        user_metadata.get("avatar_url", None),
    )
    user_auth = None
    if user:
        user_auth = AuthUserSchema(uuid=user.uuid, name=user.name)

    return AuthSchema(user=user_auth)
