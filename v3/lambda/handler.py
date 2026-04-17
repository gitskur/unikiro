"""
Coupa AI Chatbot v3 - 통합 Lambda Bot Handler
- FAISS RAG 벡터 검색 (PDF 문서 기반)
- Coupa REST API 실시간 계약/PO 조회
- Teams Bot Framework 웹훅
- DynamoDB 대화 기억
- 의도 분류 (프로세스 안내 / 계약 조회 / PO 조회 / 일반)
- knowledge/process_guide.md 참조
"""
import json
import os
import re
import boto3
import numpy as np
from datetime import datetime

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["CHAT_TABLE"])

BUCKET = os.environ["DOCS_BUCKET"]
MODEL_ID = os.environ["BEDROCK_MODEL_ID"]
EMBED_ID = os.environ["EMBED_MODEL_ID"]
COUPA_BASE_URL = os.environ.get("COUPA_BASE_URL", "")
COUPA_API_KEY = os.environ.get("COUPA_API_KEY", "")

_index = None
_chunks = None
_process_guide = None

SYSTEM_PROMPT = """당신은 Coupa 구매/계약 프로세스 안내 챗봇입니다.
아래 [프로세스 가이드]와 [문서/계약 데이터]를 우선 참고하여 정확히 답변하세요.
문서에 없는 내용은 "해당 정보를 찾을 수 없습니다. 담당 부서에 확인이 필요합니다."라고 답하세요.
답변은 한국어, 마크다운 형식으로 작성하세요.

[프로세스 가이드]
{process_guide}"""


# ── 프로세스 가이드 로딩 ─────────────────────────────────────────────────

def get_process_guide():
    global _process_guide
    if _process_guide is not None:
        return _process_guide
    try:
        obj = s3.get_object(Bucket=BUCKET, Key="knowledge/process_guide.md")
        _process_guide = obj["Body"].read().decode("utf-8")
    except Exception:
        _process_guide = ""
    return _process_guide


# ── FAISS 벡터 검색 ─────────────────────────────────────────────────────

def get_embedding(text):
    resp = bedrock.invoke_model(
        modelId=EMBED_ID, body=json.dumps({"inputText": text[:8000]})
    )
    return json.loads(resp["body"].read())["embedding"]


def load_index():
    global _index, _chunks
    if _index is not None:
        return
    import faiss
    s3.download_file(BUCKET, "faiss/index.bin", "/tmp/index.bin")
    s3.download_file(BUCKET, "faiss/chunks.json", "/tmp/chunks.json")
    _index = faiss.read_index("/tmp/index.bin")
    with open("/tmp/chunks.json") as f:
        _chunks = json.load(f)


def search_docs(query, k=5):
    load_index()
    import faiss
    vec = np.array([get_embedding(query)], dtype="float32")
    faiss.normalize_L2(vec)
    _, ids = _index.search(vec, k)
    return [_chunks[i] for i in ids[0] if i < len(_chunks)]


# ── Coupa API 연동 ──────────────────────────────────────────────────────

def _coupa_get(path, params=None):
    if not COUPA_BASE_URL or not COUPA_API_KEY:
        return None
    import urllib.request, urllib.parse
    params = params or {}
    url = f"{COUPA_BASE_URL}{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "X-COUPA-API-KEY": COUPA_API_KEY, "Accept": "application/json"
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def get_coupa_context(text):
    """텍스트에서 계약 ID를 추출하고 Coupa 데이터를 조회."""
    if not COUPA_BASE_URL:
        return ""
    ids = re.findall(r"\b(\d{3,})\b", text)
    if not ids:
        return ""
    try:
        c = _coupa_get(f"/api/contracts/{ids[0]}")
        if not c:
            return ""
        owner = c.get("contract-owner") or {}
        supplier = c.get("supplier") or {}
        return (
            f"[Coupa 계약 데이터]\n"
            f"계약명: {c.get('name')} | 상태: {c.get('status')}\n"
            f"기간: {c.get('start_date')} ~ {c.get('stop_date')}\n"
            f"담당자: {owner.get('fullname')} ({owner.get('email')})\n"
            f"공급업체: {supplier.get('name')} | "
            f"금액: {c.get('max_commit')} {(c.get('currency') or {}).get('code', '')}"
        )
    except Exception:
        return ""


