"""
Coupa REST API 클라이언트.
- 인증: X-COUPA-API-KEY 헤더
- 응답: JSON (Accept: application/json)
- 계약 주요 필드: id, name, status, start_date, stop_date,
                  contract-owner(id, email, fullname),
                  supplier(id, name, primary_address),
                  currency(code), max_commit, description
"""
import json
import urllib.request
import urllib.parse
from datetime import date, timedelta
from common.config import COUPA_BASE_URL, COUPA_API_KEY

# 필요한 필드만 요청해 응답 크기 최소화
_CONTRACT_FIELDS = (
    "id,name,status,start_date,stop_date,description,"
    "contract-owner[id,email,fullname],"
    "supplier[id,name],"
    "currency[code],"
    "max_commit"
)


def _get(path: str, params: dict | None = None) -> list | dict:
    params = params or {}
    params["fields"] = _CONTRACT_FIELDS
    url = f"{COUPA_BASE_URL}{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "X-COUPA-API-KEY": COUPA_API_KEY,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def get_contract(contract_id: str | int) -> dict:
    """단일 계약 조회. 반환 예시:
    {
      "id": 123, "name": "SW 라이선스 계약", "status": "active",
      "start_date": "2024-01-01", "stop_date": "2026-06-30",
      "contract-owner": {"id": 5, "email": "user@company.com", "fullname": "홍길동"},
      "supplier": {"id": 10, "name": "ABC Corp"},
      "currency": {"code": "KRW"}, "max_commit": "10000000.0"
    }
    """
    return _get(f"/api/contracts/{contract_id}")


def get_expiring_contracts(days: int = 60) -> list[dict]:
    """stop_date가 오늘~days일 이내인 active 계약 목록.
    Coupa 쿼리: stop_date[lt]=YYYY-MM-DD&status=active
    """
    cutoff = (date.today() + timedelta(days=days)).isoformat()
    today = date.today().isoformat()
    return _get("/api/contracts", {
        "status": "active",
        "stop_date[gt_or_eq]": today,
        "stop_date[lt_or_eq]": cutoff,
    })


def search_contracts(keyword: str, limit: int = 5) -> list[dict]:
    """계약명 또는 공급업체명으로 계약 검색."""
    return _get("/api/contracts", {"name[contains]": keyword, "per_page": limit})


# PO 조회용 필드
_PO_FIELDS = (
    "id,po-number,status,order-date,total,currency[code],"
    "supplier[id,name],"
    "requisition-header[id,status]"
)


def get_pos_by_contract(contract_id: str | int) -> list[dict]:
    """계약 ID에 연결된 PO 목록 조회.
    Coupa PO 주요 필드:
    - id, po-number, status (issued/draft/pending_approval/cancelled)
    - order-date, total, currency
    - supplier
    """
    return _get("/api/purchase_orders", {
        "contract[id]": contract_id,
        "fields": _PO_FIELDS,
    })


def get_po(po_id: str | int) -> dict:
    """단일 PO 조회."""
    params = {"fields": _PO_FIELDS}
    url = f"{COUPA_BASE_URL}/api/purchase_orders/{po_id}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "X-COUPA-API-KEY": COUPA_API_KEY,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())
