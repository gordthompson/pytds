from __future__ import annotations

import datetime
from typing import Optional, Union, Tuple

from pytds.tds_base import AuthProtocol
from pytds.tds import _TdsSocket

PoolKeyType = Tuple[
    Optional[str],
    Optional[str],
    Optional[str],
    int,
    Optional[str],
    int,
    bool,
    Optional[str],
    int,
    bool,
    bool,
    Union[AuthProtocol, None],
    datetime.tzinfo,
    bool]


class ConnectionPool:
    def __init__(self, max_pool_size: int = 100, min_pool_size: int = 0):
        self._max_pool_size = max_pool_size
        self._pool: dict[PoolKeyType, list[tuple[_TdsSocket, _TdsSession]]] = {}

    def add(self, key: PoolKeyType, conn: tuple[_TdsSocket, _TdsSession]) -> None:
        self._pool.setdefault(key, []).append(conn)

    def take(self, key: PoolKeyType) -> tuple[_TdsSocket, _TdsSession] | None:
        l = self._pool.get(key, [])
        if len(l) > 0:
            return l.pop()
        else:
            return None


connection_pool = ConnectionPool()
