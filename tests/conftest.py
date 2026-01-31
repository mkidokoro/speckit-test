import pytest
import asyncio

@pytest.fixture
def event_loop():
    """pytest-asyncio 用のイベントループフィクスチャ。日本語コメント: テストで共有するループを提供"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
