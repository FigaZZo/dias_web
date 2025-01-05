from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from crypt import getPasswordHash
from database import engine, Base, get_db
from schemas import UserCreate
from auth import createAccessToken, getCurrentUser
from crud import createChatRoom, getUserChatRooms, searchChatRooms, createUser, authenticateUser, deleteUserChatRoom, getChatRoomById
from models import Users
from fastapi.responses import HTMLResponse


Base.metadata.create_all(bind = engine)

app = FastAPI()

templates = Jinja2Templates(directory = "templates")


@app.get("/")
def getRootPage(request: Request, db: Session = Depends(get_db)):
    if request.cookies.get("sessionToken"):
        user = getCurrentUser(request.cookies.get("sessionToken"), db = db)
        return templates.TemplateResponse("index.html", {"request": request, "user": f"{user.email}"})
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register")
def getRegisterPage(request: Request):
    if request.cookies.get("sessionToken"):
        return RedirectResponse(url = "/chats", status_code = 303)
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def postRegisterUser(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if request.cookies.get("sessionToken"):
        return RedirectResponse(url = "/chats", status_code = 303)
    
    dbUser = db.query(Users).filter(Users.email == email).first()
    if dbUser:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email is already registered!"})
    
    createUser(db = db, user = UserCreate(email = email, password = password))

    accessToken = createAccessToken(data = {"sub": email})
    response = RedirectResponse(url = "/chats", status_code = 303)
    response.set_cookie(key = "sessionToken", value = accessToken, httponly = True, max_age = 3600)
    return response

@app.get("/login")
def getLoginPage(request: Request):
    if request.cookies.get("sessionToken"):
        return RedirectResponse(url = "/chats", status_code = 303)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def postLoginUser(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if request.cookies.get("sessionToken"):
        return RedirectResponse(url = "/chats", status_code = 303)
    
    if not db.query(Users).filter(Users.email == username).first():
        return templates.TemplateResponse("login.html", {"request": request, "error1": "No user with this email found!"})

    user = authenticateUser(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error2": f"Wrong password for {username}!"})

    accessToken = createAccessToken(data = {"sub": user.email})
    response = RedirectResponse(url = "/chats", status_code = 303)
    response.set_cookie(key = "sessionToken", value = accessToken, httponly = True, max_age = 3600)
    return response

@app.get("/logout")
def postLogoutUser(request: Request):
    response = RedirectResponse(url = "/", status_code = 303)
    response.delete_cookie(key = "sessionToken")
    response.delete_cookie(key = "roomId")
    return response

@app.get("/chats")
def getChatsPage(request: Request, db: Session = Depends(get_db)):
    if not request.cookies.get("sessionToken"):
        return templates.TemplateResponse("error.html", {"request": request, "error": "Not authenticated"}, status_code = 401)
    
    currentUser = getCurrentUser(request.cookies.get("sessionToken"), db)

    rooms = getUserChatRooms(db = db, user = currentUser)
    return templates.TemplateResponse("chats.html", {"request": request, "rooms": rooms, "user": currentUser})

@app.post("/chats/")
def postCreateChat(request: Request, roomName: str = Form(...), db: Session = Depends(get_db)):
    if not request.cookies.get("sessionToken"):
        return templates.TemplateResponse("error.html", {"request": request, "error": "Not authenticated"}, status_code = 401)

    currentUser = getCurrentUser(request.cookies.get("sessionToken"), db)

    createChatRoom(db = db, roomName = roomName, user = currentUser)
    return RedirectResponse(url = "/chats", status_code = 303)

@app.get("/chats/search/")
def getSearchChats(query: str, request: Request, db: Session = Depends(get_db)):
    if not request.cookies.get("sessionToken"):
        return templates.TemplateResponse("error.html", {"request": request, "error": "Not authenticated"}, status_code = 401)

    currentUser = getCurrentUser(request.cookies.get("sessionToken"), db)

    rooms = searchChatRooms(db = db, query = query)
    return templates.TemplateResponse("chats.html", {"request": request, "rooms": rooms, "user": currentUser, "query": True})

@app.post("/chats/{roomId}/delete")
def postDeleteChat(request: Request, roomId: int, db: Session = Depends(get_db)):
    if not request.cookies.get("sessionToken"):
        return templates.TemplateResponse("error.html", {"request": request, "error": "Not permitted, or not authorized, idk"}, status_code = 400)

    currentUser = getCurrentUser(request.cookies.get("sessionToken"), db)

    deleteUserChatRoom(db = db, roomId = roomId, user = currentUser)
    return RedirectResponse(url = "/chats", status_code = 303)

@app.get("/chats/{roomId}", response_class = HTMLResponse)
def getChatRoom(request: Request, roomId: int, db: Session = Depends(get_db)):
    if not request.cookies.get("sessionToken"):
        return templates.TemplateResponse("error.html", {"request": request, "error": "Not permitted, or not authorized, idk"}, status_code = 400)

    currentUser = getCurrentUser(request.cookies.get("sessionToken"), db)

    room = getChatRoomById(db, roomId)
    if not room:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Chat room not found"}, status_code = 404)
    
    response = templates.TemplateResponse("chatRoom.html", {"request": request})
    response.set_cookie(key = "roomId", value = str(roomId), httponly = True, max_age = 3600)
    return response