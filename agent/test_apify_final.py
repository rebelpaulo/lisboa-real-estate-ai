import requests
import json
import time

APIFY_TOKEN = os.getenv('APIFY_TOKEN', 'seu_token_aqui')

def test_apify():
    """Testa Apify com Website Content Crawler"""
    
    # Input para o crawler
    run_input = {
        "startUrls": [{"url": "https://www.leilosoc.com/pt/leiloes/?categoria=imoveis"}],
        "maxCrawlPages": 2,
        "crawlerType": "cheerio",
        "proxyConfiguration": {"useApifyProxy": True}
    }
    
    print("🚀 A iniciar Website Content Crawler...")
    
    # Iniciar run
    response = requests.post(
        "https://api.apify.com/v2/acts/apify~website-content-crawler/runs",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"},
        json=run_input
    )
    
    if response.status_code != 201:
        print(f"❌ Erro ao iniciar: {response.status_code}")
        print(response.text[:500])
        return
    
    run_data = response.json()
    run_id = run_data['data']['id']
    dataset_id = run_data['data']['defaultDatasetId']
    
    print(f"✅ Run iniciado: {run_id}")
    print("⏳ A aguardar conclusão (max 60s)...")
    
    # Aguardar conclusão
    for i in range(12):  # 60 segundos max
        time.sleep(5)
        
        status_resp = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
        )
        
        status = status_resp.json()['data']['status']
        print(f"  Status: {status}")
        
        if status == "SUCCEEDED":
            break
        elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            print(f"❌ Run falhou: {status}")
            return
    
    # Obter resultados
    print("📥 A obter resultados...")
    dataset_resp = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
    )
    
    items = dataset_resp.json()
    
    print(f"\n✅ {len(items)} páginas crawleadas")
    
    # Guardar resultados
    with open("apify_resultado.json", 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    
    # Mostrar exemplo
    if items:
        print("\n📄 Exemplo:")
        print(f"  URL: {items[0].get('url')}")
        print(f"  Título: {items[0].get('title', 'N/A')[:80]}")
        print(f"  Texto: {items[0].get('text', 'N/A')[:200]}...")

if __name__ == "__main__":
    test_apify()
