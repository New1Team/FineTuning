import os
from fastapi import APIRouter, HTTPException, Body
from typing import List
from pydantic import BaseModel
from ..core.settings import settings

# 1. 데이터 검증을 위한 모델 정의
class DataEntry(BaseModel):
    prompt: str
    completion: str

router = APIRouter(
    prefix="/datalist",
    tags=["Datalist"]
)

def setFolder():
    folder_path = settings.folder_path
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더를 생성했습니다: {folder_path}")
    else:
        print("폴더가 이미 존재합니다.")
    return folder_path

@router.post("/append")
def append_datalist(new_data_list: List[DataEntry] = Body(...)):
    """
    전달받은 리스트 데이터를 data.py 파일의 리스트 끝에 자동으로 추가합니다.
    new_data_list = [{"prompt": newPrompt, "completion": newCompletion}, ...] 형식
    """
    try:
        folder_path = setFolder()
        file_path = os.path.join(folder_path, "data.py")

        # 파일이 없으면 초기화
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("datalist = []")
            print(f"{file_path} 파일을 생성했습니다.")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "]" in content:
            parts = content.rsplit("]", 1)
            # 공백 및 줄바꿈 제거 후 비어있는 리스트인지 확인
            clean_content = content.replace(" ", "").replace("\n", "").replace("\r", "")
            is_empty = "datalist=[]" in clean_content
            # 추가할 데이터, 컬럼 수정시 해당 부분 수정하면 됨
            entries = []
            for i, item in enumerate(new_data_list):
                # Pydantic 모델을 dict로 변환
                item_dict = item.dict()
                separator = "" if (is_empty and i == 0) else ","
                
                entry_str = (
                    f"{separator}\n  {{\n"
                    f"    \"prompt\": {repr(item_dict['prompt'])},\n"
                    f"    \"completion\": {repr(item_dict['completion'])}\n"
                    f"  }}"
                )
                entries.append(entry_str)
            
            all_entry_str = "".join(entries)
            update_content = parts[0].rstrip() + all_entry_str + "\n]"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(update_content)
            
            return {
                "status": True,
                "message": f"{len(new_data_list)}건 추가 완료",
                "file": file_path
            }
        else:
            raise HTTPException(status_code=400, detail="파일 형식이 올바르지 않습니다 (] 누락)")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))