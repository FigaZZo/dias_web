from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from models import Users
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from schemas import TokenData


SECRET_KEY = "very-secret-password"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def createAccessToken(data: dict, expiresDelta: timedelta = None) -> str:
    toEncode = data.copy()
    if expiresDelta:
        expire = datetime.utcnow() + expiresDelta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    toEncode.update({"exp": expire})
    encodedJwt = jwt.encode(toEncode, SECRET_KEY, algorithm = ALGORITHM)
    return encodedJwt

def getCurrentUser(sessionToken: str = Cookie(None), db: Session = Depends(get_db)):
    if sessionToken is Cookie(None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    credentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(sessionToken, SECRET_KEY, algorithms= ALGORITHM)
        email: str = payload.get("sub")
        if email is None:
            raise credentialsException
        token_data = TokenData(email = email)
    except JWTError:
        raise credentialsException

    user = db.query(Users).filter(Users.email == token_data.email).first()
    if user is None:
        raise credentialsException
    return user
