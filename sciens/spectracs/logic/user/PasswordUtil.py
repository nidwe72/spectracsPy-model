import bcrypt


class PasswordUtil:
    """bcrypt password hashing/verification. Server-side only — a hash never leaves the server."""

    def hash(self, plainPassword: str) -> str:
        passwordBytes = plainPassword.encode("utf-8")
        hashBytes = bcrypt.hashpw(passwordBytes, bcrypt.gensalt())
        return hashBytes.decode("utf-8")

    def verify(self, plainPassword: str, passwordHash: str) -> bool:
        if plainPassword is None or passwordHash is None:
            return False
        try:
            return bcrypt.checkpw(plainPassword.encode("utf-8"), passwordHash.encode("utf-8"))
        except (ValueError, TypeError):
            return False
