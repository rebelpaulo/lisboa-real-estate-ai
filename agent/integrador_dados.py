"""
Integrador de Dados - Extrai e integra dados dos 6 sites OK
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

SITES_OK = [
    {"nome": "leilosoc.com", "url": "https://www.leilosoc.com/pt/leiloes/?categoria=imoveis", "tipo": "leiloes"},
    {"nome": "vendajudicial.pt", "url": "https://vendajudicial.pt/", "tipo": "vendas"},
    {"nome": "avaliberica.pt", "url": "https://www.avaliberica.pt/leiloes/", "tipo": "leiloes"},
    {"nome": "lcpremium.pt", "url": "https://www.lcpremium.pt/", "tipo": "leiloes"},
    {"nome": "exclusivagora.com", "url": "https://www.exclusivagora.com/", "tipo": "leiloes"},
    {"nome": "capital-leiloeira.pt", "url": "https://www.capital-leiloeira.pt/", "tipo": "leiloes"},
]

def extrair_preco(texto):
    """Extrai preço do texto"""
    padroes = [
        r'(\d+[\s\.]?\d+)\s*€',
        r'€\s*(\d+[\s\.]?\d+)',
        r'(\d+)\.?\d{0,3}\s*,?\d{0,2}\s*€'
    ]
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            try:
                preco_str = match.group(1).replace('.', '').replace(' ', '').replace(',', '.')
                return float(preco_str)
            except:
                continue
    return None

def extrair_area(texto):
    """Extrai área do texto"""
    padroes = [
        r'(\d+)\s*m2',
        r'(\d+)\s*m²',
        r'(\d+)\s*metros',
        r'(\d+)\s*m\s*2'
    ]
    for padrao in padroes:
        match = re.search(padrao, texto.lower())
        if match:
            try:
                return float(match.group(1))
            except:
                continue
    return None

def extrair_tipologia(texto):
    """Extrai tipologia do texto"""
    tipos = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'Moradia', 'Loja', 'Armazém', 'Terreno']
    for tipo in tipos:
        if tipo.lower() in texto.lower():
            return tipo
    return "Desconhecido"

async def scrape_leilosoc(page):
    """Scraper específico para leilosoc.com"""
    imoveis = []
    
    try:
        # Aguardar cards de imóveis
        await page.wait_for_selector('.property-item, .auction-item, .card, article', timeout=10000)
        
        cards = await page.query_selector_all('.property-item, .auction-item, .card, article, .col-md-4, .col-lg-4')
        
        for card in cards[:15]:
            try:
                # Extrair título
                titulo_elem = await card.query_selector('h2, h3, h4, .title, .property-title, a')
                titulo = await titulo_elem.inner_text() if titulo_elem else "Sem título"
                titulo = titulo.strip()
                
                # Extrair preço
                preco_elem = await card.query_selector('.price, .value, .amount, strong')
                preco_texto = await preco_elem.inner_text() if preco_elem else ""
                preco = extrair_preco(preco_texto) or extrair_preco(titulo) or 0
                
                # Extrair área
                area = extrair_area(titulo) or extrair_area(await card.inner_text())
                
                # Extrair tipologia
                tipo = extrair_tipologia(titulo)
                
                # Extrair link
                link_elem = await card.query_selector('a')
                href = await link_elem.get_attribute('href') if link_elem else ""
                if href and not href.startswith('http'):
                    href = f"https://www.leilosoc.com{href}"
                
                if titulo and len(titulo) > 10:
                    imoveis.append({
                        "id": f"leilosoc_{len(imoveis)}",
                        "fonte": "leilosoc.com",
                        "titulo": titulo[:150],
                        "tipo": tipo,
                        "preco": preco,
                        "area_m2": area,
                        "preco_m2": round(preco / area, 2) if area and preco else None,
                        "url": href or "https://www.leilosoc.com/",
                        "data_extracao": datetime.now().isoformat()
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Erro leilosoc: {e}")
    
    return imoveis

async def scrape_generico(page, site):
    """Scraper genérico para outros sites"""
    imoveis = []
    
    try:
        # Aguardar conteúdo carregar
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(3)  # Esperar JS executar
        
        # Procurar por cards
        seletores = [
            '.property', '.imovel', '.leilao', '.item', '.card',
            'article', '.col-md-4', '.col-lg-4', '.col-sm-6'
        ]
        
        cards = []
        for seletor in seletores:
            cards = await page.query_selector_all(seletor)
            if len(cards) > 0:
                break
        
        # Se não encontrou cards, procurar todos os links
        if not cards:
            cards = await page.query_selector_all('a')
        
        for card in cards[:15]:
            try:
                texto = await card.inner_text()
                texto = texto.strip()
                
                # Filtrar apenas elementos relevantes
                if len(texto) < 30:
                    continue
                    
                keywords = ['t1', 't2', 't3', 'apartamento', 'moradia', 'loja', '€', 'euro', 'm2', 'metro']
                if not any(kw in texto.lower() for kw in keywords):
                    continue
                
                preco = extrair_preco(texto)
                area = extrair_area(texto)
                tipo = extrair_tipologia(texto)
                
                href = await card.get_attribute('href')
                if href and not href.startswith('http'):
                    href = f"https://{site['nome']}{href}"
                elif not href:
                    href = site['url']
                
                imoveis.append({
                    "id": f"{site['nome'].split('.')[0]}_{len(imoveis)}",
                    "fonte": site['nome'],
                    "titulo": texto[:150],
                    "tipo": tipo,
                    "preco": preco or 0,
                    "area_m2": area,
                    "preco_m2": round(preco / area, 2) if area and preco else None,
                    "url": href,
                    "data_extracao": datetime.now().isoformat()
                })
            except:
                continue
                
    except Exception as e:
        print(f"Erro genérico {site['nome']}: {e}")
    
    return imoveis

async def integrar_dados():
    """Integra dados de todos os sites"""
    print("=" * 70)
    print("🚀 INTEGRAÇÃO DE DADOS - 6 SITES DE LEILÕES")
    print("=" * 70)
    
    todos_imoveis = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for i, site in enumerate(SITES_OK, 1):
            print(f"\n📌 [{i}/6] A processar {site['nome']}...")
            
            try:
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navegar para o site
                await page.goto(site['url'], timeout=45000)
                
                # Scraper específico ou genérico
                if site['nome'] == 'leilosoc.com':
                    imoveis = await scrape_leilosoc(page)
                else:
                    imoveis = await scrape_generico(page, site)
                
                print(f"✅ {site['nome']}: {len(imoveis)} imóveis extraídos")
                todos_imoveis.extend(imoveis)
                
                await context.close()
                await asyncio.sleep(2)  # Delay entre sites
                
            except Exception as e:
                print(f"❌ {site['nome']}: {str(e)[:80]}")
        
        await browser.close()
    
    # Guardar resultados
    resultado = {
        "data_integracao": datetime.now().isoformat(),
        "sites_processados": len(SITES_OK),
        "total_imoveis": len(todos_imoveis),
        "imoveis": todos_imoveis
    }
    
    with open("dados_integrados.json", 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    # Criar também CSV para análise
    import csv
    with open("dados_integrados.csv", 'w', newline='', encoding='utf-8') as f:
        if todos_imoveis:
            writer = csv.DictWriter(f, fieldnames=todos_imoveis[0].keys())
            writer.writeheader()
            writer.writerows(todos_imoveis)
    
    print("\n" + "=" * 70)
    print("📊 RESUMO DA INTEGRAÇÃO")
    print("=" * 70)
    print(f"Total de imóveis integrados: {len(todos_imoveis)}")
    print(f"Ficheiros criados:")
    print(f"  • dados_integrados.json")
    print(f"  • dados_integrados.csv")
    
    # Estatísticas
    if todos_imoveis:
        com_preco = [i for i in todos_imoveis if i['preco'] > 0]
        com_area = [i for i in todos_imoveis if i['area_m2']]
        print(f"\n📈 Estatísticas:")
        print(f"  • Com preço: {len(com_preco)}/{len(todos_imoveis)}")
        print(f"  • Com área: {len(com_area)}/{len(todos_imoveis)}")
        
        # Por fonte
        print(f"\n📍 Por fonte:")
        fontes = {}
        for imo in todos_imoveis:
            fontes[imo['fonte']] = fontes.get(imo['fonte'], 0) + 1
        for fonte, count in sorted(fontes.items(), key=lambda x: -x[1]):
            print(f"  • {fonte}: {count} imóveis")
    
    return resultado

if __name__ == "__main__":
    resultado = asyncio.run(integrar_dados())
