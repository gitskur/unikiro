# Coupa & eProcurement AI 챗봇

Coupa, eProcurement, CSP 문서 기반 RAG 챗봇. AWS 서버리스 + Microsoft Teams 연동.

## 아키텍처

```
[Teams 봇] → [API Gateway] → [Lambda] → Bedrock Claude 3 Haiku
                                  ↕              ↕
                             DynamoDB        S3 + FAISS
                            (대화 로그)    (PDF + 벡터 인덱스)
```

## 사전 요구사항

- AWS CLI v2
- AWS SAM CLI (`brew install aws-sam-cli`)
- Python 3.12+
- AWS 계정 (Bedrock 모델 접근 활성화 필요)

## 빠른 배포

```bash
# 1. AWS 자격 증명 설정
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
export AWS_DEFAULT_REGION="us-east-1"

# 2. 배포 (인프라 생성 + PDF 업로드 + 임베딩 자동 실행)
./deploy.sh
```

## 프로젝트 구조

```
├── template.yaml          # SAM IaC (S3, DynamoDB, Lambda, API Gateway)
├── deploy.sh              # 원클릭 배포 스크립트
├── chatbot_docs/          # PDF 원본 문서
├── lambda/
│   ├── handler.py         # RAG 챗봇 (검색 + Bedrock + 대화 로그)
│   ├── embed.py           # PDF → FAISS 임베딩
│   └── deps/              # Lambda Layer 의존성
└── teams-bot/
    ├── manifest.json      # Teams 앱 매니페스트
    ├── bot.py             # Teams 메시지 처리 + 피드백
    └── app.py             # aiohttp 서버
```

## Teams 봇 설정

1. [Azure Portal](https://portal.azure.com)에서 Bot Service 생성
2. Bot App ID/Password 발급
3. `teams-bot/manifest.json`의 `{{BOT_APP_ID}}` 교체
4. 환경변수 설정 후 실행:
   ```bash
   cd teams-bot
   pip install -r requirements.txt
   BOT_APP_ID=xxx BOT_APP_PASSWORD=xxx CHATBOT_API_URL=https://xxx.execute-api.us-east-1.amazonaws.com/Prod python app.py
   ```
5. Teams Admin Center에서 앱 업로드

## 비용 (200~300명 기준)

| 항목 | 월 예상 비용 |
|------|------------|
| Lambda | ~$0 (프리티어) |
| API Gateway | ~$3~10 |
| Bedrock Claude | ~$30~90 |
| DynamoDB | ~$5 |
| S3 | ~$1 |
| **합계** | **~$35~100** |

## 인프라 삭제

```bash
aws cloudformation delete-stack --stack-name coupa-chatbot --region us-east-1
```
