import pytest

from svetlana.db import Pollers, Alarms


def test_pollers_iter_append(mocker, monkeypatch):
    pollers = Pollers(':memory:')
    data = [(1, 2), (3, 4)]

    for x, y in data:
        pollers.append((x, y))

    for i, obj in enumerate(pollers):
        print(i)
        x, y, z = obj
        assert x == data[i][0]
        assert y == data[i][1]
        assert not z

    assert (1, 2) in pollers
    assert (1, 3) not in pollers

    pollers.remove((1, 2))
    assert (1, 2) not in pollers

def test_pollers_str(mocker, monkeypatch):
    pollers = Pollers(':memory:')
    assert str(pollers) == '[]'

    data = [(1, 2), (3, 4)]

    for x, y in data:
        pollers.append((x, y))

    assert str(pollers) == '[(1, 2, None), (3, 4, None)]'

def test_alarms_iter_append(mocker, monkeypatch):
    alarms = Alarms(':memory:')
    data = [(1, 2), (3, 4)]

    for x, y in data:
        alarms.append((x, y))

    for i, obj in enumerate(alarms):
        x, y = obj
        assert x == data[i][0]
        assert y == data[i][1]

    assert (1, 2) in alarms
    assert (1, 3) not in alarms

    alarms.remove((1, 2))
    assert (1, 2) not in alarms

def test_alarms_str(mocker, monkeypatch):
    alarms = Alarms(':memory:')
    assert str(alarms) == '[]'

    data = [(1, 2), (3, 4)]

    for x, y in data:
        alarms.append((x, y))

    assert str(alarms) == '[(1, 2), (3, 4)]'
