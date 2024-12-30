import asyncio
import importlib
import inspect
from typing import Any, Optional

import disnake
import yt_dlp

import constants
from state import reloaded_modules

ytdl = yt_dlp.YoutubeDL(constants.YTDL_OPTIONS)


class YTDLSource(disnake.PCMVolumeTransformer):
    def __init__(
        self, source: disnake.AudioSource, *, data: dict[str, Any], volume: float = 0.5
    ):
        super().__init__(source, volume)
        self.title = data.get("title")

    @classmethod
    async def from_url(
        cls,
        url,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        stream: bool = False,
    ):
        loop = loop or asyncio.get_event_loop()
        data: Any = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        return cls(
            disnake.FFmpegPCMAudio(
                data["url"] if stream else ytdl.prepare_filename(data),
                options="-vn -reconnect 1",
            ),
            data=data,
        )


def __reload_module__():
    for name, module in globals().items():
        if (
            inspect.ismodule(module)
            and name not in constants.RELOAD_BLACKLISTED_MODULES
        ):
            importlib.reload(module)
            if "__reload_module__" in dir(module) and name not in reloaded_modules:
                reloaded_modules.add(name)
                module.__reload_module__()

    global ytdl
    ytdl = yt_dlp.YoutubeDL(constants.YTDL_OPTIONS)
