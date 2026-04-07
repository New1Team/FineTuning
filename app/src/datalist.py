import os
from src.core.settings import settings

def setFolder():
  folder_path = settings.folder_path
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print("폴더를 생성했습니다.")
  else:
    print("폴더가 이미 존재합니다.")
  return folder_path

def append_datalist(new_data_list):
  """
  new_data_list = [{"prompt": newPrompt, "completion": newCompletion}, ...] 형식
  """
  folder_path = setFolder()
  file_path = os.path.join(folder_path, "data.py")

    # 파일 없으면 초기화
  if not os.path.exists(file_path):
    with open(file_path, "w", encoding="utf-8") as f:
      f.write("datalist=[]")
    print(f"{file_path} 파일을 생성했습니다.")
    
    
  
  with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

  if "]" in content:
    parts = content.rsplit("]",1)
    is_empty = "datalist=[]" in content.replace(" ", "").replace("\n", "")
    entries = []
    # 추가할 데이터, 컬럼 수정시 해당 부분 수정하면 됨
    for i, item in enumerate(new_data_list):
      separator= "" if (is_empty and i == 0) else ","
      entry_str = f"{separator}\n  {{\n    \"prompt\": {repr(item['prompt'])},\n    \"completion\": {repr(item['completion'])}\n  }}"
      entries.append(entry_str)
    all_entry_str = "".join(entries)
    update_content = parts[0].rstrip() + all_entry_str + "\n]"

    with open(file_path, "w", encoding="utf-8") as f:
      f.write(update_content)
    print(f"{new_data_list} 추가 완료.")
    return new_data_list
  else:
    print("파일 형식이 올바르지 않습니다.")


def run(new_data_list):
  """
  프로그램 메인 로직 실행 함수
  """
  append_datalist(new_data_list)
  if __name__ == "__main__":
    run()