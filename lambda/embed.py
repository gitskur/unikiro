import json
import os
import boto3
import numpy as np
from io import BytesIO
import base64

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime')
BUCKET = os.environ['DOCS_BUCKET']
EMBED_ID = os.environ.get('EMBED_MODEL_ID', 'amazon.titan-embed-text-v2:0')


def get_embedding(text):
    resp = bedrock.invoke_model(
        modelId=EMBED_ID,
        body=json.dumps({"inputText": text[:8000]}))
    return json.loads(resp['body'].read())['embedding']


def extract_text_from_pdf(pdf_bytes):
    from pypdf import PdfReader
    reader = PdfReader(BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or '' for page in reader.pages)


def chunk_text(text, size=500, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i + size])
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
    return chunks


def _cors():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST,GET,OPTIONS",
        "Content-Type": "application/json; charset=utf-8",
    }


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
    path = event.get("rawPath", "/")

    if method == "OPTIONS":
        return {"statusCode": 200, "headers": _cors(), "body": ""}

    # S3 파일 업로드 엔드포인트
    if path == "/upload" and method == "POST":
        body = json.loads(event.get("body") or "{}")
        key = body.get("key")
        content = body.get("content")
        if not key or content is None:
            return {"statusCode": 400, "headers": _cors(),
                    "body": json.dumps({"error": "key and content required"})}
        s3.put_object(Bucket=BUCKET, Key=key,
                      Body=content.encode("utf-8"), ContentType="text/plain; charset=utf-8")
        return {"statusCode": 200, "headers": _cors(),
                "body": json.dumps({"message": f"Uploaded {key}"})}

    # 임베딩 실행 (기본)
    import faiss

    all_chunks = []

    # 1. PDF 처리
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix='docs/')
    for obj in resp.get('Contents', []):
        if not obj['Key'].endswith('.pdf'):
            continue
        print(f"Processing {obj['Key']}")
        pdf = s3.get_object(Bucket=BUCKET, Key=obj['Key'])['Body'].read()
        text = extract_text_from_pdf(pdf)
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks")

    # 2. process_guide.md 처리
    try:
        obj = s3.get_object(Bucket=BUCKET, Key='knowledge/process_guide.md')
        guide_text = obj['Body'].read().decode('utf-8')
        guide_chunks = chunk_text(guide_text, size=300, overlap=50)
        all_chunks.extend(guide_chunks)
        print(f"process_guide.md → {len(guide_chunks)} chunks")
    except Exception as e:
        print(f"process_guide.md not found: {e}")

    if not all_chunks:
        return {"statusCode": 400, "headers": _cors(),
                "body": json.dumps({"error": "No documents found"})}

    # 임베딩 생성
    print(f"Embedding {len(all_chunks)} chunks...")
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        embeddings.append(get_embedding(chunk))
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(all_chunks)}")

    # FAISS 인덱스 생성 및 S3 저장
    dim = len(embeddings[0])
    vecs = np.array(embeddings, dtype='float32')
    faiss.normalize_L2(vecs)
    index = faiss.IndexFlatIP(dim)
    index.add(vecs)

    faiss.write_index(index, '/tmp/index.bin')
    s3.upload_file('/tmp/index.bin', BUCKET, 'faiss/index.bin')

    with open('/tmp/chunks.json', 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False)
    s3.upload_file('/tmp/chunks.json', BUCKET, 'faiss/chunks.json')

    return {
        "statusCode": 200,
        "headers": _cors(),
        "body": json.dumps({
            "chunks": len(all_chunks),
            "dimension": dim,
            "message": "FAISS index created and uploaded to S3"
        }, ensure_ascii=False)
    }
