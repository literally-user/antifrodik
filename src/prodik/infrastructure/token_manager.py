from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from prodik.application.common.token_manager import TokenManager, UserData
from prodik.domain.user.model import Role
from prodik.infrastructure.config import SecretConfig


@dataclass
class TokenManagerImpl(TokenManager):
    _config: SecretConfig

    def encode(self, uuid: UUID, role: Role, expires_in_seconds: int) -> str:
        now = datetime.now(tz=UTC)
        return jwt.encode(
            {
                "sub": str(uuid),
                "role": role,
                "iat": now,
                "exp": now + timedelta(seconds=expires_in_seconds),
            },
            self._config.secret,
            algorithm="HS256",
        )

    def decode(self, token: str) -> UserData:
        data = jwt.decode(token, self._config.secret, algorithms=["HS256"])
        return UserData(
            uuid=data["sub"],
            role=data["role"],
        )
