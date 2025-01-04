from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from crypt import getPasswordHash
from database import engine, Base, get_db
from schemas import UserResponse
from auth import createAccessToken, getCurrentUser
from crud import createChatRoom, getUserChatRooms, searchChatRooms, createUser, authenticateUser, deleteUserChatRoom, getChatRoomById
from models import Users
from fastapi.responses import HTMLResponse


Base.metadata.create_all(bind = engine)

app = FastAPI()

templates = Jinja2Templates(directory = "templates")

f = open("example.txt", "w")
f.write("hello")
f.close()

@app.get("/")
def readRoot(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register")
def getRegisterPage(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def registerUser(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    dbUser = db.query(Users).filter(Users.email == email).first()
    if dbUser:
        return templates.TemplateResponse("register.html", {"request": Request, "error": "Email already registered"})
    hashedPassword = getPasswordHash(password)
    newUser = Users(email = email, hashedPassword = hashedPassword)

    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    return RedirectResponse(url = "/login", status_code = 303)


@app.get("/login")
def getLoginPage(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def loginUser(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticateUser(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    accessToken = createAccessToken(data = {"sub": user.email})
    response = RedirectResponse(url = "/chatRooms", status_code = 303)
    response.set_cookie(key = "sessionToken", value = accessToken, httponly = True, max_age = 3600)
    return response

@app.get("/chatRooms")
def getChatRoomsPage(request: Request, currentUser: UserResponse = Depends(getCurrentUser), db: Session = Depends(get_db)):
    rooms = getUserChatRooms(db = db, user = currentUser)
    return templates.TemplateResponse("chatRooms.html", {"request": request, "rooms": rooms, "user": currentUser})

@app.post("/chats/")
def createChat(roomName: str = Form(...), db: Session = Depends(get_db), currentUser: UserResponse = Depends(getCurrentUser)):
    createChatRoom(db = db, roomName = roomName, user = currentUser)
    return RedirectResponse(url = "/chatRooms", status_code = 303)

@app.get("/chats/search/")
def search_chats(query: str, request: Request, db: Session = Depends(get_db), currentUser: UserResponse = Depends(getCurrentUser)):
    rooms = searchChatRooms(db = db, query = query)
    return templates.TemplateResponse("found.html", {"request": request, "rooms": rooms, "user": currentUser, "query": query})

@app.post("/chats/{roomId}/delete")
def deleteChat(roomId: int, db: Session = Depends(get_db), currentUser: UserResponse = Depends(getCurrentUser)):
    deleteUserChatRoom(db = db, roomId = roomId, user = currentUser)
    return RedirectResponse(url = "/chatRooms", status_code = 303)

@app.get("/chats/{roomId}", response_class = HTMLResponse)
def getChatRoom(request: Request, roomId: int, db: Session = Depends(get_db), currentUser: UserResponse = Depends(getCurrentUser)):
    room = getChatRoomById(db, roomId)
    if not room:
        raise HTTPException(status_code = 404, detail = "Room not found")
    
    return templates.TemplateResponse("chatRoom.html", {"request": request, "room": room})