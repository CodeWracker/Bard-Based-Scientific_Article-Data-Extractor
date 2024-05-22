import requests
import json
import os
import asyncio

from sydney import SydneyClient


os.environ["BING_U_COOKIE"] =  "16mx5R6IoiLO4hNo7MOrt0XqhIH-1kXZLJR4No23L68Lk3nAzGfnAM5mjZNYizWt4op78bEKd9mF_TX21SINkyR-yN-vYelZQGiejwczILMe72vE9BDTOWl97IyOp9AJOd1eOTyfitsjcZnFFbvfaQ2eR9CZ2WQEs5DbOCvvLOjI_nU64l7xp3JtHL-nGdh2Eu4dl33lB7MqC8oAvksRSkp18H6ijJrLvqH5JsPb-clY"

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main() -> None:
    async with SydneyClient() as sydney:
        while True:
            prompt = input("You: ")

            if prompt == "!reset":
                await sydney.reset_conversation()
                continue
            elif prompt == "!exit":
                break

            print("Sydney: ", end="", flush=True)
            async for response in sydney.ask_stream(prompt):
                print(response, end="", flush=True)
            print("\n")


if __name__ == "__main__":
    asyncio.run(main())