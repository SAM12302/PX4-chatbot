import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from api.retriever import search_embedding
from api.prompt_builder import build_prompt
from api.llm import inference

app = FastAPI()

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

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