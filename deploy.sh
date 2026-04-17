#!/bin/bash
set -e

STACK_NAME="coupa-chatbot"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"

echo "🚀 Coupa Chatbot 배포 시작 (리전: $REGION)"

# 1. SAM 빌드
echo "📦 SAM 빌드 중..."
sam build --template template.yaml

# 2. SAM 배포
echo "☁️ AWS 배포 중..."
sam deploy \
  --stack-name $STACK_NAME \
  --region $REGION \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

# 3. 출력값 가져오기
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
  --output text)
BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query "Stacks[0].Outputs[?OutputKey=='DocsBucket'].OutputValue" \
  --output text)

echo ""
echo "✅ 배포 완료!"
echo "   API URL: $API_URL"
echo "   S3 Bucket: $BUCKET"

# 4. PDF 업로드
echo ""
echo "📄 PDF 문서 업로드 중..."
aws s3 sync chatbot_docs/ s3://$BUCKET/docs/ --region $REGION

# 5. 임베딩 실행
echo ""
echo "🧠 PDF 임베딩 실행 중 (2~3분 소요)..."
aws lambda invoke \
  --function-name coupa-chatbot-embed \
  --region $REGION \
  --payload '{}' \
  --cli-read-timeout 300 \
  /tmp/embed-result.json
cat /tmp/embed-result.json
echo ""

echo ""
echo "🎉 전체 배포 완료!"
echo ""
echo "📌 Teams 봇 설정:"
echo "   1. CHATBOT_API_URL=$API_URL"
echo "   2. Azure Bot Service에서 메시징 엔드포인트 설정"
echo "   3. teams-bot/ 폴더를 Azure App Service 또는 로컬에서 실행"
