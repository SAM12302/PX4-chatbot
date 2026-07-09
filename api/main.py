import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.retriever import search_embedding
from api.prompt_builder import build_prompt
from api.llm import inference
from api.auth import create_access_token, verify_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
JWT_ENABLED = os.getenv("JWT_ENABLED", "false").lower() == "true"

@app.post("/token")
async def get_token(user_id: str = "anonymous"):
    """Issue a JWT token for WebSocket authentication."""
    token = create_access_token(user_id)
    return JSONResponse({"access_token": token, "token_type": "bearer"})

@app.websocket("/chat")
async def chat(websocket: WebSocket, token: str = None):
    if JWT_ENABLED and token:
        payload = verify_token(token)
        if not payload:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            print("WebSocket connection rejected: invalid token")
            return
        user_id = payload.get("user_id", "anonymous")
    else:
        user_id = "anonymous"

    await websocket.accept()
    print(f"Client connected (user: {user_id})")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            question = payload.get("question", "")
            history = payload.get("history", [])

            if not question:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": "No question provided"
                }))
                continue

            chunks = search_embedding(question)
            prompt = build_prompt(chunks, history, question)

            stream = await asyncio.to_thread(inference, prompt)

            for token in stream:
                content = token.choices[0].delta.content
                if content is not None:
                    await websocket.send_text(json.dumps({
                        "type": "token",
                        "content": content
                    }))

            await websocket.send_text(json.dumps({"type": "done"}))

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": str(e)
        }))