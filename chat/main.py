from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Cookie, HTTPException, status
from jose import jwt, JWTError
from typing import List, Dict, Union
import logging

app = FastAPI()

SECRET_KEY = "very-secret-password"  
ALGORITHM = "HS256"

connections: Dict[int, List[WebSocket]] = {}

logging.basicConfig(filename='example.log', level = logging.INFO)
logging.info("Hello")

async def broadcast(roomId: int, message: str):
    if roomId in connections:
        logging.info(f"Broadcasting message to room {roomId}: {message}")
        for connection in connections[roomId]:
            await connection.send_text(message)

@app.websocket("/ws")
async def websocketEndpoint(websocket: WebSocket, roomId: str = Cookie(None), sessionToken: str = Cookie(None)):
    logging.info(sessionToken)
    if sessionToken is Cookie(None) or roomId is Cookie(None):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        logging.info(f"Attempting to connect WebSocket for room {roomId} with token: {sessionToken}")
        payload = jwt.decode(sessionToken, SECRET_KEY, algorithms = ALGORITHM)
        userEmail = payload.get("sub")
        if not userEmail:
            logging.warning("Token verification failed")
            await websocket.close(code = 1008)
            return
        logging.info(f"Token verified for user {userEmail} in room {roomId}")
    except JWTError:
        logging.error("JWT error - Invalid token")
        await websocket.close(code = 1008)
        return

    await websocket.accept()
    if roomId not in connections:
        connections[roomId] = []
    connections[roomId].append(websocket)
    logging.info(f"User {userEmail} joined room {roomId}")
    await broadcast(roomId, f"{userEmail} has joined the chat")

    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Received message from {userEmail} in room {roomId}: {data}")
            await broadcast(roomId, f"{userEmail}: {data}")
    except WebSocketDisconnect:
        connections[roomId].remove(websocket)
        logging.info(f"User {userEmail} left room {roomId}")
        await broadcast(roomId, f"{userEmail} has left the chat")
