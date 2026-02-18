#!/usr/bin/env python3
"""
Extração Manual de Imóveis - Jarbas
Script otimizado para extrair dados de leilões
"""

import requests
import json
import time
from datetime import datetime

APIFY_TOKEN = os.getenv('APIFY_TOKEN', 'seu_token_aqui')

def extrair_site(url, nome):
    """Extrai dados de um site de leilões"""
    print(f"\n📌 {nome}")
    print(f"   URL: {url}")
    
    run_input = {
        "startUrls": [{"url": url}],
        "maxCrawlPages": 3,
        "crawlerType": "playwright:adaptive",
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        },
        "waitFor": "body",
        "pageFunction": """
        async function pageFunction(context) {
            const { page, request, log } = context;
            
            // Aguardar carregamento
            await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
            
            // Extrair todos os links de imóveis
            const links = await page.evaluate(() => {
                const imoveis = [];
                const elementos = document.querySelectorAll('a[href*="imovel"], a[href*="leilao"], a[href*="propriedade"], article, .property-card, .auction-item');
                
                elementos.forEach(el => {
                    const texto = el.innerText || el.textContent || '';
                    const href = el.href || '';
                    
                    if (texto.length > 20 && (texto.includes('€') || texto.match(/T[0-5]/))) {
                        imoveis.push({
                            texto: texto.trim().substring(0, 300),
                            url: href
                        });
                    }
                });
                
                return imoveis.slice(0, 10);
            });
            
            return {
                url: request.url,
                imoveis: links,
                titulo: await page.title(),
                timestamp: new Date().toISOString()
            };
        }
        """
    }
    
    try:
        response = requests.post(
            "https://api.apify.com/v2/acts/apify~website-content-crawler/run-sync-get-dataset-items",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"},
            json=run_input,
            timeout=120
        )
        
        if response.status_code == 200:
            items = response.json()
            if items and len(items) > 0:
                item = items[0]
                status = item.get('crawl', {}).get('httpStatusCode', 'N/A')
                titulo = item.get('titulo', 'N/A')
                imoveis = item.get('imoveis', [])
                
                print(f"   Status: {status}")
                print(f"   Título: {titulo[:50] if titulo else 'N/A'}...")
                print(f"   Imóveis encontrados: {len(imoveis)}")
                
                return {
                    'site': nome,
                    'url': url,
                    'status': status,
                    'imoveis': imoveis,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"   ⚠️ Nenhum dado retornado")
                return None
        else:
            print(f"   ❌ Erro HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:80]}")
        return None

def main():
    print("=" * 70)
    print("🏠 EXTRAÇÃO MANUAL - JARBAS IMOBILIÁRIO")
    print("=" * 70)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sites = [
        ("https://leilosoc.com/pt-pt/leiloes/?categoria=imoveis", "Leilosoc"),
        ("https://www.vendajudicial.pt", "Venda Judicial"),
        ("https://www.avaliberica.pt/leiloes/", "Aval Ibérica"),
        ("https://www.lcpremium.pt", "LC Premium"),
        ("https://www.exclusivagora.com", "Exclusiva Agora"),
    ]
    
    resultados = []
    
    for url, nome in sites:
        resultado = extrair_site(url, nome)
        if resultado:
            resultados.append(resultado)
        time.sleep(2)  # Pequena pausa entre sites
    
    # Guardar resultados
    output = {
        "data_extracao": datetime.now().isoformat(),
        "total_sites": len(sites),
        "sites_sucesso": len(resultados),
        "resultados": resultados
    }
    
    with open("extracao_manual_resultado.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    print(f"Sites testados: {len(sites)}")
    print(f"Sites com dados: {len(resultados)}")
    
    total_imoveis = sum(len(r.get('imoveis', [])) for r in resultados)
    print(f"Total imóveis encontrados: {total_imoveis}")
    
    print(f"\n💾 Resultados guardados em: extracao_manual_resultado.json")
    
    # Mostrar amostra
    if resultados:
        print("\n📋 Amostra de imóveis:")
        for r in resultados[:2]:
            print(f"\n🏢 {r['site']}:")
            for i, imo in enumerate(r.get('imoveis', [])[:3], 1):
                texto = imo.get('texto', 'N/A')[:80]
                print(f"   {i}. {texto}...")

if __name__ == "__main__":
    main()
