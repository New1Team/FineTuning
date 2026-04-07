from ..core.settings import settings
from fastapi import APIRouter
from datasets import load_dataset
from huggingface_hub import delete_repo

router = APIRouter(
    prefix="/Hugging_Face",
    tags=["Hugging Face"]
)

@router.get("/upload")
def upload_hug():
  """
  로컬의 데이터 파일을 읽어 Hugging Face Hub에 업로드하는 메인 함수입니다.
  """
  # 업로드 시 기록될 커밋 메시지를 설정합니다.
  commit_message = "첫 번째 업로드"
  
  # 1. 로컬 데이터 로드
  # "json" 형식의 파일을 읽어오며, 경로는 settings.json_file에 정의된 값을 사용합니다.
  # 이 과정에서 데이터는 Hugging Face의 Dataset 객체 형태로 변환됩니다.
  dataset = load_dataset("json", data_files=settings.json_file)
  
  # 2. Hugging Face Hub로 업로드
  # push_to_hub 함수를 사용하여 서버에 데이터를 전송합니다.
  dataset.push_to_hub(
    repo_id=settings.repo_name,   # 업로드할 저장소 이름 (예: "사용자ID/데이터셋이름")
    commit_message=commit_message, # 버전 관리를 위한 설명 메시지
    token=settings.hf_token       # Hugging Face API 접근을 위한 쓰기(Write) 권한 토큰
  )
  return {"status": True, "message":"업로드 되었습니다."}

@router.get("/delete")
def delete_hug():
  """
  설정된 정보에 따라 Hugging Face Hub의 특정 저장소를 삭제하는 함수입니다.
  """
  # delete_repo 함수를 호출하여 실제 삭제를 진행합니다.
  delete_repo(
    repo_id=settings.repo_name, # 삭제할 저장소의 ID (예: '사용자ID/데이터셋이름')
    repo_type="dataset",        # 삭제하려는 저장소의 유형을 'dataset'으로 명시합니다. (model, space 등 가능)
    token=settings.hf_token     # 삭제 권한을 확인하기 위한 Hugging Face Access Token입니다.
  )
  # 삭제 작업은 별도의 경고 없이 즉시 실행되므로 실행 전 repo_id를 반드시 확인해야 합니다.
  return {"status": True, "message":"삭제되었습니다."}