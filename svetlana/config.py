import os
import logging
import sys

KEYS = [
    'DISCORD_TOKEN',
]

def fetch_config():
    """Fetch the config from the environment."""
    config = { k: os.getenv(k) for k in KEYS }

    for key in KEYS:
        if not config[key]:
            logging.error("""Missing environment variable: "%s".
Tip: setup a rc-file (~/.svetlanarc) which contains the settings. Execute
'`tartarus -h` for more info'""", key)
            sys.exit(1)

    return config
