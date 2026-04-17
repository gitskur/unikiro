import os

# Bedrock
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-2")

# Coupa
COUPA_BASE_URL = os.environ.get("COUPA_BASE_URL")
COUPA_API_KEY = os.environ.get("COUPA_API_KEY")

# Teams
TEAMS_BOT_APP_ID = os.environ.get("TEAMS_BOT_APP_ID")
TEAMS_BOT_APP_PASSWORD = os.environ.get("TEAMS_BOT_APP_PASSWORD")

# Teams Incoming Webhook (채널별로 SSM Parameter Store에서 가져올 수도 있음)
TEAMS_DEFAULT_WEBHOOK_URL = os.environ.get("TEAMS_DEFAULT_WEBHOOK_URL")
