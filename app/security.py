import jwt
from config import settings
from errors import UnauthorizedError
from pydantic import ValidationError
from schemas import TokenData


def validate_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.security.public_key,
            algorithms=[settings.security.algorithm],
        )
        if not payload.get("type") == "access_token":
            raise UnauthorizedError
        sub = payload.get("sub")
        iss = payload.get("iss")
        username = payload.get("username")
        registered_at = payload.get("user_registered_at")
        if sub is None:
            raise UnauthorizedError
        return TokenData(
            sub=sub, iss=iss, username=username, user_registered_at=registered_at
        )
    except (jwt.InvalidTokenError, ValidationError, ValueError) as exc:
        raise UnauthorizedError from exc
