"""
This module contains an interface to the WebDiplomacy website.
"""

import logging
import time
import re

from datetime import datetime
from collections import defaultdict

import requests


class DiplomacyGame:
    """Contains information about a WebDiplomacy game."""
    # pylint: disable=too-many-instance-attributes
    # NOTE(jhartog): Although there are many attributes, they are all justified
    # and so it's a reasonable amount.
    def __init__(self, game_id, stats, url, game_endpoint):
        self.game_id = game_id
        self.title = stats['title'][0]
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
        self.map_url = url + stats['map_link'][0]

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
    def __init__(self, url='https://webdiplomacy.net/'):
        self.url = url

    def _request(self, url, timeout=1, threshold=300):
        """Performs a HTTPS request and returns the response body.

        When it fails, it tries again after an increasing timeout until the
        timeout reaches a given threshold.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as exc:
            if timeout > threshold:
                logging.exception('Problem while fetching data: %s', exc)
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
            'title':     r'.*<title>(.*?) - webDiplomacy<.*',
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
        except (IndexError, KeyError):
            # NOTE(jhartog): This is a parsing error, which most probably means
            # the game is invalid.
            return None
