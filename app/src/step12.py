from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from typing_extensions import TypedDict

from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph


# ============================================================
# 0. 설정값
# ============================================================
OLLAMA_MODEL = "llama3.2:3b"
REVIEW_THRESHOLD = 0.70
MAX_PARAGRAPHS = 5

# TODO: 반드시 Master -> Issue 매핑표 기준으로 교체할 것
ISSUE_POOL = [
    "Climate",
    "Energy",
    "Water",
    "Pollution",
    "Waste",
    "Biodiversity",
    "Product",
    "Circularity",
    "Labor",
    "Safety",
    "Talent",
    "Diversity",
    "Human Rights",
    "Supply Chain",
    "Community",
    "Product Liability",
    "Privacy",
    "Governance",
    "Risk",
    "Ethics",
    "Business Conduct",
    "Data Governance",
    "Compliance",
]

SIGNAL_TYPES = [
    "regulation",
    "incident",
    "litigation",
    "disclosure",
    "investment",
    "performance",
]

SEVERITY_LEVELS = ["low", "medium", "high"]
SENTIMENT_LABELS = ["positive", "neutral", "negative"]


# ============================================================
# 1. 표준 데이터 구조
# ============================================================
class ArticleRecord(TypedDict, total=False):
    article_id: str
    source_type: str
    source_name: str
    source_url: str
    title: str
    published_at: str
    crawled_at: str
    raw_text: str
    language: str
    country: str


class TextUnitRecord(TypedDict, total=False):
    text_unit_id: str
    article_id: str
    unit_type: Literal["title", "lead", "paragraph", "sentence"]
    unit_order: int
    text_unit: str
    is_core_signal: bool


class AnnotationRecord(TypedDict, total=False):
    text_unit_id: str
    primary_issue: str
    secondary_issues: List[str]
    sentiment_label: Literal["positive", "neutral", "negative"]
    signal_type: Literal[
        "regulation", "incident", "litigation", "disclosure", "investment", "performance"
    ]
    severity_level: Literal["low", "medium", "high"]
    reason_span: str
    confidence_score: float
    label_source: Literal["rule", "model", "human", "reviewed"]
    review_status: Literal["raw", "auto_labeled", "needs_review", "reviewed"]
    review_note: str


class SignalState(TypedDict, total=False):
    # input
    source_url: str
    source_type: str
    source_name: str
    title: str
    published_at: str
    raw_text: str

    # normalized records
    article: ArticleRecord
    text_units: List[TextUnitRecord]
    annotations: List[AnnotationRecord]

    # review routing
    auto_saved: List[AnnotationRecord]
    review_queue: List[AnnotationRecord]

    # ops
    debug_logs: List[str]
    error: str


# ============================================================
# 2. LLM 및 PromptTemplate
# ============================================================
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

ISSUE_PROMPT = PromptTemplate.from_template(
    """
당신은 ESG 미디어 분석용 issue 분류기다.

[목표]
아래 텍스트를 읽고 issue pool 기준으로 분류하라.

[규칙]
1. 반드시 primary_issue 1개를 선택
2. secondary_issues는 최대 2개까지 선택
3. issue는 반드시 아래 목록에서만 선택
4. 결과는 JSON만 출력

[issue pool]
{issue_pool}

[텍스트]
{text_unit}

반드시 아래 형식으로만 답하라:
{{
  "primary_issue": "...",
  "secondary_issues": ["...", "..."]
}}
""".strip()
)

SENTIMENT_PROMPT = PromptTemplate.from_template(
    """
당신은 ESG 뉴스 감성 분류기다.

[기준]
- positive: 개선, 투자 확대, 성과 달성, 정책 강화
- neutral: 단순 공시, 발표, 일반 동향, 중립적 설명
- negative: 사고, 유출, 위반, 제재, 소송, 벌금, 리스크 확대

[텍스트]
{text_unit}

반드시 아래 JSON 형식으로만 답하라:
{{
  "sentiment_label": "positive|neutral|negative"
}}
""".strip()
)

SIGNAL_TYPE_PROMPT = PromptTemplate.from_template(
    """
당신은 ESG signal_type 분류기다.

[선택지]
- regulation
- incident
- litigation
- disclosure
- investment
- performance

[텍스트]
{text_unit}

반드시 아래 JSON 형식으로만 답하라:
{{
  "signal_type": "..."
}}
""".strip()
)

