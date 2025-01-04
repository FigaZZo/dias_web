from passlib.context import CryptContext

#Encryption
pwdContext = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def getPasswordHash(password: str) -> str:
    return pwdContext.hash(password)

def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    return pwdContext.verify(plainPassword, hashedPassword)