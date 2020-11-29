import pytest
from datetime import datetime

from svetlana.webdiplomacy import DiplomacyGame, WebDiplomacyClient


def test_client_won(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo memberCountryName><bar memberStatusWon">Russia</bar>
    <a LargeMapLink href="foo.jpg">
    <"gameName">mock</gameName>
    <"gameDate">Spring 1901</gameDate><"gamePhase">Diplomacy</gamePhase>
    """
    monkeypatch.setattr(WebDiplomacyClient, '_request', lambda *args: response)
    request_spy = mocker.spy(WebDiplomacyClient, '_request')

    client = WebDiplomacyClient()
    game = client.fetch(1234)

    assert request_spy.call_count == 1
    args, kwargs = request_spy.call_args
    assert args[1] == 'https://webdiplomacy.net/board.php?gameID=1234'
    assert game.game_id == 1234
    assert game.won == 'Russia'
    assert not game.pregame
    assert game.map_url == 'https://webdiplomacy.net/foo.jpg'
    assert game.name == 'mock'
    assert game.phase == 'Diplomacy'
    assert game.date == 'Spring 1901'

def test_client_draw(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo memberCountryName><bar memberStatusDrawn">Russia</bar>
    <foo memberCountryName><bar memberStatusDrawn">France</bar>
    <a LargeMapLink href="foo.jpg">
    <"gameName">mock</gameName>
    <"gameDate">Spring 1901</gameDate><"gamePhase">Diplomacy</gamePhase>
    """
    monkeypatch.setattr(WebDiplomacyClient, '_request', lambda *args: response)
    request_spy = mocker.spy(WebDiplomacyClient, '_request')

    client = WebDiplomacyClient()
    game = client.fetch(1234)

    assert request_spy.call_count == 1
    args, kwargs = request_spy.call_args
    assert args[1] == 'https://webdiplomacy.net/board.php?gameID=1234'
    assert 'Russia' in game.drawn
    assert 'France' in game.drawn
    assert not game.pregame
    assert game.map_url == 'https://webdiplomacy.net/foo.jpg'

def test_client_pregame(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo "memberPreGameList">
    <a LargeMapLink href="foo.jpg">
    <"gameName">mock</gameName>
    <"gameDate">Spring 1901</gameDate><"gamePhase">Diplomacy</gamePhase>
    """
    monkeypatch.setattr(WebDiplomacyClient, '_request', lambda *args: response)
    request_spy = mocker.spy(WebDiplomacyClient, '_request')

    client = WebDiplomacyClient()
    game = client.fetch(1234)

    assert request_spy.call_count == 1
    args, kwargs = request_spy.call_args
    assert args[1] == 'https://webdiplomacy.net/board.php?gameID=1234'
    assert game.pregame
    assert game.map_url == 'https://webdiplomacy.net/foo.jpg'

def test_client_ready(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo memberCountryName>tick<bar "MemberStatusPlaying">Italy</bar>
    <foo memberCountryName>tick<bar "MemberStatusPlaying">France</bar>
    <a LargeMapLink href="foo.jpg">
    <"gameName">mock</gameName>
    <"gameDate">Spring 1901</gameDate><"gamePhase">Diplomacy</gamePhase>
    """
    monkeypatch.setattr(WebDiplomacyClient, '_request', lambda *args: response)
    request_spy = mocker.spy(WebDiplomacyClient, '_request')

    client = WebDiplomacyClient()
    game = client.fetch(1234)

    assert request_spy.call_count == 1
    args, kwargs = request_spy.call_args
    assert args[1] == 'https://webdiplomacy.net/board.php?gameID=1234'
    assert not game.pregame
    assert 'Italy' in game.ready
    assert 'France' in game.ready
    assert game.map_url == 'https://webdiplomacy.net/foo.jpg'

def test_client_not_ready(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo memberCountryName>alert<bar "MemberStatusPlaying">Italy</bar>
    <foo memberCountryName>alert<bar "MemberStatusPlaying">France</bar>
    <a LargeMapLink href="foo.jpg">
    <"gameName">mock</gameName>
    <"gameDate">Spring 1901</gameDate><"gamePhase">Diplomacy</gamePhase>
    """
    monkeypatch.setattr(WebDiplomacyClient, '_request', lambda *args: response)
    request_spy = mocker.spy(WebDiplomacyClient, '_request')

    client = WebDiplomacyClient()
    game = client.fetch(1234)

    assert request_spy.call_count == 1
    args, kwargs = request_spy.call_args
    assert args[1] == 'https://webdiplomacy.net/board.php?gameID=1234'
    assert not game.pregame
    assert 'Italy' in game.not_ready
    assert 'France' in game.not_ready
    assert game.map_url == 'https://webdiplomacy.net/foo.jpg'

def test_game_time(mocker, monkeypatch):
    mock_game = DiplomacyGame(1, {
        'name': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp()))],
        'defeated': [],
        'not_ready': [],
        'ready': [],
        'won': [],
        'drawn': [],
        'pregame': [],
        'map_link': [''],
    }, '', '')

    assert mock_game.days_left == -1
    assert mock_game.hours_left == 23
    assert mock_game.minutes_left == 59

    mock_game = DiplomacyGame(1, {
        'name': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp())+3600)],
        'defeated': [],
        'not_ready': [],
        'ready': [],
        'won': [],
        'drawn': [],
        'pregame': [],
        'map_link': [''],
    }, '', '')

    assert mock_game.days_left == 0
    assert mock_game.hours_left == 0
    assert mock_game.minutes_left == 59

def test_game_stats(mocker, monkeypatch):
    mock_game = DiplomacyGame(1, {
        'name': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp()))],
        'defeated': ['Italy'],
        'not_ready': ['Turkey'],
        'ready': ['Germany'],
        'won': ['Russia'],
        'drawn': ['Russia', 'France'],
        'pregame': [],
        'map_link': [''],
    }, '', '')

    assert mock_game.defeated == ['Italy']
    assert mock_game.not_ready == ['Turkey']
    assert mock_game.ready == ['Germany']
    assert mock_game.won == 'Russia'
    assert mock_game.drawn == ['Russia', 'France']
    assert not mock_game.pregame

def test_game_pregame(mocker, monkeypatch):
    mock_game = DiplomacyGame(1, {
        'name': ['Mock'],
        'date': ['Spring, 1901'],
        'phase': ['Diplomacy'],
        'deadline': [str(int(datetime.now().timestamp()))],
        'defeated': [],
        'not_ready': [],
        'ready': [],
        'won': [],
        'drawn': [],
        'pregame': ['foo'],
        'map_link': [''],
    }, '', '')

    assert mock_game.pregame
