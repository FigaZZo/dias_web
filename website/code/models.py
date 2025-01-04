from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, index = True, nullable = False)
    hashedPassword = Column(String, nullable = False)

    chat = relationship("Chats", back_populates = "user")

class Chats(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, index = True, nullable = False)
    userId = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates = "chat")
