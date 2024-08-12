from metrics import work_metrics
import asyncio


async def main():
    await work_metrics()


if __name__ == '__main__':
    asyncio.run(main())
