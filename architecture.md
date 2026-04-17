# Coupa × Teams 연동 챗봇 아키텍처

## 1. 전체 시스템 구성

```mermaid
graph TB
    subgraph Teams["💬 Microsoft Teams"]
        U[사용자]
        CH[팀 채널]
    end

    subgraph AWS["☁️ AWS"]
        BOT["Lambda 1\nTeams Bot Handler"]
        SCH["Lambda 2\nContract Scheduler"]
        WHK["Lambda 3\nCoupa Webhook Handler"]
        EB["EventBridge\n매일 00:00 UTC"]
        DB["DynamoDB\nChannelMapping\n(email → webhook URL)"]
        BR["Amazon Bedrock\nClaude 3.5 Sonnet"]
        SSM["SSM Parameter Store\n(API Keys)"]
    end

    subgraph Coupa["🛒 Coupa"]
        CAPI["Coupa REST API\n(/api/contracts)"]
        CWH["Coupa Webhook\n(상태변경 이벤트)"]
    end

    U -- "①멘션 질문" --> BOT
    BOT -- "②계약 조회" --> CAPI
    BOT -- "③RAG 답변 생성" --> BR
    BOT -- "④답변" --> U

    EB -- "매일 트리거" --> SCH
    SCH -- "⑤D-60 계약 조회" --> CAPI
    SCH -- "⑥webhook URL 조회" --> DB
    SCH -- "⑦만료 알림" --> CH

    CWH -- "상태변경 POST" --> WHK
    WHK -- "⑧webhook URL 조회" --> DB
    WHK -- "⑨상태변경 알림" --> CH

    BOT & SCH & WHK --> SSM
```

---

## 2. Lambda 1 - Teams Bot (질의응답)

```mermaid
sequenceDiagram
    actor User as 사용자 (Teams)
    participant Bot as Lambda 1
    participant Coupa as Coupa API
    participant Bedrock as Amazon Bedrock

    User->>Bot: @봇 "123번 계약 만료일이 언제야?"
    Bot->>Bot: 멘션 태그 제거 / 숫자 ID 추출
    Bot->>Coupa: GET /api/contracts/123
    Coupa-->>Bot: 계약 데이터 (name, status, stop_date, owner...)
    Bot->>Bedrock: 질문 + 계약 데이터 → 답변 생성
    Bedrock-->>Bot: "123번 계약은 2026-06-30 만료입니다..."
    Bot->>User: Teams 답변 전송 (Bot Framework API)
```

---

## 3. Lambda 2 - 계약 만료 스케줄러 (D-60 알림)

```mermaid
sequenceDiagram
    participant EB as EventBridge (매일)
    participant SCH as Lambda 2
    participant Coupa as Coupa API
    participant DB as DynamoDB
    participant Teams as Teams 채널

    EB->>SCH: 매일 오전 9시 KST 트리거
    SCH->>Coupa: GET /api/contracts?status=active&stop_date[lt_or_eq]=D+60
    Coupa-->>SCH: 만료 임박 계약 목록
    loop 계약별
        SCH->>DB: get_item(email=담당자이메일)
        DB-->>SCH: webhook URL
        SCH->>Teams: Adaptive Card 알림 전송
    end
```

---

## 4. Lambda 3 - Coupa 상태변경 알림

```mermaid
sequenceDiagram
    participant Coupa as Coupa
    participant WHK as Lambda 3
    participant DB as DynamoDB
    participant Teams as Teams 채널

    Coupa->>WHK: POST /coupa/webhook (계약 객체)
    WHK->>WHK: status 필터\n(approved/rejected/cancelled/pending_approval)
    WHK->>DB: get_item(email=담당자이메일)
    DB-->>WHK: webhook URL
    WHK->>Teams: Adaptive Card 알림\n(✅승인 / ❌거절 / 🚫반려 / 🕐검토중)
```

---

## 5. DynamoDB 채널 매핑 구조

```
ChannelMapping 테이블
┌─────────────────────────┬──────────────────────────────────────┬──────────────┐
│ email (PK)              │ webhook_url                          │ channel_name │
├─────────────────────────┼──────────────────────────────────────┼──────────────┤
│ hong@company.com        │ https://xxx.webhook.office.com/...   │ 구매팀       │
│ kim@company.com         │ https://yyy.webhook.office.com/...   │ IT팀         │
│ lee@company.com         │ https://zzz.webhook.office.com/...   │ 재무팀       │
└─────────────────────────┴──────────────────────────────────────┴──────────────┘
  ↑ 계약 담당자 이메일로 조회 → 해당 팀 채널로 알림 전송
  ↑ 매핑 없으면 TEAMS_DEFAULT_WEBHOOK_URL로 fallback
```

---

## 6. Teams 알림 메시지 예시

### 만료 알림 (D-60)
```
⚠️ 계약 만료 60일 전 알림
아래 계약이 60일 이내 만료됩니다. 갱신 여부를 검토해주세요.

계약명    | SW 라이선스 계약
계약번호  | 123
만료일    | 2026-06-30
담당자    | 홍길동
공급업체  | ABC Corp
```

### 상태변경 알림
```
✅ 계약 승인
계약이 승인되었습니다.

계약명        | SW 라이선스 계약
계약번호      | 123
만료일        | 2026-06-30
담당자        | 홍길동
담당자 이메일 | hong@company.com
공급업체      | ABC Corp
```
