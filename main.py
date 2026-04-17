import os
from dotenv import load_dotenv
from chat_engine import ChatEngine, ChatSession
from connectors import ConfluenceClient, CoupaClient

load_dotenv()


def build_context(query: str, confluence: ConfluenceClient) -> str:
    docs = confluence.search(query)
    return "\n\n".join(f"[{d.title}]({d.url})\n{d.content}" for d in docs)


def main():
    engine = ChatEngine(
        region=os.getenv("AWS_REGION", "ap-northeast-2"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    )
    confluence = ConfluenceClient(
        base_url=os.getenv("CONFLUENCE_BASE_URL", ""),
        username=os.getenv("CONFLUENCE_USERNAME", ""),
        api_token=os.getenv("CONFLUENCE_API_TOKEN", ""),
        space_key=os.getenv("CONFLUENCE_SPACE_KEY", "PROC"),
    )
    coupa = CoupaClient(  # noqa: F841  (상태 조회 등에 직접 활용 가능)
        base_url=os.getenv("COUPA_BASE_URL", ""),
        api_key=os.getenv("COUPA_API_KEY", ""),
    )

    session = ChatSession()
    print("챗봇 시작 (종료: 'exit')\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() == "exit":
            break

        context = build_context(user_input, confluence)
        response = engine.chat(session, user_input, context)
        print(f"\nBot [{session.last_intent.value}]: {response}\n")


if __name__ == "__main__":
    main()
