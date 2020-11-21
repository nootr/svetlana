import pytest

from svetlana.webdiplomacy import WebDiplomacyClient


def test_client_won(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo memberCountryName><bar memberStatusWon">Russia</bar>
    """
    monkeypatch.setattr(WebDiplomacyClient, '_request', lambda *args: response)
    request_spy = mocker.spy(WebDiplomacyClient, '_request')

    client = WebDiplomacyClient()
    game = client.fetch(1234)

    assert request_spy.call_count == 1
    args, kwargs = request_spy.call_args
    assert args[1] == 'https://webdiplomacy.net/board.php?gameID=1234'
    assert game.won == 'Russia'
    assert not game.pregame

def test_client_draw(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo memberCountryName><bar memberStatusDrawn">Russia</bar>
    <foo memberCountryName><bar memberStatusDrawn">France</bar>
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

def test_client_pregame(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo "memberPreGameList">
    """
    monkeypatch.setattr(WebDiplomacyClient, '_request', lambda *args: response)
    request_spy = mocker.spy(WebDiplomacyClient, '_request')

    client = WebDiplomacyClient()
    game = client.fetch(1234)

    assert request_spy.call_count == 1
    args, kwargs = request_spy.call_args
    assert args[1] == 'https://webdiplomacy.net/board.php?gameID=1234'
    assert game.pregame

def test_client_ready(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo memberCountryName>tick<bar "MemberStatusPlaying">Italy</bar>
    <foo memberCountryName>tick<bar "MemberStatusPlaying">France</bar>
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

def test_client_not_ready(mocker, monkeypatch):
    response = """<foo gameTimeRemaining unixtime="1337">
    <foo memberCountryName>alert<bar "MemberStatusPlaying">Italy</bar>
    <foo memberCountryName>alert<bar "MemberStatusPlaying">France</bar>
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
