# 🌱 ESG News Auto-Classifier: Issue Pull Fine-Tuning Project

> **뉴스 문장을 ESG 1차 이슈(Issue Pull)로 자동 분류하는 경량 거버넌스 AI 모델 구축 프로젝트**입니다. 
> 본 프로젝트는 단순 텍스트 분류를 넘어, **News → Signal → Issue**로 이어지는 보고서 자동화 파이프라인의 핵심 입력 단계를 구조화하는 데 목적이 있습니다. 📊

---

## 🎯 1. 프로젝트 개요 (Project Overview)

* **목적**: 뉴스 문장을 분석하여 정의된 ESG 1차 이슈 카테고리로 자동 매핑하는 분류 모델 구축
* **핵심 방향**: 
    * 비정형 뉴스 데이터를 정형화된 ESG 데이터 구조로 전환
    * **News → Signal → Issue** 구조화를 통한 보고서 자동화 파이프라인 연동
    * 다양한 LLM(Llama, Qwen, Gemma) 비교를 통한 최적의 한국어/ESG 분류 모델 식별

---

## 🗂️ 2. 데이터 설계 (Data Engineering)

### 🏗️ 데이터 구조 (Data Structure)
* **Format**: JSONL (Instruction Tuning용)
* **Prompt**: 뉴스 문장 기반의 질문 (예: "이 문장은 ESG 이슈풀 중 어디에 해당하나?")
* **Completion**: 정의된 ESG 이슈 라벨 (Climate, Labor, Safety, Governance 등)

### 📊 데이터 통계 및 설계 기준
* **데이터 수**: 약 80~90개 문장 (PoC 및 실습용 데이터셋)
* **레이어 분리**: 데이터의 신뢰성 확보를 위해 아래 레이어 구조를 유지함
    * `Master` / `Dictionary` / `Fact` / `Evidence` / `AI Layer`

---

## 🛠️ 3. 기술 스택 및 학습 방식 (Tech Stack & Training)

### 💻 개발 환경
* **Environment**: Google Colab (Tesla T4 GPU)
* **Framework**: Unsloth (2x Faster Fine-Tuning Library)
* **Method**: SFT (Supervised Fine-Tuning) + **LoRA** (Low-Rank Adaptation)

### 🤖 모델 비교 실험 (Model Comparison)
프로젝트 진행 시 환경과 목적에 따라 3가지 베이스 모델을 비교 분석했습니다.

| 모델 (Model) | 특장점 | 비고 |
| :--- | :--- | :--- |
| **LLaMA 3.1/3.2** | 안정적인 아키텍처, 가장 높은 범용성 | Baseline |
| **Qwen 2.5** | **한국어 문맥 이해 및 분류 성능 최상** | **최적 후보 (Selected)** |
| **Gemma 4/2** | 경량화된 구조, 빠른 추론 속도 | 배포용 적합 |

---

## 📈 4. 향후 과제 및 확장 계획 (Next Steps)

### ⚠️ 한계점 및 개선 사항
* **데이터 확장**: 현재 90개 수준에서 300~1,000개 이상의 문장 확보 필요 📚
* **라벨 정교화**: `Climate` vs `Energy` 등 경계가 모호한 라벨에 대한 정의 고도화

### 🚀 다음 단계 (Roadmap)
1.  **파이프라인 확장**: 뉴스 → 이슈 분류 → Evidence 추출 → KPI 매핑 → 보고서 자동 생성
2.  **RAG 연동**: 최신 ESG 공시 기준(ISSB 등)을 참조하는 검색 증강 생성 시스템 구축
3.  **Local Deployment**: Ollama 등을 활용한 로컬 서버 배포 및 테스트

---

## 💡 핵심 요약 (Key Takeaway)
> **"ESG 뉴스 문장을 구조화하는 분류 모델을 구축하고, Unsloth를 이용한 경량 파인튜닝 기법을 통해 적은 자원으로도 전문 도메인 지식을 학습할 수 있음을 증명함."** ✨
