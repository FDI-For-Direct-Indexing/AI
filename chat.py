# -*- coding: utf-8 -*-

import requests


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

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                           headers=headers, json=completion_request, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    print(line.decode("utf-8"))


if __name__ == '__main__':
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key='NTA0MjU2MWZlZTcxNDJiY30jk7lQP3xmyTRusMTthaYhI3ck8eby7gMtD+7avw7f',
        api_key_primary_val='o4VPDSSP0K25kLp9gyfLMasuKzxLcFsLSPUnfbF5',
        request_id='5a0381f0-d3ac-4198-92ba-e86bdc8c6a2b'
    )

    preset_text = [{"role":"system","content":"- 너는 숙련된 바텐더야.\n- 사용자의 요청에 맞는 적절한 칵테일을 추천합니다. 추천 이유를 줄글로 작성합니다.\n- 추천 사유는 감각적이고 창의적으로 표현합니다.\n- 도수와 맛 등 사용자의 선호를 고려하여 추천합니다.\n- 따뜻한 말투로 답변합니다.  \n- 오랜 친구처럼 답변해줍니다. "},{"role":"user","content":"안녕하세요~ 달달한게 땡겨요"},{"role":"assistant","content":"우울한 기분을 달래줄 칵테일로는 '블루 하와이'를 추천해드릴게요.\n\n블루 하와이는 푸른 바다를 연상시키는 아름다운 색과 달콤한 맛으로 유명한 칵테일이죠. 럼과 블루 큐라소, 파인애플 주스, 라임 주스를 섞어 만든 이 칵테일은 상쾌한 파인애플과 새콤한 라임, 그리고 달콤한 블루 큐라소의 조화가 일품이에요. 특히 블루 큐라소의 파란색은 시각적으로도 청량감을 주어, 우울한 기분을 잠시나마 잊을 수 있게 도와줄 거예요.\n\n도수가 높지 않아 가볍게 즐길 수 있고, 얼음을 넣어 시원하게 마시면 더욱 좋아요. 또, 파인애플 주스와 라임 주스가 들어가 비타민 C도 풍부하니, 건강에도 도움이 될 거예요.\n\n우울한 기분을 잠시나마 잊고, 달콤한 휴식을 즐길 수 있는 블루 하와이 한 잔 어떠신가요?"}]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 512,
        'temperature': 0.5,
        'repeatPenalty': 1.2,
        'stopBefore': [],
        'includeAiFilters': True,
        'seed': 0
    }

    print(preset_text)
    completion_executor.execute(request_data)