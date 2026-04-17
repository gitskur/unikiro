"""
Lambda 3: Coupa Webhook 수신 → Teams 알림

처리하는 이벤트:
1. 계약 상태변경 (POST /coupa/webhook)
   payload: 계약 객체 (status: approved/rejected/cancelled/pending_approval)

2. 단계별 승인 이벤트 (POST /coupa/approval-webhook)
   payload: Approvals 객체
   {
     "id": 55,
     "status": "approved" | "rejected" | "pending_approval",
     "approver": {"id": 3, "email": "manager@company.com", "fullname": "김팀장"},
     "approvable-type": "Contract",
     "approvable-id": 123,
     "position": 1,          ← 몇 번째 승인 단계인지
     "updated-at": "2026-04-17T10:00:00+09:00"
   }
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.teams_client import send_message
from common.channel_mapper import get_webhook_url

# 계약 최종 상태 알림
CONTRACT_STATUS_MAP = {
    "approved":         ("✅ 계약 최종 승인",  "계약이 **최종 승인**되었습니다."),
    "rejected":         ("❌ 계약 거절",       "계약이 **거절**되었습니다. 사유를 확인하세요."),
    "cancelled":        ("🚫 계약 반려",       "계약이 **반려**되었습니다."),
    "pending_approval": ("🕐 계약 검토 중",    "계약이 승인 대기 상태로 변경되었습니다."),
}

# 단계별 승인 알림
APPROVAL_STATUS_MAP = {
    "approved":         "✅ 승인 완료",
    "rejected":         "❌ 반려",
    "pending_approval": "🕐 승인 대기",
}

NOTIFY_CONTRACT_STATUSES  = {"approved", "rejected", "cancelled", "pending_approval"}
NOTIFY_APPROVAL_STATUSES  = {"approved", "rejected"}


def _get_webhook_by_email(email: str) -> str:
    return get_webhook_url(email) or os.environ.get("TEAMS_DEFAULT_WEBHOOK_URL", "")


def _handle_contract(contract: dict) -> dict:
    """계약 최종 상태변경 알림."""
    status = str(contract.get("status", "")).lower()
    if status not in NOTIFY_CONTRACT_STATUSES:
        return {"statusCode": 200, "body": "ignored"}

    owner = contract.get("contract-owner") or {}
    webhook_url = _get_webhook_by_email(owner.get("email", ""))
    if not webhook_url:
        return {"statusCode": 200, "body": "no webhook"}

    title, text = CONTRACT_STATUS_MAP[status]
    supplier = contract.get("supplier") or {}
    send_message(
        webhook_url=webhook_url,
        title=title,
        text=text,
        facts=[
            {"title": "계약명",       "value": contract.get("name", "-")},
            {"title": "계약번호",     "value": str(contract.get("id", "-"))},
            {"title": "만료일",       "value": contract.get("stop_date", "-")},
            {"title": "담당자",       "value": owner.get("fullname", "-")},
            {"title": "담당자 이메일","value": owner.get("email", "-")},
            {"title": "공급업체",     "value": supplier.get("name", "-")},
        ],
    )
    return {"statusCode": 200, "body": "ok"}


def _handle_approval(approval: dict) -> dict:
    """단계별 승인 이벤트 알림.
    
    Coupa Approvals 객체 주요 필드:
    - id: approval ID
    - status: approved | rejected | pending_approval
    - approver: 승인자 정보 {email, fullname}
    - approvable-type: "Contract" | "RequisitionHeader" 등
    - approvable-id: 계약/구매요청 ID
    - position: 승인 단계 순서 (1=1차, 2=2차 ...)
    """
    status = str(approval.get("status", "")).lower()
    if status not in NOTIFY_APPROVAL_STATUSES:
        return {"statusCode": 200, "body": "ignored"}

    approver   = approval.get("approver") or {}
    position   = approval.get("position", "-")
    obj_type   = approval.get("approvable-type", "문서")
    obj_id     = approval.get("approvable-id", "-")

    # 알림 대상: 승인자 채널 (승인 완료/반려 사실을 계약 담당자에게도 알려야 하면
    # approvable-id로 계약 조회 후 contract-owner 이메일 추가 가능)
    webhook_url = _get_webhook_by_email(approver.get("email", ""))
    if not webhook_url:
        return {"statusCode": 200, "body": "no webhook"}

    status_label = APPROVAL_STATUS_MAP[status]
    send_message(
        webhook_url=webhook_url,
        title=f"{status_label} — {position}차 승인",
        text=f"**{position}차 승인**이 {status_label} 처리되었습니다.",
        facts=[
            {"title": "대상",     "value": f"{obj_type} #{obj_id}"},
            {"title": "승인 단계","value": f"{position}차"},
            {"title": "승인자",   "value": approver.get("fullname", "-")},
            {"title": "처리",     "value": status_label},
        ],
    )
    return {"statusCode": 200, "body": "ok"}


def handler(event, context):
    body = json.loads(event.get("body") or "{}")
    path = event.get("path", "") or event.get("rawPath", "")

    if "approval-webhook" in path:
        return _handle_approval(body)
    return _handle_contract(body)
