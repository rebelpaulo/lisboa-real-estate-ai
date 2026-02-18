#!/usr/bin/env python3
"""
Scraper com ScraperAPI - Jarbas Imobiliário
Usa ScraperAPI como alternativa à Apify
"""

import requests
import json
import time
import re
from datetime import datetime
from urllib.parse import quote

# Configuração ScraperAPI
SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY', 'seu_token_aqui')
SCRAPERAPI_URL = "http://api.scraperapi.com"

# Sites de leilões
SITES = [
    {"nome": "Leilosoc", "url": "https://www.leilosoc.com/pt/leiloes/?categoria=imoveis", "ativo": True},
    {"nome": "Venda Judicial", "url": "https://www.vendajudicial.pt", "ativo": True},
    {"nome": "Aval Ibérica", "url": "https://www.avaliberica.pt/leiloes/", "ativo": True},
    {"nome": "LC Premium", "url": "https://www.lcpremium.pt", "ativo": True},
    {"nome": "Exclusiva Agora", "url": "https://www.exclusivagora.com", "ativo": True},
    {"nome": "Capital Leiloeira", "url": "https://www.capital-leiloeira.pt", "ativo": True},
]

def scrape_with_scraperapi(url, nome):
    """Faz scraping usando ScraperAPI"""
    print(f"\n📌 {nome}")
    print(f"   URL: {url}")
    
    # Construir URL da ScraperAPI
    api_url = f"{SCRAPERAPI_URL}/?api_key={SCRAPERAPI_KEY}&url={quote(url)}&render=true&country_code=pt"
    
    try:
        response = requests.get(api_url, timeout=60)
        
        if response.status_code == 200:
            html = response.text
            print(f"   ✅ HTML recebido: {len(html)} bytes")
            
            # Extrair imóveis do HTML
            imoveis = extrair_imoveis_do_html(html, nome, url)
            print(f"   🏠 Imóveis encontrados: {len(imoveis)}")
            
            return {
                "site": nome,
                "url": url,
                "status": response.status_code,
                "html_size": len(html),
                "imoveis": imoveis,
                "timestamp": datetime.now().isoformat()
            }
        else:
            print(f"   ❌ Erro HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:80]}")
        return None

def extrair_imoveis_do_html(html, fonte, base_url):
    """Extrai dados de imóveis do HTML"""
    imoveis = []
    
    # Padrões comuns para imóveis em sites de leilão
    padroes = [
        # Padrão 1: Cards com preço e localização
        r'([\w\s\-]+(?:T[0-5]|Moradia|Apartamento|Loja|Terreno)[\w\s\-]*).*?(\d+[\s\.]?\d+)\s*€.*?([\w\s]+(?:Lisboa|Porto|Cascais|Sintra|Oeiras|Loures|Amadora|Almada|Seixal|Setúbal)[\w\s]*)',
        # Padrão 2: Preço seguido de área
        r'(\d+[\s\.]?\d+)\s*€.*?([\d\.]+)\s*m[²2].*?(T[0-5]|Moradia)',
        # Padrão 3: Títulos de imóveis
        r'(Leilão.*?T[0-5].*?)(\d+[\s\.]?\d+)\s*€',
    ]
    
    # Procurar por padrões no HTML
    for padrao in padroes:
        matches = re.findall(padrao, html, re.IGNORECASE | re.DOTALL)
        for match in matches[:10]:  # Limitar a 10 por padrão
            if isinstance(match, tuple):
                texto = ' '.join(str(m) for m in match if m)
            else:
                texto = str(match)
            
            # Extrair preço
            preco_match = re.search(r'(\d+[\s\.]?\d+)\s*€', texto)
            preco = None
            if preco_match:
                preco_str = preco_match.group(1).replace('.', '').replace(' ', '')
                preco = float(preco_str) if preco_str.isdigit() else None
            
            # Extrair área
            area_match = re.search(r'(\d+)\s*m[²2]', texto, re.IGNORECASE)
            area = int(area_match.group(1)) if area_match else None
            
            # Extrair tipologia
            tipos = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'Moradia', 'Loja', 'Terreno']
            tipologia = None
            for tipo in tipos:
                if tipo.lower() in texto.lower():
                    tipologia = tipo
                    break
            
            if preco and preco > 10000:  # Filtrar preços válidos
                imovel = {
                    "id": f"{fonte.lower().replace(' ', '_')}_{len(imoveis)}",
                    "titulo": texto[:150].strip(),
                    "preco": preco,
                    "preco_texto": f"€{preco:,.0f}",
                    "area": area,
                    "tipologia": tipologia or "Imóvel",
                    "fonte": fonte,
                    "url": base_url,
                    "data_extracao": datetime.now().isoformat()
                }
                imoveis.append(imovel)
    
    # Remover duplicados baseado no título
    imoveis_unicos = []
    titulos_vistos = set()
    for imo in imoveis:
        titulo_base = imo["titulo"][:50].lower()
        if titulo_base not in titulos_vistos:
            titulos_vistos.add(titulo_base)
            imoveis_unicos.append(imo)
    
    return imoveis_unicos

def main():
    print("=" * 70)
    print("🏠 SCRAPERAPI - EXTRATOR DE IMÓVEIS")
    print("=" * 70)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Key: {SCRAPERAPI_KEY[:10]}...")
    
    resultados = []
    todos_imoveis = []
    
    for site in SITES:
        if not site["ativo"]:
            continue
            
        resultado = scrape_with_scraperapi(site["url"], site["nome"])
        if resultado:
            resultados.append(resultado)
            todos_imoveis.extend(resultado.get("imoveis", []))
        
        time.sleep(2)  # Respeitar rate limits
    
    # Guardar resultados detalhados
    output = {
        "data_extracao": datetime.now().isoformat(),
        "total_sites": len(SITES),
        "sites_sucesso": len(resultados),
        "total_imoveis": len(todos_imoveis),
        "resultados": resultados
    }
    
    with open("extracao_scraperapi_detalhes.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # Guardar apenas os imóveis (formato simplificado)
    imoveis_output = {
        "data_extracao": datetime.now().isoformat(),
        "total_imoveis": len(todos_imoveis),
        "imoveis": todos_imoveis
    }
    
    with open("imoveis_scraperapi.json", "w", encoding="utf-8") as f:
        json.dump(imoveis_output, f, ensure_ascii=False, indent=2)
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DA EXTRAÇÃO")
    print("=" * 70)
    print(f"Sites testados: {len(SITES)}")
    print(f"Sites com resposta: {len(resultados)}")
    print(f"Total de imóveis extraídos: {len(todos_imoveis)}")
    
    # Estatísticas por site
    print("\n📈 Por site:")
    for r in resultados:
        count = len(r.get("imoveis", []))
        print(f"   • {r['site']}: {count} imóveis")
    
    # Amostra de imóveis
    if todos_imoveis:
        print("\n🏠 Amostra de imóveis encontrados:")
        for i, imo in enumerate(todos_imoveis[:5], 1):
            print(f"\n   {i}. [{imo['fonte']}] {imo['tipologia']}")
            print(f"      Preço: {imo['preco_texto']}")
            if imo.get('area'):
                print(f"      Área: {imo['area']} m²")
            print(f"      {imo['titulo'][:80]}...")
    
    print(f"\n💾 Ficheiros guardados:")
    print(f"   • extracao_scraperapi_detalhes.json (detalhes completos)")
    print(f"   • imoveis_scraperapi.json (apenas imóveis)")
    
    return todos_imoveis

if __name__ == "__main__":
    imoveis = main()
