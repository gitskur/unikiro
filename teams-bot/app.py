import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from bot import CoupaBot

SETTINGS = BotFrameworkAdapterSettings(
    app_id=os.environ.get('BOT_APP_ID', ''),
    app_password=os.environ.get('BOT_APP_PASSWORD', ''))
ADAPTER = BotFrameworkAdapter(SETTINGS)
BOT = CoupaBot()


async def messages(req: web.Request) -> web.Response:
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    return web.Response(status=200)


async def health(req: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})

app = web.Application()
app.router.add_post("/api/messages", messages)
app.router.add_get("/health", health)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3978))
    web.run_app(app, host="0.0.0.0", port=port)
