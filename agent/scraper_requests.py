"""
Scraper Rápido com Requests - Para sites simples
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

SITES_RAPIDOS = [
    {"nome": "leilosoc.com", "url": "https://www.leilosoc.com/pt/leiloes/?categoria=imoveis"},
    {"nome": "vendajudicial.pt", "url": "https://vendajudicial.pt/"},
    {"nome": "avaliberica.pt", "url": "https://www.avaliberica.pt/leiloes/"},
]

def extrair_dados_html(html, fonte):
    """Extrai dados de imóveis do HTML"""
    imoveis = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Procurar por cards de imóveis
    seletores = ['.property', '.imovel', '.leilao', '.card', 'article', '.col-md-4', '.item']
    
    for seletor in seletores:
        cards = soup.select(seletor)
        if cards:
            for card in cards[:10]:
                try:
                    texto = card.get_text(strip=True)
                    if len(texto) < 20:
                        continue
                    
                    # Extrair preço
                    preco_match = re.search(r'(\d+[\.\s]?\d+)\s*€', texto)
                    preco = float(preco_match.group(1).replace('.', '').replace(' ', '')) if preco_match else 0
                    
                    # Extrair área
                    area_match = re.search(r'(\d+)\s*m[2²]', texto.lower())
                    area = float(area_match.group(1)) if area_match else None
                    
                    # Extrair tipologia
                    tipos = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'Moradia', 'Loja']
                    tipo = next((t for t in tipos if t in texto), 'Desconhecido')
                    
                    # Link
                    link_elem = card.find('a', href=True)
                    href = link_elem['href'] if link_elem else ''
                    
                    imoveis.append({
                        "id": f"{fonte}_{len(imoveis)}",
                        "fonte": fonte,
                        "titulo": texto[:120],
                        "tipo": tipo,
                        "preco": preco,
                        "area_m2": area,
                        "preco_m2": round(preco / area, 2) if area and preco else None,
                        "url": href if href.startswith('http') else f"https://{fonte}{href}",
                        "data_extracao": datetime.now().isoformat()
                    })
                except:
                    continue
            break
    
    return imoveis

def scraper_rapido():
    """Scraper rápido usando requests"""
    print("=" * 60)
    print("🚀 SCRAPER RÁPIDO - 3 SITES")
    print("=" * 60)
    
    todos_imoveis = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for site in SITES_RAPIDOS:
        print(f"\n📌 A processar {site['nome']}...")
        
        try:
            response = requests.get(site['url'], headers=headers, timeout=15)
            
            if response.status_code == 200:
                imoveis = extrair_dados_html(response.text, site['nome'])
                print(f"✅ {site['nome']}: {len(imoveis)} imóveis")
                todos_imoveis.extend(imoveis)
            else:
                print(f"❌ {site['nome']}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {site['nome']}: {str(e)[:60]}")
    
    # Guardar resultados
    resultado = {
        "data_scraping": datetime.now().isoformat(),
        "sites": len(SITES_RAPIDOS),
        "total_imoveis": len(todos_imoveis),
        "imoveis": todos_imoveis
    }
    
    with open("dados_rapidos.json", 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print(f"Total: {len(todos_imoveis)} imóveis")
    print(f"Guardado em: dados_rapidos.json")
    
    if todos_imoveis:
        print("\n🏠 Exemplos:")
        for i, imo in enumerate(todos_imoveis[:5], 1):
            print(f"{i}. [{imo['fonte']}] {imo['titulo'][:60]}...")
            if imo['preco']:
                print(f"   Preço: €{imo['preco']:,.0f}")
    
    return resultado

if __name__ == "__main__":
    scraper_rapido()
