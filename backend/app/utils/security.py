from datetime import datetime, timedelta, UTC

from jose import jwt
from passlib.context import CryptContext


# -----------------------------
# Password Hashing Configuration
# -----------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# -----------------------------
# JWT Configuration
# -----------------------------

SECRET_KEY = "your-secret-key-change-this"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# -----------------------------
# Password Functions
# -----------------------------

def hash_password(password: str):
    return pwd_context.hash(password)



def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# -----------------------------
# Create JWT Token
# -----------------------------

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "exp": expire
        }
    )


    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt



# -----------------------------
# Decode JWT Token
# -----------------------------

def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload


    except Exception:

        return None