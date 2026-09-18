"""Passwords and login tokens."""
import hashlib
import hmac
import os
import time

from app import db

SECRET = os.environ.get("SHOP_SECRET", "")


def hash_password(password, salt):
    data = (salt + password).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def check_password(password, salt, expected_hash):
    actual = hash_password(password, salt)
    return hmac.compare_digest(actual, expected_hash)


def token_is_valid(expires_at, now=None):
    if now is None:
        now = time.time()
    return now < expires_at


def login(conn, email, password):
    user = db.find_user_by_email(conn, email)
    if user is None:
        return False
    return check_password(password, user["salt"], user["password_hash"])
