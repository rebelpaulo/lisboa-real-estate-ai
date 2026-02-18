"""
Scraper Apify - Extrai dados reais dos sites de leilões
Usa Apify com proxies residenciais
"""

import asyncio
import json
import requests
from datetime import datetime

# Configuração
APIFY_TOKEN = os.getenv('APIFY_TOKEN', 'seu_token_aqui')

SITES = [
    {"nome": "leilosoc.com", "url": "https://www.leilosoc.com/pt/leiloes/?categoria=imoveis"},
    {"nome": "vendajudicial.pt", "url": "https://vendajudicial.pt/"},
    {"nome": "avaliberica.pt", "url": "https://www.avaliberica.pt/leiloes/"},
    {"nome": "lcpremium.pt", "url": "https://www.lcpremium.pt/"},
    {"nome": "exclusivagora.com", "url": "https://www.exclusivagora.com/"},
    {"nome": "capital-leiloeira.pt", "url": "https://www.capital-leiloeira.pt/"},
]

def run_apify_scraper(url, nome):
    """Executa scraper Apify para um site"""
    
    # Usar o Website Content Crawler da Apify
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
            const { request, log, jQuery: $ } = context;
            const data = [];
            
            // Procurar por cards de imóveis
            const cards = $('.property-item, .auction-item, .card, article, .col-md-4, .col-lg-4, .item');
            
            cards.each((i, el) => {
                const $el = $(el);
                const texto = $el.text().trim();
                
                if (texto.length > 30 && (texto.includes('€') || texto.includes('m2') || texto.includes('T1') || texto.includes('T2') || texto.includes('T3'))) {
                    // Extrair preço
                    const precoMatch = texto.match(/(\d+[.\s]?\d+)\s*€/);
                    const preco = precoMatch ? parseFloat(precoMatch[1].replace('.', '').replace(' ', '')) : null;
                    
                    // Extrair área
                    const areaMatch = texto.match(/(\d+)\s*m[2²]/i);
                    const area = areaMatch ? parseFloat(areaMatch[1]) : null;
                    
                    // Extrair tipologia
                    const tipos = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'Moradia', 'Loja', 'Terreno'];
                    const tipo = tipos.find(t => texto.includes(t)) || 'Imóvel';
                    
                    // Título (primeira linha)
                    const titulo = texto.split('\n')[0].substring(0, 150);
                    
                    data.push({
                        titulo: titulo,
                        textoCompleto: texto.substring(0, 500),
                        preco: preco,
                        area: area,
                        tipo: tipo,
                        url: request.url
                    });
                }
            });
            
            return {
                url: request.url,
                imoveis: data.slice(0, 10)  // Máximo 10 por site
            };
        }
        """
    }
    
    try:
        # Iniciar run síncrono
        response = requests.post(
            "https://api.apify.com/v2/acts/apify~website-content-crawler/run-sync-get-dataset-items",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"},
            json=run_input,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ {nome}: Erro {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ {nome}: {str(e)[:80]}")
        return None

def main():
    print("=" * 70)
    print("🚀 SCRAPER APIFY - TESTE GRATUITO")
    print("=" * 70)
    
    todos_imoveis = []
    
    # Testar apenas 2 sites (para economizar créditos)
    sites_teste = SITES[:2]
    
    for site in sites_teste:
        print(f"\n📌 A processar {site['nome']}...")
        
        resultado = run_apify_scraper(site['url'], site['nome'])
        
        if resultado and isinstance(resultado, list) and len(resultado) > 0:
            # Extrair dados do resultado
            for item in resultado:
                if 'imoveis' in item:
                    for imo in item['imoveis']:
                        imo['fonte'] = site['nome']
                        imo['id'] = f"{site['nome'].split('.')[0]}_{len(todos_imoveis)}"
                        imo['data_extracao'] = datetime.now().isoformat()
                        todos_imoveis.append(imo)
            
            print(f"✅ {site['nome']}: {len(item.get('imoveis', []))} imóveis")
        else:
            print(f"⚠️ {site['nome']}: Nenhum dado retornado")
    
    # Guardar resultados
    if todos_imoveis:
        resultado = {
            "data_scraping": datetime.now().isoformat(),
            "sites_testados": len(sites_teste),
            "total_imoveis": len(todos_imoveis),
            "imoveis": todos_imoveis
        }
        
        with open("dados_apify_teste.json", 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 70)
        print("📊 RESULTADO DO TESTE")
        print("=" * 70)
        print(f"Total: {len(todos_imoveis)} imóveis extraídos")
        print(f"Ficheiro: dados_apify_teste.json")
        
        print("\n🏠 Exemplos:")
        for i, imo in enumerate(todos_imoveis[:5], 1):
            print(f"{i}. [{imo['fonte']}] {imo['titulo'][:70]}")
            if imo.get('preco'):
                print(f"   Preço: €{imo['preco']:,.0f}")
    else:
        print("\n❌ Nenhum imóvel extraído")
        print("Possíveis causas:")
        print("  • Créditos gratuitos esgotados")
        print("  • Sites com proteção avançada")
        print("  • Necessário plano pago")

if __name__ == "__main__":
    main()
