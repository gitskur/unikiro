@echo off
REM 인프라 배포 스크립트
REM 실행 전: build_layer.bat 먼저 실행 후 Layer ARN 확인

set STACK_NAME=coupa-ai-facilitator
set REGION=us-east-1
set /p LAYER_ARN="build_layer.bat 출력된 Layer ARN 입력: "

echo [1/2] CloudFormation 스택 배포 중...
aws cloudformation deploy ^
  --template-file infra\cloudformation.yaml ^
  --stack-name %STACK_NAME% ^
  --parameter-overrides LayerArn=%LAYER_ARN% ^
  --capabilities CAPABILITY_NAMED_IAM ^
  --region %REGION%

echo [2/2] 출력값 확인...
aws cloudformation describe-stacks ^
  --stack-name %STACK_NAME% ^
  --region %REGION% ^
  --query "Stacks[0].Outputs" ^
  --output table

echo.
echo 위 ApiUrl을 ui\index.html 의 API 변수에 입력하세요.
