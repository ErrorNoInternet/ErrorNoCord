dynamic_handlers = {}


async def trigger_dynamic_handlers(event_type: str, *data):
    if event_type in dynamic_handlers:
        for message_handler in dynamic_handlers[event_type]:
            await message_handler(*data)
