import disnake

playback_queue = {}
reloaded_modules = set()

intents = disnake.Intents.default()
intents.message_content = True
client = disnake.Client(intents=intents)
