from metrics import work_metrics
import asyncio


async def main():
    partner = 1
    partner_list = [1]
    date_start = '2024-08-21T00:00:00'
    date_end = '2024-08-22T00:00:00'
    units = ['000d3a240c719a8711e68aba13f81faa', '000d3a24d2b7a94311e8bd9d5101a4b5']
    metrics = await work_metrics((partner, partner_list), date_start, date_end,
                                 units=units)
    for unit in units:
        for key, value in metrics[unit].items():
            print(value.__dict__)

if __name__ == '__main__':
    asyncio.run(main())
