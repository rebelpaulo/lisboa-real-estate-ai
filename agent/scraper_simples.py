#!/usr/bin/env python3
"""
Scraper Simples - Teste rápido com output imediato
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

SITES = [
    {"nome": "leilosoc.com", "url": "https://www.leilosoc.com/pt/leiloes/?categoria=imoveis"},
    {"nome": "vendajudicial.pt", "url": "https://vendajudicial.pt/"},
    {"nome": "avaliberica.pt", "url": "https://www.avaliberica.pt/leiloes/"},
    {"nome": "lcpremium.pt", "url": "https://www.lcpremium.pt/"},
    {"nome": "exclusivagora.com", "url": "https://www.exclusivagora.com/"},
    {"nome": "capital-leiloeira.pt", "url": "https://www.capital-leiloeira.pt/"},
]

print("=" * 70)
print("🏠 SCRAPER SIMPLES - TESTE RÁPIDO")
print("=" * 70)
print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📍 Sites a processar: {len(SITES)}")
print("")

async def scrape_site(browser, site):
    """Scraper simples para um site"""
    print(f"📌 {site['nome']} - A iniciar...", flush=True)
    
    imoveis = []
    
    try:
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print(f"   🌐 A navegar para {site['url'][:50]}...", flush=True)
        
        # Navegar com timeout
        response = await page.goto(site['url'], timeout=30000, wait_until='domcontentloaded')
        
        print(f"   ✅ Página carregada (Status: {response.status if response else 'N/A'})", flush=True)
        
        # Aguardar um pouco para JS carregar
        await asyncio.sleep(3)
        
        # Extrair todo o texto da página
        content = await page.content()
        text = await page.inner_text('body')
        
        print(f"   📄 HTML: {len(content)} bytes | Texto: {len(text)} bytes", flush=True)
        
        # Procurar por padrões de imóveis
        # Padrão: T1, T2, Apartamento, Moradia + preço
        padroes_imoveis = [
            r'(T[0-5]|Apartamento|Moradia|Loja)[\s\w\-]+(?:\d+[\.\s]?\d+)\s*€',
            r'(\d+[\.\s]?\d+)\s*€[\s\w\-]+(?:T[0-5]|Apartamento|Moradia)',
        ]
        
        encontrados = 0
        for padrao in padroes_imoveis:
            matches = re.findall(padrao, text, re.IGNORECASE)
            encontrados += len(matches)
        
        print(f"   🔍 Padrões de imóveis encontrados: {encontrados}", flush=True)
        
        # Extrair links de imóveis
        links = await page.query_selector_all('a')
        links_imoveis = []
        
        for link in links[:30]:  # Limitar a 30 links
            try:
                href = await link.get_attribute('href') or ""
                texto = await link.inner_text()
                
                # Filtrar links relevantes
                if any(kw in texto.lower() for kw in ['t1', 't2', 't3', 'apartamento', 'moradia', 'imovel', 'leilao', '€']):
                    if len(texto) > 10 and len(texto) < 200:
                        links_imoveis.append({
                            'texto': texto.strip()[:100],
                            'url': href[:100] if href else ''
                        })
            except:
                pass
        
        print(f"   🔗 Links de imóveis: {len(links_imoveis)}", flush=True)
        
        # Criar entradas de imóveis dos links
        for i, link in enumerate(links_imoveis[:10]):  # Máximo 10 por site
            # Extrair preço
            preco_match = re.search(r'(\d+[\.\s]?\d+)\s*€', link['texto'])
            preco = None
            if preco_match:
                try:
                    preco_str = preco_match.group(1).replace('.', '').replace(' ', '')
                    preco = float(preco_str)
                except:
                    pass
            
            # Extrair tipologia
            tipos = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'Apartamento', 'Moradia', 'Loja']
            tipologia = None
            for tipo in tipos:
                if tipo.lower() in link['texto'].lower():
                    tipologia = tipo
                    break
            
            imoveis.append({
                'id': f"{site['nome'].split('.')[0]}_{i}",
                'fonte': site['nome'],
                'titulo': link['texto'],
                'tipologia': tipologia or 'Imóvel',
                'preco': preco,
                'url': link['url'] if link['url'].startswith('http') else f"https://{site['nome']}{link['url']}",
                'data_extracao': datetime.now().isoformat()
            })
        
        await context.close()
        
        print(f"   ✅ Concluído: {len(imoveis)} imóveis extraídos", flush=True)
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:80]}", flush=True)
    
    return imoveis

async def main():
    todos_imoveis = []
    
    async with async_playwright() as p:
        print("🚀 A lançar browser...", flush=True)
        browser = await p.chromium.launch(headless=True)
        print("✅ Browser pronto!\n", flush=True)
        
        for site in SITES:
            imoveis = await scrape_site(browser, site)
            todos_imoveis.extend(imoveis)
            print("")
        
        await browser.close()
    
    # Guardar resultados
    resultado = {
        'data_extracao': datetime.now().isoformat(),
        'total_imoveis': len(todos_imoveis),
        'imoveis': todos_imoveis
    }
    
    with open('dados_scraper_simples.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    print(f"Total de imóveis: {len(todos_imoveis)}")
    
    # Por fonte
    fontes = {}
    for imo in todos_imoveis:
        fontes[imo['fonte']] = fontes.get(imo['fonte'], 0) + 1
    
    print("\n📍 Por fonte:")
    for fonte, count in sorted(fontes.items(), key=lambda x: -x[1]):
        print(f"   • {fonte}: {count}")
    
    # Amostra
    if todos_imoveis:
        print("\n🏠 Amostra:")
        for imo in todos_imoveis[:5]:
            preco_str = f"€{imo['preco']:,.0f}" if imo['preco'] else "Preço não disponível"
            print(f"   • [{imo['fonte']}] {imo['tipologia']} - {preco_str}")
            print(f"     {imo['titulo'][:60]}...")
    
    print(f"\n💾 Guardado em: dados_scraper_simples.json")

if __name__ == "__main__":
    asyncio.run(main())
