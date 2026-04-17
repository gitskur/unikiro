"""
Lambda 1: Teams Bot Handler
Teams 멘션 메시지 수신 → Coupa 계약 데이터 조회 → Bedrock 답변 → Teams 회신
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3
from common.config import BEDROCK_MODEL_ID, AWS_REGION
from common.coupa_client import get_contract, search_contracts, get_pos_by_contract

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Lambda 패키징 시 함께 포함된 프로세스 가이드 문서 로드
_GUIDE_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "process_guide.md")
try:
    with open(_GUIDE_PATH, encoding="utf-8") as f:
        _PROCESS_GUIDE = f.read()
except FileNotFoundError:
    _PROCESS_GUIDE = ""

SYSTEM_PROMPT = """당신은 사내 구매/비용처리 프로세스 안내 및 Coupa 시스템 어시스턴트입니다.
아래 [프로세스 가이드]와 [계약 데이터]를 우선 참고하여 정확히 답변하세요.
모르는 내용은 솔직히 모른다고 하고 담당자 문의를 안내하세요.

[프로세스 가이드]
{process_guide}

[계약 데이터 - Coupa]
{coupa_context}"""

ANALYSIS_PROMPT = """당신은 사내 구매/계약 전문 어시스턴트입니다.
아래 [프로세스 가이드]와 [계약 데이터]를 바탕으로 이 계약에 대한 실용적인 조언을 제공하세요.

다음 항목을 중심으로 분석하세요:
1. 만료일 임박 여부 및 갱신 필요성
2. 결재 라인 적정성 (금액 대비 On/Off-Budget 기준)
3. 누락된 정보나 주의해야 할 사항
4. 다음 액션 추천

[프로세스 가이드]
{process_guide}

