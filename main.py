from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import List
from dotenv import load_dotenv
import os
import json
import re

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

class SaveResponseRequest(BaseModel):
    response: str

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
        with requests.post(self._host + '/testapp/v1/tasks/x571330t/chat-completions',
                           headers=headers, json=completion_request.dict(), stream=True) as r:
            for line in r.iter_lines():
                if line:
                    response_lines.append(line.decode("utf-8"))

        return response_lines

executor = CompletionExecutor()
final_response = ""  # 저장할 응답을 위한 전역 변수

@app.post("/ai/execute-completion") 
def execute_completion(request: CompletionRequest):
    global final_response
    try:
        response = executor.execute(request)
        
        # event:result부분만 추출 - 데이터 파싱
        for line in response:
            if line.startswith('event:result'):
                next_line_index = response.index(line) + 1
                data_line = response[next_line_index]
                break
        else:
            raise HTTPException(status_code=500, detail="No valid data line found")

        # Extract the JSON part from the data line
        data_json_str = data_line.split("data:", 1)[1]
        data_json = json.loads(data_json_str)

        #'content'부분만 추출
        content = data_json.get("message", {}).get("content", "")

        # 5번째 응답을 저장
        if request.messages[-1].content.endswith("가중치 지수를 보여주세요"):
            final_response = content

        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/save-final-response")
def save_final_response(request: SaveResponseRequest):
    global latest_response
    latest_response = request.response
    return {"status": "success"}

@app.get("/ai/get-final-response")
def get_final_response():
    if latest_response is None:
        return {"parsed_response": "가중치 지수 정보를 찾을 수 없습니다."}

    # 대괄호 안의 내용만 추출하는 정규식 패턴
    match = re.search(r'\[.*?\]', latest_response)
    if match:
        parsed_response = match.group(0)  # 대괄호 포함된 내용만 저장
    else:
        parsed_response = "가중치 지수 정보를 찾을 수 없습니다."

    return {parsed_response}




# run: uvicorn filename:app --reload

