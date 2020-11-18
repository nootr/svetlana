import requests
import logging
import time
import re

from datetime import datetime


class WebDiplomacyClient(object):
    """Acts as an interface to the WebDiplomacy website.

    Example usage:

    >>> wd = WebDiplomacy()
    >>> data = wd.fetch(327239)
    >>> import pprint
    >>> pprint.pprint(data)
    {'deadline': datetime.datetime(2020, 11, 18, 16, 10, 40),
     'defeated': ['Austria', 'England'],
     'not_ready': ['France', 'Italy'],
     'ready': ['Russia', 'Germany'],
     'won': []}
    >>> data = wd.fetch(333174)
    >>> data['won']
    'Austria'
    """
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
        except Exception as e:
            logging.error('Request failed: "%s" "%s"', url, e)
            time.sleep(timeout)
            self._request(url, timeout=timeout*2)

    def _parse(self, content):
        """Parses the contents of a WebDiplomacy game page.

        Returns a dict with country and game info.

        Note that exceptions are not caught by design, these should be handled
        outside of this function.
        """
        patterns = {
            'defeated':  r'.*memberCountryName.*memberStatusDefeated">(.*?)<.*',
            'drawn':     r'.*memberCountryName.*memberStatusDrawn">(.*?)<.*',
            'ready':     r'.*memberCountryName.*tick.*rStatusPlaying">(.*?)<.*',
            'not_ready': r'.*memberCountryName.*alert.*StatusPlaying">(.*?)<.*',
            'won':       r'.*memberCountryName.*memberStatusWon">(.*?)<.*',
            'deadline':  r'.*gameTimeRemaining.*unixtime="([0-9]+)".*',
        }
        data = { k: [] for k in patterns }

        for line in content.split('\n'):
            for key, pattern in patterns.items():
                match = re.match(pattern, line.strip())
                if match:
                    current_list = data.get(key, [])
                    data[key] = current_list + [match.group(1)]

        logging.debug('Parsed data: %s', data)
        data['deadline'] = datetime.fromtimestamp(int(data['deadline'][0]))

        return data

    def fetch(self, id, endpoint='board.php?gameID={}'):
        """Fetches info from WebDiplomacy, parses it and returns the data."""
        try:
            response = self._request(self.url + endpoint.format(id))
            data = self._parse(response)

            return data
        except Exception as e:
            logging.error('Problems while fetching data: %s', e)
