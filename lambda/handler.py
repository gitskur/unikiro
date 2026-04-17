import json
import os
import boto3
import numpy as np
from datetime import datetime

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CHAT_TABLE'])
BUCKET = os.environ['DOCS_BUCKET']
MODEL_ID = os.environ['BEDROCK_MODEL_ID']
EMBED_ID = os.environ['EMBED_MODEL_ID']

# FAISS 인덱스와 텍스트 청크를 메모리에 캐싱 (Lambda warm start 활용)
_index = None
_chunks = None


def get_embedding(text):
    resp = bedrock.invoke_model(
        modelId=EMBED_ID,
        body=json.dumps({"inputText": text[:8000]}))
    return json.loads(resp['body'].read())['embedding']


def load_index():
    global _index, _chunks
    if _index is not None:
        return
    import faiss
    s3.download_file(BUCKET, 'faiss/index.bin', '/tmp/index.bin')
    s3.download_file(BUCKET, 'faiss/chunks.json', '/tmp/chunks.json')
    _index = faiss.read_index('/tmp/index.bin')
    with open('/tmp/chunks.json') as f:
        _chunks = json.load(f)


def search(query, k=5):
    load_index()
    import faiss
    vec = np.array([get_embedding(query)], dtype='float32')
    faiss.normalize_L2(vec)
    scores, ids = _index.search(vec, k)
    return [_chunks[i] for i in ids[0] if i < len(_chunks)]


def ask_bedrock(query, context, history):
    history_text = "\n".join([f"User: {h['q']}\nBot: {h['a']}" for h in history[-3:]])
    prompt = f"""다음 문서 내용을 기반으로 질문에 한국어로 답변하세요. 문서에 없는 내용은 "해당 정보를 찾을 수 없습니다"라고 답하세요.

<documents>
{context}
</documents>

<history>
{history_text}
</history>

질문: {query}"""

    resp = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }))
    return json.loads(resp['body'].read())['content'][0]['text']


def get_history(user_id, limit=3):
    resp = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id),
        ScanIndexForward=False, Limit=limit)
    items = resp.get('Items', [])
    return [{'q': i['question'], 'a': i['answer']} for i in reversed(items)]


def save_log(user_id, question, answer, feedback=None):
    table.put_item(Item={
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'question': question,
        'answer': answer,
        'feedback': feedback
    })


def lambda_handler(event, context):
    # Health check
    if event.get('httpMethod') == 'GET':
        return {'statusCode': 200, 'body': json.dumps({'status': 'ok'})}

    body = json.loads(event.get('body', '{}'))
    query = body.get('message', '')
    user_id = body.get('user_id', 'anonymous')
    feedback = body.get('feedback')

    # 피드백 저장만
    if feedback and body.get('timestamp'):
        table.update_item(
            Key={'user_id': user_id, 'timestamp': body['timestamp']},
            UpdateExpression='SET feedback = :f',
            ExpressionAttributeValues={':f': feedback})
        return {'statusCode': 200, 'body': json.dumps({'status': 'feedback saved'})}

    if not query:
        return {'statusCode': 400, 'body': json.dumps({'error': 'message required'})}

    # RAG 파이프라인
    docs = search(query)
    context_text = "\n---\n".join(docs)
    history = get_history(user_id)
    answer = ask_bedrock(query, context_text, history)
    ts = datetime.utcnow().isoformat()
    save_log(user_id, query, answer)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'answer': answer, 'timestamp': ts, 'sources': docs[:2]}, ensure_ascii=False)
    }
