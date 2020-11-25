import pytest
import asyncio

from datetime import datetime

from svetlana.bot import DiscordClient, DESCRIPTION
from svetlana.webdiplomacy import DiplomacyGame

MINUTE = 60
HOUR = 60*MINUTE
DAY = 24*HOUR


class MockChannel:
    id = 1

    @asyncio.coroutine
    def send(self, *args, **kwargs):
        return None

class MockAuthor:
    name = 'jhartog'

class MockMessage:
    channel = MockChannel()
    author = MockAuthor()

    def __init__(self, msg):
        self.content = msg

class MockWebDiplomacyClient:
    def __init__(self, data):
        self._response = DiplomacyGame(1, data, 'https://foo.bar/', 'game.php')

    def fetch(self, _):
        return self._response


@pytest.mark.asyncio
async def test_help(mocker, monkeypatch):
    send_spy = mocker.spy(MockMessage.channel, 'send')

    client = DiscordClient(None, ':memory:', False)

    await client.on_message(MockMessage('svetlana help'))
    args, kwargs = send_spy.call_args
    assert args[0] == f'Hello, jhartog!\n{DESCRIPTION}'

@pytest.mark.asyncio
async def test_follow_unfollow_list(mocker, monkeypatch):
    send_spy = mocker.spy(MockMessage.channel, 'send')

    wd_client = MockWebDiplomacyClient({
        'title': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp()))],
        'defeated': [],
        'not_ready': [],
        'ready': [],
        'won': [],
        'drawn': [],
        'pregame': ['foo'],
        'map_link': ['foo.jpg'],
    })
    client = DiscordClient(wd_client, ':memory:', False)

    await client.on_message(MockMessage('svetlana list'))
    args, kwargs = send_spy.call_args
    assert args[0] == "I'm following: "

    await client.on_message(MockMessage('svetlana follow 1234'))
    args, kwargs = send_spy.call_args
    assert kwargs['embed'].description == 'Now following 1234!'
    assert kwargs['embed'].url == 'https://foo.bar/game.php'
    assert kwargs['embed'].image.url == 'https://foo.bar/foo.jpg'
    assert kwargs['embed'].title == 'Mock - Spring, 1901 - Diplomacy phase'

    await client.on_message(MockMessage('svetlana follow 1234'))
    args, kwargs = send_spy.call_args
    assert kwargs['embed'].description == "I'm already following that game!"

    await client.on_message(MockMessage('svetlana follow 1337'))
    args, kwargs = send_spy.call_args
    assert kwargs['embed'].description == 'Now following 1337!'

    await client.on_message(MockMessage('svetlana list'))
    args, kwargs = send_spy.call_args
    assert args[0] == "I'm following: 1234, 1337"

    await client.on_message(MockMessage('svetlana unfollow 1234'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Consider it done!'

    await client.on_message(MockMessage('svetlana unfollow 1234'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Huh? What game?'

    await client.on_message(MockMessage('svetlana follow 1234a'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Huh?'

    await client.on_message(MockMessage('svetlana follow -1'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Huh?'

@pytest.mark.asyncio
async def test_alert_silence(mocker, monkeypatch):
    send_spy = mocker.spy(MockMessage.channel, 'send')

    client = DiscordClient(None, ':memory:', False)

    await client.on_message(MockMessage('svetlana alert 2'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'OK, I will alert 2 hours before a deadline.'

    await client.on_message(MockMessage('svetlana alert 3'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'OK, I will alert 3 hours before a deadline.'

    await client.on_message(MockMessage('svetlana alert 2'))
    args, kwargs = send_spy.call_args
    assert args[0] == "I'm already alerting 2 hours before a deadline!"

    await client.on_message(MockMessage('svetlana silence 2'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Understood, I will stop alerting T-2h..'

    await client.on_message(MockMessage('svetlana silence 2'))
    args, kwargs = send_spy.call_args
    assert args[0] == "I already don't alert 2 hours before a deadline?!"

    await client.on_message(MockMessage('svetlana alert list'))
    args, kwargs = send_spy.call_args
    assert args[0] == "I'm alerting at: T-3h"

    await client.on_message(MockMessage('svetlana silence 3'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Understood, I will stop alerting T-3h..'

@pytest.mark.asyncio
async def test_poll_pregame(mocker, monkeypatch):
    def _test_days(N):
        game = DiplomacyGame(1, {
            'title': ['Mock'],
            'date': ['Spring, 1901'],
            'phase': ['Diplomacy'],
            'deadline': [str(int(datetime.now().timestamp())+N*DAY+MINUTE)],
            'defeated': [],
            'not_ready': [],
            'ready': [],
            'won': [],
            'drawn': [],
            'pregame': ['foo'],
            'map_link': ['foo.jpg'],
        }, '', '')

        client = DiscordClient(None, ':memory:', False)

        msg = client._poll(game, None)
        assert msg == f'The game starts in {N} days!'

    for N in range(7):
        _test_days(N)

@pytest.mark.asyncio
async def test_poll_two_hours_left_ready(mocker, monkeypatch):
    game = DiplomacyGame(1, {
        'title': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp())+2*HOUR+MINUTE)],
        'defeated': [],
        'not_ready': [],
        'ready': [],
        'won': [],
        'drawn': [],
        'pregame': [],
        'map_link': ['foo.jpg'],
    }, '', '')

    client = DiscordClient(None, ':memory:', False)
    await client.on_message(MockMessage('svetlana alert 2'))

    msg = client._poll(game, 1)
    assert msg == "2h left, everybody's ready!"

@pytest.mark.asyncio
async def test_poll_two_hours_left_not_ready(mocker, monkeypatch):
    game = DiplomacyGame(1, {
        'title': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp())+2*HOUR+MINUTE)],
        'defeated': [],
        'not_ready': ['Turkey', 'France'],
        'ready': [],
        'won': [],
        'drawn': [],
        'pregame': [],
        'map_link': ['foo.jpg'],
    }, '', '')

    client = DiscordClient(None, ':memory:', False)
    await client.on_message(MockMessage('svetlana alert 2'))

    msg = client._poll(game, 1)
    assert msg == "2h left! These countries aren't ready: Turkey, France"

@pytest.mark.asyncio
async def test_poll_drawn(mocker, monkeypatch):
    game = DiplomacyGame(1, {
        'title': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp()))],
        'defeated': [],
        'not_ready': [],
        'ready': [],
        'won': [],
        'drawn': ['France', 'Russia'],
        'pregame': [],
        'map_link': ['foo.jpg'],
    }, '', '')

    client = DiscordClient(None, ':memory:', False)

    msg = client._poll(game, None)
    assert msg == 'The game was a draw between France, Russia!'

@pytest.mark.asyncio
async def test_poll_won(mocker, monkeypatch):
    game = DiplomacyGame(1, {
        'title': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp()))],
        'defeated': [],
        'not_ready': [],
        'ready': [],
        'won': ['Russia'],
        'drawn': [],
        'pregame': [],
        'map_link': ['foo.jpg'],
    }, '', '')

    client = DiscordClient(None, ':memory:', False)

    msg = client._poll(game, None)
    assert msg == 'Russia has won!'

@pytest.mark.asyncio
async def test_poll_new_round(mocker, monkeypatch):
    game = DiplomacyGame(1, {
        'title': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp())+DAY)],
        'defeated': [],
        'not_ready': [],
        'ready': [],
        'won': [],
        'drawn': [],
        'pregame': [],
        'map_link': ['foo.jpg'],
    }, '', '')

    client = DiscordClient(None, ':memory:', False)

    msg = client._poll(game, None)
    assert msg == 'Starting new round! Good luck :)'

