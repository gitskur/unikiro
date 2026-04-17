"""
Confluence / Coupa 연동 stub.
실제 API 연동 시 각 메서드 내부를 구현하세요.
"""
from dataclasses import dataclass


@dataclass
class Document:
    title: str
    content: str
    url: str


class ConfluenceClient:
    def __init__(self, base_url: str, username: str, api_token: str, space_key: str):
        self.base_url = base_url
        self.space_key = space_key
        # TODO: self.client = Confluence(url=base_url, username=username, password=api_token)

    def search(self, query: str, limit: int = 3) -> list[Document]:
        """CQL로 관련 문서를 검색합니다."""
        # TODO: results = self.client.cql(f'space="{self.space_key}" AND text~"{query}"', limit=limit)
        return [
            Document(
                title="[stub] 구매 요청 프로세스",
                content="1. Coupa에서 구매 요청서 작성 → 2. 팀장 승인 → 3. 구매팀 발주",
                url=f"{self.base_url}/wiki/spaces/{self.space_key}/pages/stub",
            )
        ]


class CoupaClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"X-COUPA-API-KEY": api_key, "Accept": "application/json"}

    def get_requisition_status(self, requisition_id: str) -> dict:
        """구매 요청 상태를 조회합니다."""
        # TODO: requests.get(f"{self.base_url}/api/requisitions/{requisition_id}", headers=self.headers)
        return {"id": requisition_id, "status": "stub_pending", "approver": "홍길동"}

    def get_expense_status(self, expense_id: str) -> dict:
        """비용 처리 상태를 조회합니다."""
        # TODO: requests.get(f"{self.base_url}/api/expense_reports/{expense_id}", headers=self.headers)
        return {"id": expense_id, "status": "stub_approved", "amount": 0}
