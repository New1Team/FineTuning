import json
from src.sessions.data import datalist
from fastapi import APIRouter

router = APIRouter(
    prefix="/jsonl",
    tags=["jsonl"]
)

data = datalist

@router.post("/save")
def save_to_jsonl(data, filename):
  """
  1 .파이썬 리스트 데이터를 .jsonl 파일로 저장하는 함수입니다.
  
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
  return {"status": True, "data": data}

