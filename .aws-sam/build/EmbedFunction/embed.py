import json
import os
import boto3
import numpy as np
from io import BytesIO

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


def lambda_handler(event, context):
    import faiss

    # S3에서 모든 PDF 가져오기
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix='docs/')
    all_chunks = []

    for obj in resp.get('Contents', []):
        if not obj['Key'].endswith('.pdf'):
            continue
        print(f"Processing {obj['Key']}")
        pdf = s3.get_object(Bucket=BUCKET, Key=obj['Key'])['Body'].read()
        text = extract_text_from_pdf(pdf)
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks")

    if not all_chunks:
        return {'statusCode': 400, 'body': 'No PDF files found in docs/'}

    # 임베딩 생성
    print(f"Embedding {len(all_chunks)} chunks...")
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        embeddings.append(get_embedding(chunk))
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(all_chunks)}")

    # FAISS 인덱스 생성
    dim = len(embeddings[0])
    vecs = np.array(embeddings, dtype='float32')
    faiss.normalize_L2(vecs)
    index = faiss.IndexFlatIP(dim)
    index.add(vecs)

    # S3에 저장
    faiss.write_index(index, '/tmp/index.bin')
    s3.upload_file('/tmp/index.bin', BUCKET, 'faiss/index.bin')

    with open('/tmp/chunks.json', 'w') as f:
        json.dump(all_chunks, f, ensure_ascii=False)
    s3.upload_file('/tmp/chunks.json', BUCKET, 'faiss/chunks.json')

    return {
        'statusCode': 200,
        'body': json.dumps({
            'chunks': len(all_chunks),
            'dimension': dim,
            'message': 'FAISS index created and uploaded to S3'
        })
    }
