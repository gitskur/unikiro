"""Teams Incoming Webhook으로 메시지를 전송하는 클라이언트."""
import json
import urllib.request


def send_message(webhook_url: str, title: str, text: str, facts: list[dict] | None = None) -> None:
    """Adaptive Card 형식으로 Teams 채널에 메시지 전송."""
    body = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {"type": "TextBlock", "text": title, "weight": "Bolder", "size": "Medium"},
                    {"type": "TextBlock", "text": text, "wrap": True},
                    *(
                        [{"type": "FactSet", "facts": facts}] if facts else []
                    ),
                ],
            },
        }],
    }
    data = json.dumps(body).encode()
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        if resp.status not in (200, 202):
            raise RuntimeError(f"Teams webhook 실패: {resp.status}")
