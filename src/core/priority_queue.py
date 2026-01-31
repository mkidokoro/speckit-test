"""優先度キュー実装 (asyncio.PriorityQueue)  
日本語コメント: FIRE=1, SECURITY=2, CALL=3 の優先度を扱う
"""
import asyncio
from dataclasses import dataclass

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: object

class AlertPriorityQueue:
    """優先度付きキューのラッパー。

    日本語コメント: 非同期で put/get を行えるようにする。
    """
    def __init__(self):
        self._q = asyncio.PriorityQueue()

    async def put(self, alert, priority: int):
        """警報をキューに追加。"""
        await self._q.put(PrioritizedItem(priority, alert))

    async def get(self):
        """キューから次の要素を取得。"""
        item = await self._q.get()
        return item.item

    def qsize(self):
        return self._q.qsize()
