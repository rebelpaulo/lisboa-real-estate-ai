"""
Scraper de Leilões - Lisboa Real Estate AI
Testa sites de leilões de forma segura
"""

import asyncio
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

# Lista de sites de leilões ordenados por "segurança" (menos provável de bloquear)
LEILAO_SITES = {
    # Tier 1: Sites mais estáveis/seguros
    "safe": [
        ("leilosoc.com", "https://www.leilosoc.com/"),
        ("e-leiloes.pt", "https://www.e-leiloes.pt/"),
        ("vendajudicial.pt", "https://vendajudicial.pt/"),
        ("vendasjudiciais.pt", "https://vendasjudiciais.pt/"),
    ],
    # Tier 2: Sites médios
    "medium": [
        ("avaliberica.pt", "https://www.avaliberica.pt/"),
        ("lcpremium.pt", "https://www.lcpremium.pt/"),
        ("bidleiloeira.pt", "https://www.bidleiloeira.pt/"),
        ("exclusivagora.com", "https://www.exclusivagora.com/"),
        ("capital-leiloeira.pt", "https://www.capital-leiloeira.pt/"),
    ],
    # Tier 3: Sites mais agressivos/protegidos
    "aggressive": [
        ("leiloseabra.com", "http://www.leiloseabra.com/"),
        ("leiloeiradolena.com", "https://www.leiloeiradolena.com/"),
        ("onefix-leiloeiros.pt", "https://www.onefix-leiloeiros.pt/"),
        ("available-equation.pt", "https://www.available-equation.pt/"),
        ("aleiloeira.pt", "http://www.aleiloeira.pt/todos_leiloes.php"),
        ("leiloport.pt", "https://leiloport.pt/"),
        ("domuslegis.pt", "https://www.domuslegis.pt/"),
        ("justavenda.pt", "https://www.justavenda.pt/"),
        ("cparaiso.pt", "https://www.cparaiso.pt/"),
        ("maximovalor.pt", "https://www.maximovalor.pt/"),
        ("aijm.pt", "http://www.aijm.pt/bens.aspx"),
        ("imoloriente.pt", "https://imoloriente.pt/"),
        ("leilovalor.com", "https://www.leilovalor.com/index.php"),
        ("viaserumos.pt", "https://www.viaserumos.pt/pt/home"),
        ("e-negocios.pt", "https://www.e-negocios.pt/"),
        ("pesquisabenspenhorados.com", "https://www.pesquisabenspenhorados.com/leiloes-venda-judicial/"),
        ("leiloatrium.pt", "https://leiloatrium.pt/"),
        ("vleiloes.com", "https://www.vleiloes.com/"),
        ("leilostar.pt", "https://www.leilostar.pt/"),
        ("lexleiloes.com", "https://lexleiloes.com/vendas-em-curso/vendas-judiciais/"),
        ("marceloferreirasolicitador.pt", "https://marceloferreirasolicitador.pt/vendas-judiciais/"),
        ("esoauction.pt", "https://www.esoauction.pt/"),
        ("yourstone.pt", "http://www.yourstone.pt/"),
        ("lusoprocessos.com", "http://www.lusoprocessos.com/index.php"),
        ("leilowin.pt", "https://www.leilowin.pt/"),
        ("vamgo.pt", "https://www.vamgo.pt/"),
        ("a7s.pt", "https://a7s.pt/"),
        ("bidmarket.pt", "https://www.bidmarket.pt/#/"),
        ("leiloesimobiliarios.pt", "https://www.leiloesimobiliarios.pt/Imobiliario.aspx"),
        ("inlexleiloeira.pt", "https://www.inlexleiloeira.pt/"),
        ("leilobusiness.com", "http://www.leilobusiness.com/index.php?page=bem_listar"),
        ("leiloexpert.pt", "https://www.leiloexpert.pt/?chkimoveis=I&q="),
    ]
}

@dataclass
class LeilaoProperty:
    """Imóvel em leilão"""
    id: str
    titulo: str
    localizacao: str
    descricao: str
    preco_base: float
    preco_avaliacao: Optional[float]
    data_leilao: Optional[datetime]
    tipo: str
    area: Optional[float]
    url: str
    fonte: str
    imagens: List[str]
    estado: str  # "aberto", "fechado", "adiado"
    
