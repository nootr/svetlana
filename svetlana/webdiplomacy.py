"""
This module contains an interface to the WebDiplomacy website.
"""

import logging
import time
import re

from datetime import datetime
from collections import defaultdict

import requests


class InvalidGameError(Exception):
    """Custom exception which represents the encounter of an invalid game.

    This is probably triggered by an invalid game ID or by a cancelled game.
    """

class DiplomacyGame:
    """Contains information about a WebDiplomacy game."""
    # pylint: disable=too-many-instance-attributes
    # NOTE(jhartog): Although there are many attributes, they are all justified
    # and so it's a reasonable amount.
    def __init__(self, game_id, stats, url, game_endpoint):
        if game_id < 0:
            raise InvalidGameError

        self.game_id = game_id
        self.name = stats['name'][0]
        self.date = stats['date'][0]
        self.phase = stats['phase'][0]
        self.deadline = datetime.fromtimestamp(int(stats['deadline'][0])) \
                if stats['deadline'] else None
        self.defeated = stats['defeated']
        self.not_ready = stats['not_ready']
        self.ready = stats['ready']
        self.won = stats['won'][0] if stats['won'] else None
        self.drawn = stats['drawn']
        self.pregame = stats['pregame'] != []
        self.url = url + game_endpoint
        # NOTE(krist): Discord caches embed images. After a retreat phase,
        # the turn number does not increase - so the image url stays the same.
        # This causes Discord to keep using a cached, but outdated map image.
        # Add a parameter time to the map url, which does not do anything other
        # than to prevent Discord from invalidly caching the map image.
        self.map_url = f'{url}{stats["map_link"][0]}&time={str(int(time.time()))}'

    @property
    def _timedelta(self):
        """Returns the time until the deadline."""
        return self.deadline - datetime.now()

    @property
    def days_left(self):
        """Returns the number of days left."""
        return self._timedelta.days if self.deadline else None

    @property
    def hours_left(self):
        """Returns the number of hours left."""
        return self._timedelta.seconds//3600 if self.deadline else None

    @property
    def minutes_left(self):
        """Returns the number of minutes left."""
        return (self._timedelta.seconds//60)%60 if self.deadline else None

    @property
    def delta(self):
        """Returns the total number of seconds left."""
        return self._timedelta.seconds if self.deadline else None


class WebDiplomacyClient:
    """Acts as an interface to the WebDiplomacy website."""
    # pylint: disable=too-few-public-methods
    # NOTE(jhartog): Although this class only has one public method, there are a
    # number of reasons why it's better as a class; e.g. only having to specify
    # the url once without sketchy global variables.
    def __init__(self, url='https://webdiplomacy.net/'):
        self.url = url

    def _request(self, url, timeout=1, threshold=300):
        """Performs a HTTPS request and returns the response body.

        When it fails, it tries again after an increasing timeout until the
        timeout reaches a given threshold.
        """
        try:
            # pylint: disable=bare-except
            # NOTE(jhartog): A bare except is justified here as it's retrying
            # the request a finite amount of times. If there is a bug, it will
            # be raised.
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except:
            if timeout > threshold:
                raise
            time.sleep(timeout)
            self._request(url, timeout=timeout*2)

    @staticmethod
    def _parse(content):
        """Parses the contents of a WebDiplomacy game page.

        Returns a dict with country and game info.

        Note that exceptions are not caught by design, these should be handled
        outside of this function.
        """
        patterns = {
            'name':      r'.*gameName">(.*?)<.*',
            'date':      r'.*gameDate">(.*?)<.*',
            'phase':     r'.*gamePhase">(.*?)<.*',
            'defeated':  r'.*memberCountryName.*memberStatusDefeated">(.*?)<.*',
            'drawn':     r'.*memberCountryName.*memberStatusDrawn">(.*?)<.*',
            'ready':     r'.*memberCountryName.*tick.*rStatusPlaying">(.*?)<.*',
            'not_ready': r'.*memberCountryName.*alert.*StatusPlaying">(.*?)<.*',
            'won':       r'.*memberCountryName.*memberStatusWon">(.*?)<.*',
            'deadline':  r'.*gameTimeRemaining.*unixtime="([0-9]+)".*',
            'pregame':   r'.*(memberPreGameList)">.*',
            'map_link':  r'.*<a.*LargeMapLink.*href="(.*?)".*',
        }
        data = defaultdict(list)

        for line in content.split('\n'):
            for key, pattern in patterns.items():
                match = re.match(pattern, line.strip())
                if match:
                    data[key] += [match.group(1)]

        logging.debug('Parsed data: %s', data)

        return data

    def fetch(self, game_id, endpoint='board.php?gameID={}'):
        """Fetches info from WebDiplomacy, parses it and returns the data."""
        try:
            response = self._request(self.url + endpoint.format(game_id))
            data = self._parse(response)
            game = DiplomacyGame(game_id, data, self.url,
                    endpoint.format(game_id))
            return game
        except (IndexError, KeyError) as exc:
            # NOTE(jhartog): This is a parsing error, which most probably means
            # the game ID is invalid or the game has been cancelled.
            raise InvalidGameError from exc
