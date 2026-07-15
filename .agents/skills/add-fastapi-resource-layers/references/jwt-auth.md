# Optional JWT authentication

Add authentication only when requested.

1. Add `PyJWT` and `pwdlib[argon2]` dependencies.
2. Store only password hashes. Accept plaintext passwords only in dedicated input schemas and exclude both plaintext and hashes from every response schema.
3. Add typed `jwt_secret_key`, `jwt_algorithm` (default `HS256`), and short access-token lifetime settings. Require a real secret through environment configuration.
4. Use `OAuth2PasswordBearer` to extract bearer tokens. Encode a stable subject identifier and expiration; decode with an explicit algorithm allowlist.
5. Resolve the current principal through a FastAPI dependency and attach it only to protected routers or endpoints.
6. Return the same 401 response for unknown users, bad passwords, expired tokens, and invalid tokens where practical. Never include secrets or tokens in logs.
7. Test valid login, invalid credentials, missing/malformed authorization, expiration, protected access, and response-field exclusion.

