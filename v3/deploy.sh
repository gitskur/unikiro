#!/bin/bash
set -e

STACK_NAME="coupa-chatbot"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

echo "🚀 Coupa Chatbot v3 배포 시작 (리전: $REGION)"

if ! command -v sam &>/dev/null; then
  echo "❌ SAM CLI 필요: pip3 install aws-sam-cli"
  exit 1
fi

# 1. 빌드
echo "📦 SAM 빌드 중..."
sam build --template template.yaml

# 2. 배포
echo "☁️ AWS 배포 중..."
sam deploy \
  --stack-name $STACK_NAME \
  --region $REGION \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

# 3. 출력값
API_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
BUCKET=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query "Stacks[0].Outputs[?OutputKey=='DocsBucket'].OutputValue" --output text)

echo "✅ 인프라 배포 완료! API: $API_URL"

# 4. PDF + 프로세스 가이드 업로드
echo "📄 문서 업로드 중..."
aws s3 sync chatbot_docs/ s3://$BUCKET/docs/ --region $REGION
[ -f knowledge/process_guide.md ] && \
  aws s3 cp knowledge/process_guide.md s3://$BUCKET/knowledge/process_guide.md --region $REGION

# 5. 임베딩
echo "🧠 PDF 임베딩 실행 중 (2~3분)..."
aws lambda invoke --function-name coupa-chatbot-embed --region $REGION \
  --payload '{}' --cli-read-timeout 300 /tmp/embed-result.json
cat /tmp/embed-result.json && echo ""

echo ""
echo "🎉 전체 배포 완료!"
echo "   API:      $API_URL"
echo "   Teams:    $API_URL/teams"
echo "   Webhook:  $API_URL/coupa/webhook"
