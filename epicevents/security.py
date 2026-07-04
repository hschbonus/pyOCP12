from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def hash_password(plain_value: str) -> str:
    return ph.hash(plain_value)


def verify_password(hashed_value: str, plain_value: str) -> bool:
    try:
        ph.verify(hashed_value, plain_value)
        return True
    except VerifyMismatchError:
        return False
