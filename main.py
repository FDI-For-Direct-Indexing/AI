from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용. 필요에 따라 특정 도메인을 명시할 수 있습니다.
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
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

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

executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY30jk7lQP3xmyTRusMTthaYhI3ck8eby7gMtD+7avw7f',
    api_key_primary_val='o4VPDSSP0K25kLp9gyfLMasuKzxLcFsLSPUnfbF5',
    request_id='01cf4b60-dc37-4695-86f1-0718c4661770'
)

@app.post("/execute_completion")
def execute_completion(request: CompletionRequest):
    try:
        response = executor.execute(request)
        return {"status": "success", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run the server, save this file and run: uvicorn filename:app --reload