[계약 데이터]
{contract_data}"""


def _ask_bedrock(question: str, coupa_context: str) -> str:
    resp = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT.format(
                process_guide=_PROCESS_GUIDE or "없음",
                coupa_context=coupa_context or "없음",
            ),
            "messages": [{"role": "user", "content": question}],
        }),
    )
    return json.loads(resp["body"].read())["content"][0]["text"]


def _analyze_contract(contract_id: str) -> str:
    """Coupa 계약 데이터를 조회해 Claude로 분석 조언 생성."""
    try:
        c = get_contract(contract_id)
    except Exception:
        return "계약 정보를 불러올 수 없습니다. 계약 번호 또는 접근 권한을 확인해주세요."

    owner = c.get("contract-owner") or {}
    supplier = c.get("supplier") or {}
    from datetime import date
    stop_date = c.get("stop_date", "")
    days_left = None
    if stop_date:
        try:
            days_left = (date.fromisoformat(stop_date) - date.today()).days
        except ValueError:
            pass

    contract_data = (
        f"계약명: {c.get('name')} | 상태: {c.get('status')}\n"
        f"기간: {c.get('start_date')} ~ {stop_date}"
        + (f" (D-{days_left})" if days_left is not None else "") + "\n"
        f"담당자: {owner.get('fullname')} ({owner.get('email')})\n"
        f"공급업체: {supplier.get('name')}\n"
        f"금액: {c.get('max_commit')} {(c.get('currency') or {}).get('code', '')}\n"
        f"설명: {c.get('description', '없음')}"
    )

    resp = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": ANALYSIS_PROMPT.format(
                process_guide=_PROCESS_GUIDE or "없음",
                contract_data=contract_data,
            ),
            "messages": [{"role": "user", "content": "이 계약을 분석하고 조언해줘."}],
        }),
    )
    return json.loads(resp["body"].read())["content"][0]["text"]


def _extract_coupa_contract_id(text: str) -> str | None:
    """Coupa 계약 URL 또는 텍스트에서 계약 ID 추출.
    예: https://company.coupahost.com/contracts/123
        https://company.coupahost.com/contracts/123/edit
    """
    match = re.search(r"coupahost\.com/contracts/(\d+)", text)
    if match:
        return match.group(1)
    return None


PO_KEYWORDS = {"po", "발주", "purchase order", "발주서", "po 발행", "발행"}


def _build_coupa_context(text: str) -> str:
    text_lower = text.lower()
    ids = re.findall(r"\b(\d{3,})\b", text)

    # PO 관련 질문 감지
    if any(kw in text_lower for kw in PO_KEYWORDS):
        if ids:
            try:
                pos = get_pos_by_contract(ids[0])
                if not pos:
                    return f"계약 #{ids[0]}에 연결된 PO가 없습니다."
                lines = ["[PO 발행 현황]"]
                for po in pos:
                    currency = (po.get("currency") or {}).get("code", "")
                    lines.append(
                        f"- PO #{po.get('po-number', po.get('id'))} | "
                        f"상태: {po.get('status')} | "
                        f"발주일: {po.get('order-date', '-')} | "
                        f"금액: {po.get('total', '-')} {currency}"
                    )
                return "\n".join(lines)
            except Exception:
                return "PO 정보를 불러오는 중 오류가 발생했습니다."
        return "PO를 조회하려면 계약 번호를 함께 알려주세요. 예: '123번 계약 PO 발행됐어?'"

    # 계약 ID 직접 조회
    if ids:
        try:
            c = get_contract(ids[0])
            owner = c.get("contract-owner") or {}
            supplier = c.get("supplier") or {}
            return (
                f"계약명: {c.get('name')} | 상태: {c.get('status')}\n"
                f"기간: {c.get('start_date')} ~ {c.get('stop_date')}\n"
                f"담당자: {owner.get('fullname')} ({owner.get('email')})\n"
                f"공급업체: {supplier.get('name')} | "
                f"금액: {c.get('max_commit')} {(c.get('currency') or {}).get('code', '')}"
            )
        except Exception:
            pass

    # 키워드 검색 fallback
    try:
        results = search_contracts(text[:30], limit=3)
        if not results:
            return ""
        lines = ["[유사 계약 검색 결과 - 참고용]"]
        for c in results:
            owner = c.get("contract-owner") or {}
            lines.append(
                f"- [{c.get('id')}] {c.get('name')} | {c.get('status')} | "
                f"만료: {c.get('stop_date')} | 담당자: {owner.get('fullname')}"
            )
        lines.append("위 유사 계약을 Coupa에서 참고하면 도움이 될 수 있습니다.")
        return "\n".join(lines)
    except Exception:
        return ""


def _reply_to_teams(activity: dict, answer: str) -> None:
    service_url = activity.get("serviceUrl", "").rstrip("/")
    conversation_id = activity["conversation"]["id"]
    activity_id = activity["id"]

    token_data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": os.environ["TEAMS_BOT_APP_ID"],
        "client_secret": os.environ["TEAMS_BOT_APP_PASSWORD"],
        "scope": "https://api.botframework.com/.default",
    }).encode()

    req = urllib.request.Request(
        "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token",
        data=token_data,
    )
    with urllib.request.urlopen(req) as r:
        token = json.loads(r.read())["access_token"]

    reply_url = f"{service_url}/v3/conversations/{conversation_id}/activities/{activity_id}"
    req = urllib.request.Request(
        reply_url,
        data=json.dumps({"type": "message", "text": answer, "replyToId": activity_id}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req)


def handler(event, context):
    body = json.loads(event.get("body") or "{}")

    if body.get("type") == "invoke":
        return {"statusCode": 200, "body": "{}"}
    if body.get("type") != "message":
        return {"statusCode": 200, "body": "ok"}

    text = re.sub(r"<at>[^<]+</at>", "", body.get("text", "")).strip()
    if not text:
        return {"statusCode": 200, "body": "ok"}

    # Coupa 계약 URL 감지 → 계약 분석 모드
    contract_id = _extract_coupa_contract_id(text)
    if contract_id:
        answer = _analyze_contract(contract_id)
    else:
        answer = _ask_bedrock(text, _build_coupa_context(text))
    _reply_to_teams(body, answer)
    return {"statusCode": 200, "body": "ok"}
