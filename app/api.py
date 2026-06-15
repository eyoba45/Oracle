from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent.core import run_agent
import json

app = FastAPI(title="Oracle AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "Oracle AI Agent is running"}

@app.post("/ask")
def ask(request: QueryRequest):
    result = run_agent(request.question)
    return result 