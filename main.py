import asyncio
import os
import sys
import traceback
from typing import Any

import dotenv
from discord import Permissions
from discord.ext.commands import Bot, BotMissingPermissions, when_mentioned_or


INITIAL_COGS = [
    "cogs.auth",
]


def permissions_to_error_text(permissions: list[str]) -> str:
    formatted = [f"`{s.replace('_', ' ').title()}`" for s in permissions]
    return "権限" + ", ".join(formatted) + " を追加してください"


class MyBot(Bot):
    def __init__(self) -> None:
        self.permissions = Permissions(
            view_channel=True,
            send_messages=True,
            manage_messages=True,
            embed_links=True,
            read_message_history=True,
            manage_webhooks=True,
            add_reactions=True,
        )
        super().__init__(command_prefix=when_mentioned_or("$"))
        for cog in INITIAL_COGS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self) -> None:
        print(self.user.name)  # type: ignore
        print(self.user.id, "\n")  # type: ignore

    def run(self, token: str) -> None:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start(token))
        except KeyboardInterrupt:
            print("Program End.")
            sys.exit()
        finally:
            loop.run_until_complete(self.close())

    async def on_error(self, *args: Any) -> None:
        error_type, error, _traceback = sys.exc_info()
        if isinstance(error, BotMissingPermissions):
            _, message, *_ = args
            await message.channel.send(permissions_to_error_text(error.missing_perms))
        else:
            traceback.print_exception(error_type, error, _traceback)


if __name__ == "__main__":
    if os.environ.get("DEBUG") is not None:
        dotenv.load_dotenv()

    while True:
        MyBot().run(os.environ["DISCORD_TOKEN"])
