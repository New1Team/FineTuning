from settings import settings
import json

# 저장할 학습용 데이터셋 예시입니다.
# 각 요소는 'prompt'(입력)와 'completion'(출력)을 키로 가진 딕셔너리 형태입니다.
# 이 data를 어떻게 만드냐에 따라 성능에 차이가 생김(질문-답 한 세트)
# 사용 모델에 따라 키가 달라짐
data = [
  {"prompt": "안녕?", "completion": "안녕하세요! 무엇을 도와드릴까요?"},
  {"prompt": "날씨 어때?", "completion": "오늘은 맑고 화창합니다."},
  {"prompt": "1+1은?", "completion": "2입니다."}
]

def save_to_jsonl(data, filename):
  """
  파이썬 리스트 데이터를 .jsonl 파일로 저장하는 함수입니다.
  
  Args:
    data (list): 저장할 딕셔너리들이 담긴 리스트
    filename (str): 저장할 파일의 경로 및 이름
  """
  # 파일을 쓰기 모드('w')로 엽니다. 한글 깨짐 방지를 위해 utf-8 인코딩을 지정합니다.
  with open(filename, 'w', encoding='utf-8') as f:
    for entry in data:
      # 딕셔너리를 JSON 문자열로 변환합니다.
      # ensure_ascii=False는 한글이 \uXXXX 형태로 변하는 것을 막고 그대로 저장하게 합니다.
      json_record = json.dumps(entry, ensure_ascii=False)
      
      # 변환된 JSON 문자열 뒤에 줄바꿈 기호(\n)를 붙여 파일에 씁니다.
      # 이 과정을 통해 한 줄에 하나의 JSON 객체가 위치하는 JSONL 형식이 완성됩니다.
      f.write(json_record + '\n')

def run():
  """
  프로그램의 메인 로직을 실행하는 함수입니다.
  """
  # settings 객체에 정의된 json_file 경로를 사용하여 데이터를 저장합니다.
  save_to_jsonl(data, settings.json_file)

# 이 스크립트가 직접 실행될 때만 run() 함수를 호출합니다.
# 다른 파일에서 이 파일을 import 할 때는 실행되지 않습니다.
if __name__ == "__main__":
  run()