SEVERITY_PROMPT = PromptTemplate.from_template(
    """
당신은 ESG signal severity 판정기다.

[기준]
- low: 일반 동향, 경미한 언급
- medium: 중요도 있으나 대형 사건은 아님
- high: 대규모 사고, 유출, 제재, 중대한 규제 영향

[텍스트]
{text_unit}

반드시 아래 JSON 형식으로만 답하라:
{{
  "severity_level": "low|medium|high"
}}
""".strip()
)

REASON_PROMPT = PromptTemplate.from_template(
    """
당신은 ESG 미디어 분류 근거 추출기다.

[목표]
아래 텍스트에서 현재 분류 결과를 가장 잘 뒷받침하는 짧은 근거 문구를 그대로 뽑아라.
근거 문구는 반드시 원문 일부여야 한다.

[텍스트]
{text_unit}

[현재 분류 결과]
- primary_issue: {primary_issue}
- sentiment_label: {sentiment_label}
- signal_type: {signal_type}
- severity_level: {severity_level}

반드시 아래 JSON 형식으로만 답하라:
{{
  "reason_span": "원문 그대로의 짧은 문구"
}}
""".strip()
)

issue_chain = ISSUE_PROMPT | llm
sentiment_chain = SENTIMENT_PROMPT | llm
signal_type_chain = SIGNAL_TYPE_PROMPT | llm
severity_chain = SEVERITY_PROMPT | llm
reason_chain = REASON_PROMPT | llm


# ============================================================
# 3. 유틸
# ============================================================
JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def parse_json_from_llm(raw: Any) -> Dict[str, Any]:
    text = raw.content if hasattr(raw, "content") else str(raw)
    match = JSON_BLOCK_RE.search(text)
    if not match:
        raise ValueError(f"JSON 블록을 찾을 수 없습니다: {text}")
    return json.loads(match.group(0))


def contains_reason_span(text_unit: str, reason_span: str) -> bool:
    return reason_span.strip() != "" and reason_span in text_unit


def validate_enum(value: str, allowed: List[str]) -> bool:
    return value in allowed


def calc_confidence(ann: AnnotationRecord, text_unit: str) -> float:
    score = 0.0

    if ann.get("primary_issue") in ISSUE_POOL:
        score += 0.25
    if validate_enum(ann.get("sentiment_label", ""), SENTIMENT_LABELS):
        score += 0.15
    if validate_enum(ann.get("signal_type", ""), SIGNAL_TYPES):
        score += 0.15
    if validate_enum(ann.get("severity_level", ""), SEVERITY_LEVELS):
        score += 0.15

    reason = ann.get("reason_span", "")
    if reason:
        score += 0.10
    if contains_reason_span(text_unit, reason):
        score += 0.20

    return round(min(score, 1.0), 2)


# ============================================================
# 4. Node 구현
# ============================================================
def init_article(state: SignalState) -> SignalState:
    article: ArticleRecord = {
        "article_id": new_id("article"),
        "source_type": state.get("source_type", "news"),
        "source_name": state.get("source_name", "unknown"),
        "source_url": state.get("source_url", ""),
        "title": state.get("title", ""),
        "published_at": state.get("published_at", ""),
        "crawled_at": now_iso(),
        "raw_text": state.get("raw_text", ""),
        "language": "ko",
        "country": "KR",
    }
    return {
        "article": article,
        "debug_logs": state.get("debug_logs", []) + [f"init_article: {article['article_id']}"]
    }


def split_text_units(state: SignalState) -> SignalState:
    article = state["article"]
    title = article.get("title", "").strip()
    raw_text = article.get("raw_text", "").strip()

    units: List[TextUnitRecord] = []
    order = 1

    if title:
        units.append({
            "text_unit_id": new_id("tu"),
            "article_id": article["article_id"],
            "unit_type": "title",
            "unit_order": order,
            "text_unit": title,
            "is_core_signal": True,
        })
        order += 1

    paragraphs = [p.strip() for p in raw_text.split("\n") if p.strip()]
    for p in paragraphs[:MAX_PARAGRAPHS]:
        units.append({
            "text_unit_id": new_id("tu"),
            "article_id": article["article_id"],
            "unit_type": "paragraph",
            "unit_order": order,
            "text_unit": p,
            "is_core_signal": True,
        })
        order += 1

    return {
        "text_units": units,
        "debug_logs": state.get("debug_logs", []) + [f"split_text_units: {len(units)} units"]
    }


