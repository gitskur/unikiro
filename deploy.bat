@echo off
REM Lambda Layer 빌드 + 배포 스크립트
REM 필요: Docker Desktop 실행 중 (Amazon Linux 2 환경에서 빌드)

set LAYER_NAME=coupa-ai-deps
set REGION=us-east-1
set FUNCTION_NAME=coupa-ai-facilitator

echo [1/4] Lambda Layer 패키지 빌드 (Docker 사용)...
docker run --rm -v "%cd%\lambda:/var/task" public.ecr.aws/lambda/python:3.12 ^
  pip install -r /var/task/requirements.txt -t /var/task/python/lib/python3.12/site-packages/ --quiet

echo [2/4] Layer ZIP 압축...
cd lambda
powershell Compress-Archive -Path python -DestinationPath ..\layer.zip -Force
cd ..

echo [3/4] Lambda Layer 배포...
aws lambda publish-layer-version ^
  --layer-name %LAYER_NAME% ^
  --zip-file fileb://layer.zip ^
  --compatible-runtimes python3.12 ^
  --region %REGION%

echo [4/4] Lambda 함수 코드 배포...
cd lambda
powershell Compress-Archive -Path lambda_function.py -DestinationPath ..\function.zip -Force
cd ..
aws lambda update-function-code ^
  --function-name %FUNCTION_NAME% ^
  --zip-file fileb://function.zip ^
  --region %REGION%

del layer.zip
del function.zip
echo 완료! Layer ARN을 Lambda 함수에 연결하세요.
