import asyncio
from app.core.settings import get_settings
from app.agents.classifier import TicketClassifier
from app.agents.generator import ResponseGenerator
import traceback

async def main():
    try:
        settings = get_settings()
        print("Settings loaded:", settings.APP_NAME)
        
        print("Testing Classifier...")
        classifier = TicketClassifier()
        res = await classifier.classify("my account is locked help me")
        print("Classifier result:", res)
        
        print("Testing Generator...")
        generator = ResponseGenerator()
        res2 = await generator.generate("my account is locked help me", "account", [], [])
        print("Generator result:", res2)
        print("Done!")
    except Exception as e:
        print("RUNTIME ERROR:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
