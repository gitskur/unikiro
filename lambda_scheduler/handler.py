"""
Lambda 2: 계약 만료 스케줄러
EventBridge로 매일 실행 → D-60 계약 조회 → 담당자 + 팀 채널에 Teams 알림
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.coupa_client import get_expiring_contracts
from common.teams_client import send_message
from common.channel_mapper import get_webhook_url


def _get_webhook(contract: dict) -> str:
    email = (contract.get("contract-owner") or {}).get("email", "")
    return get_webhook_url(email) or os.environ.get("TEAMS_DEFAULT_WEBHOOK_URL", "")


def handler(event, context):
    contracts = get_expiring_contracts(days=60)
    notified = 0

    for c in contracts:
        webhook_url = _get_webhook(c)
        if not webhook_url:
            continue

        owner = c.get("contract-owner") or {}
        send_message(
            webhook_url=webhook_url,
            title="⚠️ 계약 만료 60일 전 알림",
            text=f"아래 계약이 **60일 이내** 만료됩니다. 갱신 여부를 검토해주세요.",
            facts=[
                {"title": "계약명", "value": c.get("name", "-")},
                {"title": "계약번호", "value": str(c.get("id", "-"))},
                {"title": "만료일", "value": c.get("stop_date", "-")},
                {"title": "담당자", "value": owner.get("fullname", "-")},
                {"title": "공급업체", "value": c.get("supplier", {}).get("name", "-")},
            ],
        )
        notified += 1

    print(f"[scheduler] 만료 임박 계약 {notified}건 알림 전송 완료")
    return {"notified": notified}
