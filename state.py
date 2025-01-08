import time
from collections import OrderedDict

import disnake


class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        self.size_limit = kwargs.pop("size_limit", 1000)
        super().__init__(*args, **kwargs)
        self._check_size_limit()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
client = disnake.Client(intents=intents)

command_locks = LimitedSizeDict()
idle_tracker = {"is_idle": False, "last_used": time.time()}
kill = {"transcript": False}
message_responses = LimitedSizeDict()
players = {}
start_time = time.time()
