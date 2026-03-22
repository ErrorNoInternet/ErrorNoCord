import logging

from . import constants, events
from .state import client


def main():
    logging.basicConfig(
        format=(
            "%(asctime)s %(levelname)s %(name)s:%(module)s %(message)s"
            if __debug__
            else "%(asctime)s %(levelname)s %(message)s"
        ),
        datefmt="%Y-%m-%d %T",
        level=logging.DEBUG if __debug__ else logging.INFO,
    )
    logging.getLogger("disnake").setLevel(logging.WARNING)

    events.prepare()
    client.run(constants.SECRETS["TOKEN"])


if __name__ == "__main__":
    main()
