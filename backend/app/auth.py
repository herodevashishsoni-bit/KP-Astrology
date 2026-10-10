"""Single-user login: the first account created is the only account."""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .db import SessionLocal, User

def _secret() -> str:
    if os.environ.get("KP_SECRET"):
        return os.environ["KP_SECRET"]
    path = os.path.join(os.path.dirname(__file__), "..", ".secret")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    return open(path).read().strip()


SECRET = _secret()
_bearer = HTTPBearer(auto_error=False)


def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def check_pw(pw: str, h: str) -> bool:
    return bcrypt.checkpw(pw.encode(), h.encode())


def token_for(user: User) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": str(user.id), "exp": exp}, SECRET, algorithm="HS256")


def current_user(cred: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> User:
    if not cred:
        raise HTTPException(401, "Not logged in")
    try:
        data = jwt.decode(cred.credentials, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Session expired, please log in again")
    with SessionLocal() as s:
        u = s.get(User, int(data["sub"]))
        if not u:
            raise HTTPException(401, "Unknown user")
        s.expunge(u)
        return u
