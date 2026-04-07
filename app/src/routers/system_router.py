import torch
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/system",
    tags=["System Info"]
)

@router.get("/cuda-check")
def check_cuda_status():
    """
    1. PyTorch 버전 및 NVIDIA GPU의 연산 능력(Compute Capability)을 확인하는 API입니다. 🚀
    """
    try:
        # GPU 사용 가능 여부 먼저 체크
        is_cuda_available = torch.cuda.is_available()
        
        if not is_cuda_available:
            return {
                "pytorch_version": torch.__version__,
                "cuda_available": False,
                "message": "NVIDIA GPU를 찾을 수 없습니다. CPU 모드로 동작합니다."
            }

        # GPU 연산 능력 가져오기
        # major: 아키텍처 세대 (8: Ampere, 9: Hopper 등)
        # minor: 세부 개선 버전
        major, minor = torch.cuda.get_device_capability()
        device_name = torch.cuda.get_device_name(0)

        return {
            "pytorch_version": torch.__version__,
            "cuda_available": True,
            "device_name": device_name,
            "compute_capability": {
                "major": major,
                "minor": minor,
                "full": f"{major}.{minor}"
            },
            "message": f"성공적으로 {device_name}을(를) 인식했습니다! 🎉"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시스템 정보 확인 중 오류 발생: {str(e)}")