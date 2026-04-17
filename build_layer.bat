@echo off
REM Lambda Layer 빌드 + 배포 (Docker 필수)
REM 실행: build_layer.bat

set LAYER_NAME=coupa-ai-deps
set REGION=us-east-1

echo [1/3] Amazon Linux 2 환경에서 패키지 빌드...
docker run --rm ^
  -v "%cd%\lambda:/var/task" ^
  public.ecr.aws/lambda/python:3.12 ^
  pip install -r /var/task/requirements.txt ^
    -t /var/task/python/lib/python3.12/site-packages/ ^
    --quiet --no-cache-dir

echo [2/3] Layer ZIP 생성...
cd lambda
powershell Compress-Archive -Path python -DestinationPath ..\layer.zip -Force
rd /s /q python
cd ..

echo [3/3] Lambda Layer 배포...
for /f "tokens=*" %%i in ('aws lambda publish-layer-version ^
  --layer-name %LAYER_NAME% ^
  --zip-file fileb://layer.zip ^
  --compatible-runtimes python3.12 ^
  --region %REGION% ^
  --query LayerVersionArn ^
  --output text') do set LAYER_ARN=%%i

del layer.zip
echo.
echo Layer ARN: %LAYER_ARN%
echo.
echo 다음 명령으로 Lambda 함수에 Layer를 연결하세요:
echo aws lambda update-function-configuration --function-name coupa-ai-facilitator --layers %LAYER_ARN% --region %REGION%
