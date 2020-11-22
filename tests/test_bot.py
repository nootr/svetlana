import pytest
import asyncio

from svetlana.bot import DiscordClient


class MockChannel(object):
    id = 1
    @asyncio.coroutine
    def send(self, msg):
        return None

class MockMessage(object):
    channel = MockChannel()
    def __init__(self, msg):
        self.content = msg

@pytest.mark.asyncio
async def test_follow_unfollow_list(mocker, monkeypatch):
    send_spy = mocker.spy(MockMessage.channel, 'send')

    client = DiscordClient(None, ':memory:', False)

    await client.on_message(MockMessage('svetlana list'))
    args, kwargs = send_spy.call_args
    assert args[0] == "I'm following: []"

    await client.on_message(MockMessage('svetlana follow 1234'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Will do!'

    await client.on_message(MockMessage('svetlana follow 1234'))
    args, kwargs = send_spy.call_args
    assert args[0] == "I'm already following that game!"

    await client.on_message(MockMessage('svetlana list'))
    args, kwargs = send_spy.call_args
    assert args[0] == "I'm following: [1234]"

    await client.on_message(MockMessage('svetlana unfollow 1234'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Consider it done!'

    await client.on_message(MockMessage('svetlana unfollow 1234'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Huh? What game?'

    await client.on_message(MockMessage('svetlana follow 1234a'))
    args, kwargs = send_spy.call_args
    assert args[0] == 'Huh?'

