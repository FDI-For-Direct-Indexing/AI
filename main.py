from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import List
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class CompletionRequest(BaseModel):
    messages: List[Message]
    topP: float
    topK: int
    maxTokens: int
    temperature: float
    repeatPenalty: float
    stopBefore: List[str]
    includeAiFilters: bool
    seed: int

class CompletionExecutor:
    def __init__(self):
        self._host = os.getenv('HOST')
        self._api_key = os.getenv('API_KEY')
        self._api_key_primary_val = os.getenv('API_KEY_PRIMARY_VAL')
        self._request_id = os.getenv('REQUEST_ID')

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        response_lines = []
        with requests.post(self._host + '/testapp/v1/tasks/5s8ggqow/chat-completions',
                           headers=headers, json=completion_request.dict(), stream=True) as r:
            for line in r.iter_lines():
                if line:
                    response_lines.append(line.decode("utf-8"))

        return response_lines

executor = CompletionExecutor()

@app.post("/execute_completion") 
#post url
def execute_completion(request: CompletionRequest):
    try:
        response = executor.execute(request)
        return {"status": "success", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# run: uvicorn filename:app --reload

