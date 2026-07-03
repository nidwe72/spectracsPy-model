class PasswordUtil:
    """bcrypt password hashing/verification. Server-side only — a hash never leaves the server.

    bcrypt (native, via cffi) is imported lazily so the CLIENT app, which imports this module
    transitively but never hashes/verifies (that happens server-side), doesn't need bcrypt/cffi
    bundled. The server APK, which actually calls these, lists bcrypt in its requirements.
    """

    def hash(self, plainPassword: str) -> str:
        import bcrypt
        passwordBytes = plainPassword.encode("utf-8")
        hashBytes = bcrypt.hashpw(passwordBytes, bcrypt.gensalt())
        return hashBytes.decode("utf-8")

    def verify(self, plainPassword: str, passwordHash: str) -> bool:
        if plainPassword is None or passwordHash is None:
            return False
        try:
            import bcrypt
            return bcrypt.checkpw(plainPassword.encode("utf-8"), passwordHash.encode("utf-8"))
        except (ValueError, TypeError):
            return False
