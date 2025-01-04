from sqlalchemy.orm import Session
from models import Chats, Users
from fastapi import HTTPException, status
from crypt import getPasswordHash, verifyPassword
from schemas import UserCreate

def getChatRoomById(db: Session, roomId: int) -> Chats:
    room = db.query(Chats).filter(Chats.id == roomId).first()
    return room

def getUserChatRooms(db: Session, user: Users):
    return db.query(Chats).filter(Chats.userId == user.id).all()

def searchChatRooms(db: Session, query: str):
    return db.query(Chats).filter(Chats.name.contains(query)).all()

def createChatRoom(db: Session, roomName: str, user: Users):
    chatRoom = Chats(name = roomName, userId = user.id)
    db.add(chatRoom)
    db.commit()
    db.refresh(chatRoom)
    return chatRoom

def deleteUserChatRoom(db: Session, roomId: int, user: Users):
    room = db.query(Chats).filter(Chats.id == roomId, Chats.userId == user.id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you do not have permission to delete this room."
        )
    
    db.delete(room)
    db.commit()

def createUser(db: Session, user: UserCreate) -> Users:
    hashedPassword = getPasswordHash(user.password)
    dbUser = Users(email = user.email, hashedPassword = hashedPassword)
    db.add(dbUser)
    db.commit()
    db.refresh(dbUser)
    return dbUser

def authenticateUser(db: Session, email: str, password: str) -> Users | None:
    user = db.query(Users).filter(Users.email == email).first()
    if user and verifyPassword(password, user.hashedPassword):
        return user
    return None