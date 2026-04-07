import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class ESGClassifier:
    def __init__(self):
        # 1. 모델 경로 설정 (로컬 경로로 수정)
        self.model_path = "app/models/esg_classifier"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 2. 토크나이저 및 모델 로드
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # 3. 카테고리 매핑 (코랩 설정에 맞게 수정)
        self.categories = {0: "Climate", 1: "Energy", 2: "Labor", 3: "Safety", 4: "Human Rights", 5: "Governance"}

    def predict(self, sentence: str):
        # 코랩의 전처리 로직을 그대로 가져옵니다.
        inputs = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=128)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            prediction = torch.argmax(logits, dim=-1).item()
            
        return self.categories.get(prediction, "Unknown")