class LeilaoScraper:
    """Scraper para sites de leilões"""
    
    def __init__(self):
        self.results: List[LeilaoProperty] = []
        self.failed_sites: List[str] = []
        self.success_sites: List[str] = []
        
    async def test_site_simple(self, name: str, url: str) -> bool:
        """Testa um site de forma simples (apenas verifica se responde)"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }) as response:
                    if response.status == 200:
                        logger.info(f"✅ {name}: OK (Status {response.status})")
                        self.success_sites.append(name)
                        return True
                    else:
                        logger.warning(f"⚠️ {name}: Status {response.status}")
                        self.failed_sites.append(f"{name} (Status {response.status})")
                        return False
        except Exception as e:
            logger.error(f"❌ {name}: {str(e)}")
            self.failed_sites.append(f"{name} ({str(e)[:50]})")
            return False
    
    async def scrape_leilosoc(self) -> List[LeilaoProperty]:
        """Scraper específico para leilosoc.com"""
        properties = []
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            
            async with aiohttp.ClientSession() as session:
                # URL de leilões imobiliários
                url = "https://www.leilosoc.com/pt/leiloes/?categoria=imoveis"
                
                async with session.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }) as response:
                    if response.status != 200:
                        return properties
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Procurar cards de imóveis (estrutura típica)
                    cards = soup.find_all('div', class_=re.compile('property|imovel|leilao', re.I))
                    
                    for card in cards[:10]:  # Limitar a 10 para teste
                        try:
                            # Extrair dados básicos
                            titulo = card.find(['h2', 'h3', 'h4', 'a'])
                            titulo = titulo.get_text(strip=True) if titulo else "Sem título"
                            
                            preco_elem = card.find(text=re.compile(r'\d+[\.\d]*\s*€'))
                            preco = 0
                            if preco_elem:
                                match = re.search(r'(\d+[\.\d]*)\s*€', preco_elem)
                                if match:
                                    preco = float(match.group(1).replace('.', ''))
                            
                            link_elem = card.find('a', href=True)
                            link = link_elem['href'] if link_elem else ""
                            if link and not link.startswith('http'):
                                link = f"https://www.leilosoc.com{link}"
                            
                            prop = LeilaoProperty(
                                id=f"leilosoc_{len(properties)}",
                                titulo=titulo,
                                localizacao="Lisboa",
                                descricao="",
                                preco_base=preco,
                                preco_avaliacao=None,
                                data_leilao=None,
                                tipo="Apartamento",
                                area=None,
                                url=link,
                                fonte="leilosoc.com",
                                imagens=[],
                                estado="aberto"
                            )
                            properties.append(prop)
                            
                        except Exception as e:
                            logger.warning(f"Erro ao extrair card: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Erro no scraper leilosoc: {e}")
        
        return properties
    
    async def run_safe_tests(self):
        """Executa testes nos sites mais seguros"""
        logger.info("🧪 Iniciando testes em sites seguros (Tier 1)...")
        
        tasks = []
        for name, url in LEILAO_SITES["safe"]:
            tasks.append(self.test_site_simple(name, url))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"\n✅ Sites OK: {len(self.success_sites)}")
        logger.info(f"❌ Sites falhados: {len(self.failed_sites)}")
        
        return {
            "success": self.success_sites,
            "failed": self.failed_sites
        }
    
    async def scrape_all_safe(self) -> List[LeilaoProperty]:
        """Tenta fazer scraping nos sites que funcionaram"""
        all_properties = []
        
        # Primeiro testar quais funcionam
        await self.run_safe_tests()
        
        # Tentar scraping nos que funcionaram
        if "leilosoc.com" in self.success_sites:
            props = await self.scrape_leilosoc()
            all_properties.extend(props)
            logger.info(f"📊 leilosoc.com: {len(props)} imóveis encontrados")
        
        return all_properties
    
    def save_results(self, filename: str = "leiloes_resultados.json"):
        """Guarda resultados em JSON"""
        data = {
            "data_scraping": datetime.now().isoformat(),
            "sites_testados": len(LEILAO_SITES["safe"]) + len(LEILAO_SITES["medium"]) + len(LEILAO_SITES["aggressive"]),
            "sites_ok": len(self.success_sites),
            "sites_falhados": self.failed_sites,
            "imoveis_encontrados": len(self.results),
            "imoveis": [
                {
                    "id": p.id,
                    "titulo": p.titulo,
                    "localizacao": p.localizacao,
                    "preco_base": p.preco_base,
                    "preco_avaliacao": p.preco_avaliacao,
                    "tipo": p.tipo,
                    "area": p.area,
                    "url": p.url,
                    "fonte": p.fonte,
                    "estado": p.estado
                }
                for p in self.results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"💾 Resultados guardados em {filename}")

# Instância global
scraper = LeilaoScraper()

async def main():
    """Função principal para testes"""
    print("🚀 Iniciando testes de scraping de leilões...")
    print("=" * 60)
    
    # Testar sites seguros
    results = await scraper.run_safe_tests()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO:")
    print(f"✅ Sites que responderam: {len(results['success'])}")
    print(f"❌ Sites falhados: {len(results['failed'])}")
    
    if results['success']:
        print("\n✅ Sites OK:")
        for site in results['success']:
            print(f"  • {site}")
    
    if results['failed']:
        print("\n❌ Sites falhados:")
        for site in results['failed']:
            print(f"  • {site}")
    
    # Tentar scraping nos que funcionaram
    print("\n🔍 Tentando extrair dados dos sites OK...")
    properties = await scraper.scrape_all_safe()
    
    print(f"\n📊 Total de imóveis encontrados: {len(properties)}")
    
    if properties:
        print("\n🏠 Exemplos:")
        for p in properties[:3]:
            print(f"  • {p.titulo[:60]}... - €{p.preco_base:,.0f}")
    
    scraper.results = properties
    scraper.save_results()
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
