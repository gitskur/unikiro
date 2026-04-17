"""
DynamoDB ChannelMapping 테이블 조회/등록.
스키마: PK=email(S), webhook_url(S), channel_name(S)
"""
import os
import boto3
from botocore.exceptions import ClientError

_table = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "ap-northeast-2")) \
              .Table("ChannelMapping")


def get_webhook_url(email: str) -> str | None:
    """담당자 이메일로 Teams 채널 webhook URL 조회. 없으면 None."""
    try:
        resp = _table.get_item(Key={"email": email})
        return resp.get("Item", {}).get("webhook_url")
    except ClientError:
        return None


def put_mapping(email: str, webhook_url: str, channel_name: str = "") -> None:
    """매핑 등록/갱신 (관리 스크립트용)."""
    _table.put_item(Item={"email": email, "webhook_url": webhook_url, "channel_name": channel_name})