def classify_issue(state: SignalState) -> SignalState:
    annotations: List[AnnotationRecord] = []

    for unit in state.get("text_units", []):
        parsed = parse_json_from_llm(issue_chain.invoke({
            "issue_pool": ", ".join(ISSUE_POOL),
            "text_unit": unit["text_unit"],
        }))

        annotations.append({
            "text_unit_id": unit["text_unit_id"],
            "primary_issue": parsed["primary_issue"],
            "secondary_issues": parsed.get("secondary_issues", [])[:2],
            "label_source": "model",
            "review_status": "raw",
            "review_note": "",
        })

    return {
        "annotations": annotations,
        "debug_logs": state.get("debug_logs", []) + ["classify_issue: done"]
    }


def classify_sentiment(state: SignalState) -> SignalState:
    unit_map = {u["text_unit_id"]: u for u in state.get("text_units", [])}
    anns = state.get("annotations", [])

    for ann in anns:
        parsed = parse_json_from_llm(sentiment_chain.invoke({
            "text_unit": unit_map[ann["text_unit_id"]]["text_unit"]
        }))
        ann["sentiment_label"] = parsed["sentiment_label"]

    return {
        "annotations": anns,
        "debug_logs": state.get("debug_logs", []) + ["classify_sentiment: done"]
    }


def classify_signal_type(state: SignalState) -> SignalState:
    unit_map = {u["text_unit_id"]: u for u in state.get("text_units", [])}
    anns = state.get("annotations", [])

    for ann in anns:
        parsed = parse_json_from_llm(signal_type_chain.invoke({
            "text_unit": unit_map[ann["text_unit_id"]]["text_unit"]
        }))
        ann["signal_type"] = parsed["signal_type"]

    return {
        "annotations": anns,
        "debug_logs": state.get("debug_logs", []) + ["classify_signal_type: done"]
    }


def classify_severity(state: SignalState) -> SignalState:
    unit_map = {u["text_unit_id"]: u for u in state.get("text_units", [])}
    anns = state.get("annotations", [])

    for ann in anns:
        parsed = parse_json_from_llm(severity_chain.invoke({
            "text_unit": unit_map[ann["text_unit_id"]]["text_unit"]
        }))
        ann["severity_level"] = parsed["severity_level"]

    return {
        "annotations": anns,
        "debug_logs": state.get("debug_logs", []) + ["classify_severity: done"]
    }


def extract_reason_span(state: SignalState) -> SignalState:
    unit_map = {u["text_unit_id"]: u for u in state.get("text_units", [])}
    anns = state.get("annotations", [])

    for ann in anns:
        parsed = parse_json_from_llm(reason_chain.invoke({
            "text_unit": unit_map[ann["text_unit_id"]]["text_unit"],
            "primary_issue": ann["primary_issue"],
            "sentiment_label": ann["sentiment_label"],
            "signal_type": ann["signal_type"],
            "severity_level": ann["severity_level"],
        }))
        ann["reason_span"] = parsed.get("reason_span", "")

    return {
        "annotations": anns,
        "debug_logs": state.get("debug_logs", []) + ["extract_reason_span: done"]
    }


def validate_annotation(state: SignalState) -> SignalState:
    unit_map = {u["text_unit_id"]: u for u in state.get("text_units", [])}
    anns = state.get("annotations", [])

    for ann in anns:
        text_unit = unit_map[ann["text_unit_id"]]["text_unit"]
        ann["confidence_score"] = calc_confidence(ann, text_unit)

        issues = ann.get("secondary_issues", []) or []
        if len(issues) > 2:
            ann["review_note"] = "secondary_issues 초과"
            ann["review_status"] = "needs_review"
            continue

        if ann["confidence_score"] < REVIEW_THRESHOLD:
            ann["review_note"] = "confidence 낮음"
            ann["review_status"] = "needs_review"
        elif not contains_reason_span(text_unit, ann.get("reason_span", "")):
            ann["review_note"] = "reason_span 본문 불일치"
            ann["review_status"] = "needs_review"
        else:
            ann["review_status"] = "auto_labeled"

    return {
        "annotations": anns,
        "debug_logs": state.get("debug_logs", []) + ["validate_annotation: done"]
    }


