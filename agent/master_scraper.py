"""
Scraper Master - Lisboa Real Estate AI
Testa 9 sites de leilões com Apify e técnicas avançadas
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LeilaoImovel:
    """Imóvel em leilão"""
    id: str
    titulo: str
    localizacao: str
    concelho: str
    freguesia: str
    descricao: str
    tipo: str  # Apartamento, Moradia, Loja, Terreno, etc.
    area_m2: Optional[float]
    preco_base: float
    preco_avaliacao: Optional[float]
    data_leilao: Optional[str]
    estado: str  # Aberto, Fechado, Adiado
    url: str
    fonte: str
    imagens: List[str]
    contacto: Optional[str] = None
    notas: str = ""

# Tier 1 + Tier 2 (9 sites)
SITES_TESTE = [
    # Tier 1 - Mais seguros
    {"nome": "leilosoc.com", "url": "https://www.leilosoc.com/", "tipo": "profissional", "prioridade": 1},
    {"nome": "e-leiloes.pt", "url": "https://www.e-leiloes.pt/", "tipo": "plataforma", "prioridade": 1},
    {"nome": "vendajudicial.pt", "url": "https://vendajudicial.pt/", "tipo": "especializado", "prioridade": 1},
    {"nome": "vendasjudiciais.pt", "url": "https://vendasjudiciais.pt/", "tipo": "especializado", "prioridade": 1},
    # Tier 2 - Médios
    {"nome": "avaliberica.pt", "url": "https://www.avaliberica.pt/", "tipo": "leiloeira", "prioridade": 2},
    {"nome": "lcpremium.pt", "url": "https://www.lcpremium.pt/", "tipo": "leiloeira", "prioridade": 2},
    {"nome": "bidleiloeira.pt", "url": "https://www.bidleiloeira.pt/", "tipo": "leiloeira", "prioridade": 2},
    {"nome": "exclusivagora.com", "url": "https://www.exclusivagora.com/", "tipo": "plataforma", "prioridade": 2},
    {"nome": "capital-leiloeira.pt", "url": "https://www.capital-leiloeira.pt/", "tipo": "leiloeira", "prioridade": 2},
]

class MasterScraper:
    """Scraper master para sites de leilões"""
    
    def __init__(self):
        self.resultados: List[LeilaoImovel] = []
        self.sites_ok: List[Dict] = []
        self.sites_falhados: List[Dict] = []
        self.imoveis_por_site: Dict[str, List[LeilaoImovel]] = {}
        
    async def testar_site_simples(self, site: Dict) -> bool:
        """Testa se site responde (método mais seguro)"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    site["url"], 
                    timeout=15,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ {site['nome']}: OK (Status {response.status})")
                        return True
                    else:
                        logger.warning(f"⚠️ {site['nome']}: Status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ {site['nome']}: {str(e)[:60]}")
            return False
    
    async def scrape_com_apify(self, site: Dict) -> List[LeilaoImovel]:
        """Usa Apify para fazer scraping (método avançado)"""
        imoveis = []
        
        try:
            # Tentar usar Apify se disponível
            from apify_client import ApifyClient
            
            client = ApifyClient()
            
            # Configurar actor de web scraping
            run_input = {
                "startUrls": [{"url": site["url"]}],
                "maxPages": 5,
                "maxRequests": 50,
                "waitFor": "body",
                "viewport": {"width": 1920, "height": 1080}
            }
            
            # Usar actor de scraping genérico
            run = client.actor("apify/web-scraper").call(run_input=run_input)
            
            # Extrair resultados
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                # Processar dados extraídos
                imovel = self._extrair_imovel_de_dados(item, site["nome"])
                if imovel:
                    imoveis.append(imovel)
                    
        except ImportError:
            logger.warning(f"Apify não disponível para {site['nome']}, usando método alternativo")
            return await self.scrape_com_playwright(site)
        except Exception as e:
            logger.error(f"Erro Apify em {site['nome']}: {e}")
            return await self.scrape_com_playwright(site)
        
        return imoveis
    
    async def scrape_com_playwright(self, site: Dict) -> List[LeilaoImovel]:
        """Usa Playwright para scraping (método intermédio)"""
        imoveis = []
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navegar para o site
                await page.goto(site["url"], timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # Extrair dados (lógica específica por site)
                if "leilosoc" in site["nome"]:
                    imoveis = await self._scrape_leilosoc(page, site)
                elif "e-leiloes" in site["nome"]:
                    imoveis = await self._scrape_eleiloes(page, site)
                else:
                    # Método genérico
                    imoveis = await self._scrape_generico(page, site)
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"Erro Playwright em {site['nome']}: {e}")
        
        return imoveis
    
    async def _scrape_leilosoc(self, page, site: Dict) -> List[LeilaoImovel]:
        """Scraper específico para leilosoc.com"""
        imoveis = []
        
        try:
            # Procurar link para leilões imobiliários
            links = await page.query_selector_all('a[href*="imovel"], a[href*="imoveis"], a[href*="leilao"]')
            
            for link in links[:5]:  # Limitar a 5 para teste
                try:
                    href = await link.get_attribute('href')
                    if href:
                        # Extrair informações básicas
                        texto = await link.inner_text()
                        
                        imovel = LeilaoImovel(
                            id=f"leilosoc_{len(imoveis)}",
                            titulo=texto[:100] if texto else "Imóvel em Leilão",
                            localizacao="Lisboa",
                            concelho="Lisboa",
                            freguesia="",
                            descricao="",
                            tipo="Apartamento",
                            area_m2=None,
                            preco_base=0,
                            preco_avaliacao=None,
                            data_leilao=None,
                            estado="Aberto",
                            url=href if href.startswith('http') else f"https://www.leilosoc.com{href}",
                            fonte="leilosoc.com",
                            imagens=[],
                            notas="Extraído via Playwright"
                        )
                        imoveis.append(imovel)
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Erro específico leilosoc: {e}")
        
        return imoveis
    
    async def _scrape_eleiloes(self, page, site: Dict) -> List[LeilaoImovel]:
        """Scraper específico para e-leiloes.pt"""
        imoveis = []
        # Implementação similar ao leilosoc
        return imoveis
    
    async def _scrape_generico(self, page, site: Dict) -> List[LeilaoImovel]:
        """Scraper genérico para sites desconhecidos"""
        imoveis = []
        
        try:
            # Procurar por cards de imóveis
            seletores = [
                '.property', '.imovel', '.leilao', '.item',
                '[class*="property"]', '[class*="imovel"]',
                'article', '.card'
            ]
            
            for seletor in seletores:
                elementos = await page.query_selector_all(seletor)
                if elementos:
                    for elem in elementos[:3]:
                        try:
                            texto = await elem.inner_text()
                            if '€' in texto or 'm2' in texto.lower() or 'metro' in texto.lower():
                                imovel = LeilaoImovel(
                                    id=f"{site['nome'].split('.')[0]}_{len(imoveis)}",
                                    titulo=texto[:80] if len(texto) > 20 else "Imóvel em Leilão",
                                    localizacao="Lisboa",
                                    concelho="Lisboa",
                                    freguesia="",
                                    descricao=texto[:200],
                                    tipo="Desconhecido",
                                    area_m2=None,
                                    preco_base=0,
                                    preco_avaliacao=None,
                                    data_leilao=None,
                                    estado="Aberto",
                                    url=site["url"],
                                    fonte=site["nome"],
                                    imagens=[],
                                    notas="Detetado automaticamente"
                                )
                                imoveis.append(imovel)
                        except:
                            continue
                    break  # Parar se encontrou elementos
                    
        except Exception as e:
            logger.error(f"Erro scraper genérico: {e}")
        
        return imoveis
    
    def _extrair_imovel_de_dados(self, dados: Dict, fonte: str) -> Optional[LeilaoImovel]:
        """Extrai objeto LeilaoImovel de dados brutos"""
        try:
            return LeilaoImovel(
                id=f"{fonte}_{dados.get('id', 'unknown')}",
                titulo=dados.get('title', 'Sem título'),
                localizacao=dados.get('location', 'Lisboa'),
                concelho=dados.get('concelho', 'Lisboa'),
                freguesia=dados.get('freguesia', ''),
                descricao=dados.get('description', ''),
                tipo=dados.get('type', 'Apartamento'),
                area_m2=dados.get('area'),
                preco_base=dados.get('price', 0),
                preco_avaliacao=dados.get('appraisal_price'),
                data_leilao=dados.get('auction_date'),
                estado=dados.get('status', 'Aberto'),
                url=dados.get('url', ''),
                fonte=fonte,
                imagens=dados.get('images', [])
            )
        except:
            return None
    
    async def executar_testes(self):
        """Executa testes nos 9 sites"""
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO TESTES NOS 9 SITES DE LEILÕES")
        logger.info("=" * 80)
        
        for i, site in enumerate(SITES_TESTE, 1):
            logger.info(f"\n📌 [{i}/9] Testando {site['nome']}...")
            
            # Teste 1: Verificar se site responde
            responde = await self.testar_site_simples(site)
            
            if not responde:
                self.sites_falhados.append({
                    **site,
                    "motivo": "Não responde ou bloqueado",
                    "imoveis": 0
                })
                continue
            
            # Teste 2: Tentar extrair dados
            try:
                imoveis = await self.scrape_com_apify(site)
                
                if imoveis:
                    self.sites_ok.append({
                        **site,
                        "imoveis": len(imoveis),
                        "metodo": "Apify/Playwright"
                    })
                    self.imoveis_por_site[site["nome"]] = imoveis
                    self.resultados.extend(imoveis)
                    logger.info(f"✅ {site['nome']}: {len(imoveis)} imóveis extraídos")
                else:
                    self.sites_falhados.append({
                        **site,
                        "motivo": "Site responde mas não encontrou imóveis",
                        "imoveis": 0
                    })
                    logger.warning(f"⚠️ {site['nome']}: Nenhum imóvel encontrado")
                    
            except Exception as e:
                self.sites_falhados.append({
                    **site,
                    "motivo": f"Erro: {str(e)[:80]}",
                    "imoveis": 0
                })
                logger.error(f"❌ {site['nome']}: Erro - {e}")
            
            # Delay entre sites para não sobrecarregar
            await asyncio.sleep(2)
        
        # Resumo final
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMO DOS TESTES")
        logger.info("=" * 80)
        logger.info(f"✅ Sites OK: {len(self.sites_ok)}")
        logger.info(f"❌ Sites Falhados: {len(self.sites_falhados)}")
        logger.info(f"🏠 Total de imóveis: {len(self.resultados)}")
        
        return {
            "sites_ok": self.sites_ok,
            "sites_falhados": self.sites_falhados,
            "total_imoveis": len(self.resultados),
            "imoveis": self.resultados
        }
    
    def guardar_resultados(self, filename: str = "resultados_scraping.json"):
        """Guarda resultados em JSON"""
        data = {
            "data_teste": datetime.now().isoformat(),
            "sites_testados": len(SITES_TESTE),
            "sites_ok": len(self.sites_ok),
            "sites_falhados": len(self.sites_falhados),
            "total_imoveis": len(self.resultados),
            "detalhes_sites_ok": self.sites_ok,
            "detalhes_sites_falhados": self.sites_falhados,
            "imoveis": [asdict(i) for i in self.resultados]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"💾 Resultados guardados em {filename}")

async def main():
    """Função principal"""
    scraper = MasterScraper()
    resultados = await scraper.executar_testes()
    scraper.guardar_resultados()
    
    # Mostrar resumo
    print("\n" + "=" * 80)
    print("🎯 RESULTADO FINAL")
    print("=" * 80)
    print(f"\n✅ Sites que funcionaram: {len(resultados['sites_ok'])}")
    for site in resultados['sites_ok']:
        print(f"   • {site['nome']}: {site['imoveis']} imóveis")
    
    print(f"\n❌ Sites que falharam: {len(resultados['sites_falhados'])}")
    for site in resultados['sites_falhados']:
        print(f"   • {site['nome']}: {site['motivo']}")
    
    print(f"\n🏠 Total: {resultados['total_imoveis']} imóveis encontrados")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
