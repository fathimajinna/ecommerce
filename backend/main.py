from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import get_agent_response

app = FastAPI()
origins = [
    "http://localhost:3000",  # The origin of your React frontend
    # You can add more origins here if needed (e.g., for production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_query = request.message
        agent_response = get_agent_response(user_query)
        return ChatResponse(response=agent_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "General Agent API is running."}