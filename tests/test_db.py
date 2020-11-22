import pytest

from svetlana.db import Pollers


def test_iter_append(mocker, monkeypatch):
    pollers = Pollers(':memory:')
    data = [(1, 2), (3, 4)]

    for x, y in data:
        pollers.append((x, y))

    for i, obj in enumerate(pollers):
        print(i)
        x, y = obj
        assert x == data[i][0]
        assert y == data[i][1]

    assert (1, 2) in pollers
    assert (1, 3) not in pollers

    pollers.remove((1, 2))
    assert (1, 2) not in pollers
