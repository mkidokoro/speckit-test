"""アプリケーションのエントリポイント（簡易）
日本語コメント: 非同期ランナーを起動します
"""
import asyncio
from src.core.asyncio_manager import AsyncIOManager

async def main_async():
    """メインの非同期処理。将来的に依存サービスを起動します。"""
    manager = AsyncIOManager()
    await manager.run_main()

def main():
    """同期エントリポイント。"""
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