# ── Bedrock 호출 ────────────────────────────────────────────────────────

def ask_bedrock(query, context, history):
    history_text = "\n".join(
        [f"User: {h['q']}\nBot: {h['a']}" for h in history[-3:]]
    )
    system = SYSTEM_PROMPT.format(process_guide=get_process_guide() or "없음")
    prompt = f"""{system}

<documents>
{context}
</documents>

<history>
{history_text}
</history>

질문: {query}"""

    resp = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({"messages": [{"role": "user", "content": [{"text": prompt}]}]}),
    )
    return json.loads(resp["body"].read())["output"]["message"]["content"][0]["text"]


# ── DynamoDB 대화 기억 ──────────────────────────────────────────────────

def get_history(user_id, limit=3):
    resp = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id),
        ScanIndexForward=False, Limit=limit,
    )
    return [{"q": i["question"], "a": i["answer"]} for i in reversed(resp.get("Items", []))]


def save_log(user_id, question, answer):
    table.put_item(Item={
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer,
    })


# ── 통합 RAG + Coupa 파이프라인 ─────────────────────────────────────────

def rag_answer(query, user_id="anonymous"):
    # FAISS 문서 검색
    docs = search_docs(query)
    doc_context = "\n---\n".join(docs)

    # Coupa 실시간 데이터 (계약 ID가 있으면)
    coupa_context = get_coupa_context(query)
    if coupa_context:
        doc_context = coupa_context + "\n\n" + doc_context

    history = get_history(user_id)
    answer = ask_bedrock(query, doc_context, history)
    save_log(user_id, query, answer)
    return answer, docs


# ── 응답 헬퍼 ───────────────────────────────────────────────────────────

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,GET,OPTIONS",
}


def _resp(code, body):
    return {"statusCode": code, "headers": CORS_HEADERS, "body": body}


# ── Teams 웹훅 핸들러 ───────────────────────────────────────────────────

def handle_teams(activity):
    if activity.get("type") != "message":
        return _resp(200, "")
    # 멘션 태그 제거
    text = re.sub(r"<at>[^<]+</at>", "", activity.get("text") or "").strip()
    if not text:
        return _resp(200, "")

    user_id = f"teams-{activity.get('from', {}).get('id', 'unknown')}"
    try:
        answer, _ = rag_answer(text, user_id)
    except Exception as e:
        answer = f"오류가 발생했습니다: {e}"

    reply = {
        "type": "message", "text": answer,
        "textFormat": "markdown", "replyToId": activity.get("id"),
    }
    return _resp(200, json.dumps(reply, ensure_ascii=False))


# ── Lambda 핸들러 ───────────────────────────────────────────────────────

def lambda_handler(event, context):
    method = event.get("httpMethod", "POST")
    path = event.get("path", "/")

    if method == "OPTIONS":
        return _resp(200, "")
    if method == "GET":
        return _resp(200, json.dumps({"status": "ok"}))

    body = json.loads(event.get("body") or "{}")

    # Teams 웹훅
    if path.endswith("/teams"):
        return handle_teams(body)

    # 피드백
    if body.get("feedback") and body.get("timestamp"):
        table.update_item(
            Key={"user_id": body.get("user_id", "anonymous"), "timestamp": body["timestamp"]},
            UpdateExpression="SET feedback = :f",
            ExpressionAttributeValues={":f": body["feedback"]},
        )
        return _resp(200, json.dumps({"status": "feedback saved"}))

    # 채팅
    query = body.get("message", "")
    if not query:
        return _resp(400, json.dumps({"error": "message required"}))

    user_id = body.get("user_id", "anonymous")
    try:
        answer, docs = rag_answer(query, user_id)
        return _resp(200, json.dumps(
            {"answer": answer, "timestamp": datetime.utcnow().isoformat(), "sources": docs[:2]},
            ensure_ascii=False,
        ))
    except Exception as e:
        return _resp(500, json.dumps({"error": str(e)}))
