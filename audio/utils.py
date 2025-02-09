def format_duration(duration: int | float) -> str:
    hours, duration = divmod(int(duration), 3600)
    minutes, duration = divmod(duration, 60)
    segments = [hours, minutes, duration]
    if len(segments) == 3 and segments[0] == 0:
        del segments[0]
    return f"{':'.join(f'{s:0>2}' for s in segments)}"
