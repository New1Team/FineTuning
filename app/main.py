from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import dataset, hugging_face, model_router, save_db, save_jsonl, system_router


app = FastAPI(
    title="1Team's ESG FineTuning API System",
    description="데이터 수집부터 모델 로드, DB 저장까지 통합된 AI 관리 시스템입니다. ✨",
    version="1.0.0"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
      "http://localhost:5173",
      "http://127.0.0.1:5173",
      "http://localhost:8501",
      "http://aiedu.tplinkdns.com:7210",
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# 1. 시스템 정보 확인 (GPU/PyTorch 체크)
app.include_router(system_router.router)

# 2. 데이터 관리 (data.py 리스트 관리)
app.include_router(dataset.router)

# 3. 데이터 저장 (DB 및 JSONL 저장)
app.include_router(save_db.router)
app.include_router(save_jsonl.router)

# 4. 모델 관리 및 추론 (Unsloth 로드 및 HuggingFace 연동)
app.include_router(model_router.router)
app.include_router(hugging_face.router)

# @app.on_event("startup")
# async def startup_event():
#     print("🚀 ESG 분석 서버가 가동됩니다!")
#     print("📍 Swagger UI: http://127.0.0.1:8000/docs")
#     # 필요시 서버 시작 시점에 모델을 미리 로드하려면 아래 주석을 해제하세요.
#     # model_router.load_unsloth_model()

@app.get("/")
def read_root():
  return {"status": True}