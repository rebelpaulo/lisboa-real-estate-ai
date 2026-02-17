import aiohttp
import asyncio

sites = [
    'https://www.leilosoc.com/',
    'https://www.e-leiloes.pt/',
    'https://vendajudicial.pt/',
    'https://vendasjudiciais.pt/',
    'https://www.avaliberica.pt/',
    'https://www.lcpremium.pt/',
    'https://www.bidleiloeira.pt/',
    'https://www.exclusivagora.com/',
    'https://www.capital-leiloeira.pt/'
]

async def test(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                return url, resp.status
    except Exception as e:
        return url, str(e)[:50]

async def main():
    results = await asyncio.gather(*[test(u) for u in sites])
    print('='*60)
    print('RESULTADOS DOS 9 SITES:')
    print('='*60)
    for url, status in results:
        icon = '✅' if status == 200 else '❌'
        domain = url.split('/')[2]
        print(f'{icon} {domain}: {status}')

asyncio.run(main())
