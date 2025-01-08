import logging

import constants
import events
from state import client

if __name__ == "__main__":
    logging.basicConfig(
        format=(
            "%(asctime)s %(levelname)s %(name):%(module)s %(message)s"
            if __debug__
            else "%(asctime)s %(levelname)s %(message)s"
        ),
        datefmt="%Y-%m-%d %T",
        level=logging.DEBUG if __debug__ else logging.INFO,
    )
    logging.getLogger("disnake").setLevel(logging.WARNING)

    events.prepare()
    client.run(constants.SECRETS["TOKEN"])
