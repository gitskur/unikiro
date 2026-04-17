import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import boto3


class Intent(Enum):
    PURCHASE_REQUEST = "purchase_request"      # 구매 요청
    EXPENSE_CLAIM = "expense_claim"            # 비용 처리
    PROCESS_GUIDE = "process_guide"            # 프로세스 안내
    STATUS_CHECK = "status_check"              # 진행 상태 조회
    GENERAL = "general"                        # 일반 문의


@dataclass
class Message:
    role: str   # "user" | "assistant"
    content: str


@dataclass
class ChatSession:
    history: list[Message] = field(default_factory=list)
    last_intent: Optional[Intent] = None

    def add(self, role: str, content: str):
        self.history.append(Message(role, content))

    def get_messages(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.history]


SYSTEM_PROMPT = """당신은 사내 구매/비용처리 프로세스 안내 어시스턴트입니다.
Confluence의 프로세스 문서와 Coupa 구매 시스템을 기반으로 정확한 절차를 안내합니다.

답변 시:
- 단계별로 명확하게 안내하세요
- 관련 시스템(Confluence/Coupa) 링크나 양식을 제시하세요
- 모르는 내용은 솔직하게 모른다고 하세요

[참고 문서]
{context}
"""

INTENT_PROMPT = """다음 사용자 메시지의 의도를 분류하세요. JSON으로만 응답하세요.

의도 목록:
- purchase_request: 구매 요청/발주
- expense_claim: 비용 처리/경비 청구
- process_guide: 프로세스/절차 안내
- status_check: 진행 상태 조회
- general: 기타

메시지: {message}

응답 형식: {{"intent": "...", "confidence": 0.0~1.0}}"""


class ChatEngine:
    def __init__(self, region: str, model_id: str):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id

    def _invoke(self, messages: list[dict], system: str) -> str:
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "system": system,
                "messages": messages,
            }),
        )
        return json.loads(response["body"].read())["content"][0]["text"]

    def classify_intent(self, message: str) -> Intent:
        result = self._invoke(
            messages=[{"role": "user", "content": INTENT_PROMPT.format(message=message)}],
            system="JSON만 반환하는 분류기입니다.",
        )
        try:
            data = json.loads(result)
            return Intent(data["intent"])
        except (json.JSONDecodeError, KeyError, ValueError):
            return Intent.GENERAL

    def chat(self, session: ChatSession, user_message: str, context: str = "") -> str:
        intent = self.classify_intent(user_message)
        session.last_intent = intent

        session.add("user", user_message)

        system = SYSTEM_PROMPT.format(context=context or "제공된 문서 없음")
        answer = self._invoke(session.get_messages(), system)

        session.add("assistant", answer)
        return answer
