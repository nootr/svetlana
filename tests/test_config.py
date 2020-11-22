import pytest
import os

from svetlana.config import fetch_config


def test_env(mocker, monkeypatch):
    monkeypatch.setenv('DISCORD_TOKEN', 'foobar')
    getenv_spy = mocker.spy(os, 'getenv')

    config = fetch_config()

    args, kwargs = getenv_spy.call_args
    assert args[0] == 'DISCORD_TOKEN'
    assert config['DISCORD_TOKEN'] == 'foobar'

def test_noenv(mocker, monkeypatch):
    getenv_spy = mocker.spy(os, 'getenv')

    with pytest.raises(SystemExit):
        fetch_config()

    args, kwargs = getenv_spy.call_args
    assert args[0] == 'DISCORD_TOKEN'
