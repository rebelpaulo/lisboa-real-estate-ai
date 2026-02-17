"""
Scraper Rápido - Extrai dados dos 6 sites OK
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

SITES_OK = [
    {"nome": "leilosoc.com", "url": "https://www.leilosoc.com/pt/leiloes/?categoria=imoveis"},
    {"nome": "vendajudicial.pt", "url": "https://vendajudicial.pt/"},
    {"nome": "avaliberica.pt", "url": "https://www.avaliberica.pt/leiloes/"},
    {"nome": "lcpremium.pt", "url": "https://www.lcpremium.pt/"},
    {"nome": "exclusivagora.com", "url": "https://www.exclusivagora.com/"},
    {"nome": "capital-leiloeira.pt", "url": "https://www.capital-leiloeira.pt/"},
]

async def scrape_site(site):
    """Extrai dados de um site"""
    imoveis = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"🔍 A aceder {site['nome']}...")
            await page.goto(site['url'], timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            # Scroll para carregar lazy content
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # Extrair todos os links e títulos
            elementos = await page.query_selector_all('a, h2, h3, .title, .property-title')
            
            for elem in elementos[:10]:  # Limitar a 10 por site
                try:
                    texto = await elem.inner_text()
                    href = await elem.get_attribute('href') if hasattr(elem, 'get_attribute') else None
                    
                    # Filtrar apenas elementos relevantes
                    if texto and len(texto) > 20 and any(kw in texto.lower() for kw in ['t1', 't2', 't3', 'apartamento', 'moradia', 'loja', '€', 'euro']):
                        imovel = {
                            "id": f"{site['nome']}_{len(imoveis)}",
                            "fonte": site['nome'],
                            "titulo": texto[:150].strip(),
                            "url": href if href and href.startswith('http') else site['url'],
                            "data_extracao": datetime.now().isoformat()
                        }
                        imoveis.append(imovel)
                except:
                    continue
            
            await browser.close()
            print(f"✅ {site['nome']}: {len(imoveis)} imóveis extraídos")
            
    except Exception as e:
        print(f"❌ {site['nome']}: {str(e)[:80]}")
    
    return imoveis

async def main():
    print("=" * 60)
    print("🚀 EXTRAÇÃO DE DADOS - 6 SITES")
    print("=" * 60)
    
    todos_imoveis = []
    
    for site in SITES_OK:
        imoveis = await scrape_site(site)
        todos_imoveis.extend(imoveis)
        await asyncio.sleep(1)  # Delay entre sites
    
    # Guardar resultados
    resultado = {
        "data_scraping": datetime.now().isoformat(),
        "sites_ok": len(SITES_OK),
        "total_imoveis": len(todos_imoveis),
        "imoveis": todos_imoveis
    }
    
    with open("imoveis_reais.json", 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print(f"Total de imóveis extraídos: {len(todos_imoveis)}")
    print(f"Dados guardados em: imoveis_reais.json")
    
    # Mostrar exemplos
    if todos_imoveis:
        print("\n🏠 Exemplos encontrados:")
        for i, imo in enumerate(todos_imoveis[:5], 1):
            print(f"{i}. [{imo['fonte']}] {imo['titulo'][:80]}...")

if __name__ == "__main__":
    asyncio.run(main())
