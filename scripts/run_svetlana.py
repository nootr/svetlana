#!/usr/bin/env python3

import logging
import argparse

from svetlana import bot
from svetlana.config import fetch_config

def parse_args():
    parser = argparse.ArgumentParser(
        description='A WebDiplomacy notification bot for Discord.')

    parser.add_argument('-c', '--config', action='store',
            help='Configuration file')
    parser.add_argument('-d', '--debug', action='store_true',
            help='Enable debug')
    return parser.parse_args()

def run(config, debug=False):
    loglevel = logging.DEBUG if debug else logging.INFO
    logformat = '%(asctime)s %(levelname)-8s %(message)s'
    logging.basicConfig(level=loglevel, format=logformat)

    config = fetch_config()
    logging.debug('Loaded config: %s', config)

    bot.run(config['DISCORD_TOKEN'])

if __name__ == '__main__':
    args = parse_args()
    kwargs = vars(args)
    run(**kwargs)
