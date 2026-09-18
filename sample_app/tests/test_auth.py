from app import auth


def test_password_round_trip():
    hashed = auth.hash_password("correct horse", "s1")
    assert auth.check_password("correct horse", "s1", hashed)
    assert not auth.check_password("wrong", "s1", hashed)


def test_token_expiry():
    assert auth.token_is_valid(expires_at=200, now=100)
    assert not auth.token_is_valid(expires_at=100, now=200)