def route_review(state: SignalState) -> SignalState:
    auto_saved: List[AnnotationRecord] = []
    review_queue: List[AnnotationRecord] = []

    for ann in state.get("annotations", []):
        if ann.get("review_status") == "needs_review":
            review_queue.append(ann)
        else:
            auto_saved.append(ann)

    return {
        "auto_saved": auto_saved,
        "review_queue": review_queue,
        "debug_logs": state.get("debug_logs", []) + [
            f"route_review: auto={len(auto_saved)}, review={len(review_queue)}"
        ]
    }


def save_auto(state: SignalState) -> SignalState:
    # TODO: DB insert / CSV append / Spreadsheet write
    print("\n=== AUTO SAVED ===")
    print(json.dumps(state.get("auto_saved", []), ensure_ascii=False, indent=2))
    return {
        "debug_logs": state.get("debug_logs", []) + ["save_auto: done"]
    }


def save_human_review(state: SignalState) -> SignalState:
    # TODO: human review queue 저장
    print("\n=== REVIEW QUEUE ===")
    print(json.dumps(state.get("review_queue", []), ensure_ascii=False, indent=2))
    return {
        "debug_logs": state.get("debug_logs", []) + ["save_human_review: done"]
    }


def review_router(state: SignalState) -> Literal["save_auto", "save_human_review"]:
    return "save_human_review" if state.get("review_queue") else "save_auto"


# ============================================================
# 5. Graph 빌드
# ============================================================
def build_signal_annotation_engine():
    builder = StateGraph(SignalState)

    builder.add_node("init_article", init_article)
    builder.add_node("split_text_units", split_text_units)
    builder.add_node("classify_issue", classify_issue)
    builder.add_node("classify_sentiment", classify_sentiment)
    builder.add_node("classify_signal_type", classify_signal_type)
    builder.add_node("classify_severity", classify_severity)
    builder.add_node("extract_reason_span", extract_reason_span)
    builder.add_node("validate_annotation", validate_annotation)
    builder.add_node("route_review", route_review)
    builder.add_node("save_auto", save_auto)
    builder.add_node("save_human_review", save_human_review)

    builder.add_edge(START, "init_article")
    builder.add_edge("init_article", "split_text_units")
    builder.add_edge("split_text_units", "classify_issue")
    builder.add_edge("classify_issue", "classify_sentiment")
    builder.add_edge("classify_sentiment", "classify_signal_type")
    builder.add_edge("classify_signal_type", "classify_severity")
    builder.add_edge("classify_severity", "extract_reason_span")
    builder.add_edge("extract_reason_span", "validate_annotation")
    builder.add_edge("validate_annotation", "route_review")
    builder.add_conditional_edges("route_review", review_router)
    builder.add_edge("save_auto", END)
    builder.add_edge("save_human_review", END)

    return builder.compile()


# ============================================================
# 6. 실행 예시
# ============================================================
if __name__ == "__main__":
    engine = build_signal_annotation_engine()

    input_state: SignalState = {
        "source_url": "https://www.impacton.net/news/articleView.html?idxno=18412",
        "source_type": "news",
        "source_name": "IMPACT ON",
        "title": "KT·롯데카드 해킹 사고로 ESG 평가 큰 폭으로 감점",
        "published_at": "2026-04-08",
        "raw_text": (
            "ESG 평가기관 서스틴베스트가 KT와 롯데카드에서 연이어 발생한 해킹 피해와 관련해 "
            "정보보호 리스크의 심각성이 크다고 밝혔다.\n"
            "KT는 고객 개인정보 노출 피해 금액과 피해 고객 규모를 발표했다.\n"
            "롯데카드는 해킹으로 유출된 정보가 200GB에 달한다고 밝혔다."
        ),
    }

    result = engine.invoke(input_state)
    print("\n=== DEBUG LOGS ===")
    print(json.dumps(result.get("debug_logs", []), ensure_ascii=False, indent=2))
