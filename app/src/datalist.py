import os
from settings import settings

def setFolder():
  folder_path = settings.folder_path
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print("폴더를 생성했습니다.")
  else:
    print("폴더가 이미 존재합니다.")
  return folder_path

def append_datalist(newPrompt, newCompletion):
  folder_path = setFolder()
  file_path = os.path.join(folder_path, "data.py")

    # 파일 없으면 초기화
  if not os.path.exists(file_path):
    with open(file_path, "w", encoding="utf-8") as f:
      f.write("datalist=[]")
    print(f"{file_path} 파일을 생성했습니다.")
    
    # 추가할 데이터
  new_entry={
    "prompt": newPrompt,
    "completion": newCompletion
  }

  with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

  if "]" in content:
    parts = content.rsplit("]",1)
    is_empty = "datalist = []" in content.replace(" ","")
    separator = "" if is_empty else ","

    entry_str = f"{separator}\n  {{\n    \"prompt\": {repr(new_entry['prompt'])},\n    \"completion\": {repr(new_entry['completion'])}\n  }}"
    update_content = parts[0].rstrip() + entry_str + "\n]"

    with open(file_path, "w", encoding="utf-8") as f:
      f.write(update_content)
    print(f"{newCompletion} 추가 완료.")
  else:
    print("파일 형식이 올바르지 않습니다.")


def run():
  """
  프로그램 메인 로직 실행 함수
  """
  prompt_text = "질문 프롬포트"
  completion_text = "매칭 답"
  append_datalist(prompt_text, completion_text)
  if __name__ == "__main__":
    run()