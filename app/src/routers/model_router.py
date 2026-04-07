from fastapi import APIRouter, HTTPException
# from unsloth import FastLanguageModel
import torch

router = APIRouter(
    prefix="/model",
    tags=["Model Management"]
)

# 전역 변수로 모델과 토크나이저를 관리 (싱글톤 패턴처럼 활용)
model = None
tokenizer = None

# def load_unsloth_model():
#     """
#     Unsloth를 사용하여 모델과 토크나이저를 로드하고 LoRA 설정을 적용합니다.
#     """
#     global model, tokenizer
    
#     try:
#         # 1. 모델 및 토크나이저 로드 (4bit 양자화 적용)
#         model, tokenizer = FastLanguageModel.from_pretrained(
#             model_name = "unsloth/Llama-3.2-3B-Instruct",
#             max_seq_length = 2048,
#             dtype = None,
#             load_in_4bit = True,
#         )

#         # 2. PEFT/LoRA 설정 적용
#         model = FastLanguageModel.get_peft_model(
#             model,
#             r = 16,
#             lora_alpha = 32,
#             lora_dropout = 0.05,
#             target_modules = [
#                 "q_proj", "k_proj", "v_proj", "o_proj",
#                 "gate_proj", "up_proj", "down_proj",
#             ],
#             bias = "none",
#             use_gradient_checkpointing = "unsloth",
#             random_state = 123,
#             use_rslora = False,
#             loftq_config = None,
#         )
#         print("✅ Unsloth 모델 로드 및 LoRA 설정 완료!")
#         return True
#     except Exception as e:
#         print(f"❌ 모델 로드 중 오류 발생: {e}")
#         return False

# @router.get("/status")
# def get_model_status():
#     """
#     현재 모델이 메모리에 로드되어 있는지 확인합니다.
#     """
#     if model is not None and tokenizer is not None:
#         return {
#             "status": "loaded",
#             "model_name": model.config._name_or_path,
#             "max_seq_length": model.config.max_position_embeddings,
#             "is_trainable": any(p.requires_grad for p in model.parameters())
#         }
#     return {"status": "not_loaded", "message": "모델이 아직 로드되지 않았습니다."}

# # 서버 시작 시 자동으로 로드하고 싶다면 main.py에서 load_unsloth_model()을 호출하세요.

@router.get("/status")
def get_model_status():
    return {
        "status": "disabled",
        "message": "현재 Unsloth 라이브러리 충돌로 인해 모델 로드가 비활성화되었습니다."
    }