import constants
import events
from state import client

if __name__ == "__main__":
    events.prepare()
    client.run(constants.SECRETS["TOKEN"])
