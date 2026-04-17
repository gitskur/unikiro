import os
import json
import aiohttp
from botbuilder.core import TurnContext, ActivityHandler
from botbuilder.schema import Activity

API_URL = os.environ.get('CHATBOT_API_URL', '')


class CoupaBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.strip() if turn_context.activity.text else ''
        user_id = turn_context.activity.from_property.id

        if text.lower() == 'help':
            await turn_context.send_activity(
                "💬 **Coupa 도우미 사용법**\n\n"
                "질문을 입력하면 Coupa, eProcurement, CSP 문서를 기반으로 답변합니다.\n\n"
                "예시:\n"
                "- CSP에 어떻게 로그인하나요?\n"
                "- 인보이스 생성 방법 알려줘\n"
                "- PO 확인하는 방법은?\n\n"
                "👍👎 답변 후 피드백을 남겨주시면 품질 개선에 도움이 됩니다.")
            return

        if not text:
            return

        # 타이핑 표시
        await turn_context.send_activity(Activity(type="typing"))

        # API 호출
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{API_URL}/chat",
                    json={"message": text, "user_id": user_id},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    data = await resp.json()

            answer = data.get('answer', '답변을 가져올 수 없습니다.')
            ts = data.get('timestamp', '')

            # 답변 + 피드백 버튼 (Adaptive Card)
            card = {
                "type": "AdaptiveCard",
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4",
                "body": [{"type": "TextBlock", "text": answer, "wrap": True}],
                "actions": [
                    {"type": "Action.Submit", "title": "👍 도움됨",
                     "data": {"feedback": "positive", "timestamp": ts, "user_id": user_id}},
                    {"type": "Action.Submit", "title": "👎 부족함",
                     "data": {"feedback": "negative", "timestamp": ts, "user_id": user_id}}
                ]
            }
            message = Activity(
                type="message",
                attachments=[{
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": card
                }])
            await turn_context.send_activity(message)

        except Exception as e:
            await turn_context.send_activity(f"⚠️ 오류가 발생했습니다: {str(e)}")

    async def on_adaptive_card_invoke(self, turn_context: TurnContext, invoke_value):
        data = invoke_value
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(f"{API_URL}/chat", json={
                    "user_id": data.get("user_id"),
                    "timestamp": data.get("timestamp"),
                    "feedback": data.get("feedback")
                })
            return {"statusCode": 200, "type": "application/vnd.microsoft.activity.message",
                    "value": "피드백 감사합니다! 🙏"}
        except:
            return {"statusCode": 200, "type": "application/vnd.microsoft.activity.message",
                    "value": "피드백 저장 중 오류가 발생했습니다."}
