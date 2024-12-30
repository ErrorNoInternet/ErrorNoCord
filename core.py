message_handlers = {}

async def trigger_message_handlers(event_type: str, *data):
    if event_type in message_handlers:
        for message_handler in message_handlers[event_type]:
            await message_handler(*data)
