"""
Scraper Definitivo - Extrai dados completos dos 6 sites OK
Com informação detalhada para cards expandidos
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
    padroes = [r'(\d+[\.\s]?\d+)\s*€', r'€\s*(\d+[\.\s]?\d+)', r'(\d+)\.?\d{0,3}\s*€']
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            try:
                return float(match.group(1).replace('.', '').replace(' ', '').replace(',', '.'))
            except:
                continue
    return None

def extrair_area(texto):
    padroes = [r'(\d+)\s*m2', r'(\d+)\s*m²', r'(\d+)\s*metros', r'(\d+)\s*m\s*2']
    for padrao in padroes:
        match = re.search(padrao, texto.lower())
        if match:
            try:
                return float(match.group(1))
            except:
                continue
    return None

def extrair_tipologia(texto):
    tipos = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'Moradia', 'Loja', 'Armazém', 'Terreno', 'Prédio']
    for tipo in tipos:
        if tipo.lower() in texto.lower():
            return tipo
    return "Imóvel"

def extrair_localizacao(texto):
    # Procurar por padrões de localização em Portugal
    concelhos = ['Lisboa', 'Oeiras', 'Cascais', 'Sintra', 'Amadora', 'Loures', 'Almada', 'Seixal']
    for concelho in concelhos:
        if concelho.lower() in texto.lower():
            return concelho
    return "Grande Lisboa"

async def scrape_site_detalhado(site):
    """Faz scraping detalhado de um site"""
    imoveis = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            print(f"🔍 A aceder {site['nome']}...")
            await page.goto(site['url'], timeout=60000, wait_until='domcontentloaded')
            
            # Aguardar carregamento
            await asyncio.sleep(5)
            
            # Scroll para carregar lazy content
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
            
            # Procurar cards de imóveis
            seletores = [
                '.property-item', '.auction-item', '.card', 'article',
                '.col-md-4', '.col-lg-4', '.col-sm-6', '.item',
                '[class*="property"]', '[class*="imovel"]', '[class*="leilao"]'
            ]
            
            cards = []
            for seletor in seletores:
                cards = await page.query_selector_all(seletor)
                if len(cards) > 0:
                    print(f"  ✓ Encontrados {len(cards)} elementos com '{seletor}'")
                    break
            
            # Se não encontrou, tentar todos os links
            if not cards:
                cards = await page.query_selector_all('a')
                print(f"  ⚠ A usar todos os links ({len(cards)} encontrados)")
            
            for i, card in enumerate(cards[:20]):  # Máximo 20 por site
                try:
                    # Extrair texto completo
                    texto = await card.inner_text()
                    texto = texto.strip()
                    
                    # Filtrar apenas elementos relevantes
                    if len(texto) < 30:
                        continue
                    
                    keywords = ['t1', 't2', 't3', 'apartamento', 'moradia', 'loja', '€', 'euro', 'm2', 'metro', 'lei']
                    if not any(kw in texto.lower() for kw in keywords):
                        continue
                    
                    # Extrair dados
                    preco = extrair_preco(texto)
                    area = extrair_area(texto)
                    tipo = extrair_tipologia(texto)
                    localizacao = extrair_localizacao(texto)
                    
                    # Extrair título (primeira linha ou texto curto)
                    linhas = [l.strip() for l in texto.split('\n') if l.strip()]
                    titulo = linhas[0] if linhas else texto[:100]
                    
                    # Descrição (restante do texto)
                    descricao = '\n'.join(linhas[1:5]) if len(linhas) > 1 else texto[100:300]
                    
                    # Link
                    href = await card.get_attribute('href')
                    if href:
                        if not href.startswith('http'):
                            href = f"https://{site['nome']}{href}"
                    else:
                        href = site['url']
                    
                    # Extrair imagem se existir
                    img_elem = await card.query_selector('img')
                    imagem = await img_elem.get_attribute('src') if img_elem else None
                    
                    imovel = {
                        "id": f"{site['nome'].split('.')[0]}_{i}",
                        "fonte": site['nome'],
                        "tipo": tipo,
                        "titulo": titulo[:150],
                        "descricao": descricao[:500],
                        "localizacao": localizacao,
                        "concelho": localizacao,
                        "freguesia": "",
                        "preco": preco or 0,
                        "preco_original": None,
                        "area_m2": area,
                        "preco_m2": round(preco / area, 2) if area and preco else None,
                        "tipologia": tipo,
                        "quartos": None,
                        "casas_banho": None,
                        "estado": "Em Leilão",
                        "data_leilao": None,
                        "url": href,
                        "imagem": imagem,
                        "imagens": [imagem] if imagem else [],
                        "contacto": None,
                        "notas": f"Extraído de {site['nome']}",
                        "data_extracao": datetime.now().isoformat()
                    }
                    
                    imoveis.append(imovel)
                    
                except Exception as e:
                    continue
            
            await context.close()
            
        except Exception as e:
            print(f"  ❌ Erro: {str(e)[:80]}")
        
        await browser.close()
    
    return imoveis

async def main():
    print("=" * 70)
    print("🚀 SCRAPER DEFINITIVO - 6 SITES")
    print("=" * 70)
    
    todos_imoveis = []
    
    for i, site in enumerate(SITES_OK, 1):
        print(f"\n📌 [{i}/6] {site['nome']}")
        imoveis = await scrape_site_detalhado(site)
        print(f"✅ {len(imoveis)} imóveis extraídos")
        todos_imoveis.extend(imoveis)
        await asyncio.sleep(3)  # Delay entre sites
    
    # Guardar resultados
    resultado = {
        "data_scraping": datetime.now().isoformat(),
        "sites_processados": len(SITES_OK),
        "total_imoveis": len(todos_imoveis),
        "imoveis": todos_imoveis
    }
    
    # JSON completo
    with open("dados_reais_completos.json", 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    # JSON para dashboard (formato simplificado)
    dashboard_data = {
        "properties": [
            {
                "id": imo["id"],
                "title": imo["titulo"],
                "location": imo["localizacao"],
                "parish": imo["freguesia"],
                "price": imo["preco"],
                "originalPrice": imo["preco_original"],
                "area": imo["area_m2"] or 0,
                "typology": imo["tipologia"],
                "bedrooms": imo["quartos"] or 0,
                "bathrooms": imo["casas_banho"] or 0,
                "category": "D",
                "opportunityScore": 65,
                "daysOnMarket": 30,
                "priceDrops": 0,
                "vsMarket": -5,
                "images": imo["imagens"] or ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800"],
                "source": imo["fonte"],
                "url": imo["url"],
                "description": imo["descricao"]
            }
            for imo in todos_imoveis
        ]
    }
    
    with open("../dashboard/public/data/properties.json", 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    print(f"Total de imóveis: {len(todos_imoveis)}")
    print(f"Ficheiros criados:")
    print(f"  • dados_reais_completos.json")
    print(f"  • dashboard/public/data/properties.json")
    
    # Estatísticas
    if todos_imoveis:
        com_preco = len([i for i in todos_imoveis if i['preco'] > 0])
        com_area = len([i for i in todos_imoveis if i['area_m2']])
        print(f"\n📈 Estatísticas:")
        print(f"  • Com preço: {com_preco}/{len(todos_imoveis)}")
        print(f"  • Com área: {com_area}/{len(todos_imoveis)}")
        
        # Por fonte
        print(f"\n📍 Por fonte:")
        fontes = {}
        for imo in todos_imoveis:
            fontes[imo['fonte']] = fontes.get(imo['fonte'], 0) + 1
        for fonte, count in sorted(fontes.items(), key=lambda x: -x[1]):
            print(f"  • {fonte}: {count}")
        
        # Exemplos
        print(f"\n🏠 Exemplos:")
        for i, imo in enumerate(todos_imoveis[:3], 1):
            print(f"{i}. [{imo['fonte']}] {imo['titulo'][:70]}")
            print(f"   Preço: €{imo['preco']:,.0f}" if imo['preco'] else "   Preço: N/A")
    
    return resultado

if __name__ == "__main__":
    asyncio.run(main())
