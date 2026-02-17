"""
Scrapers - Lisboa Real Estate AI
Coleta de dados dos portais imobiliários
"""

import asyncio
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re

try:
    import aiohttp
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright
except ImportError:
    pass  # Serão instaladas via requirements.txt

logger = logging.getLogger(__name__)

@dataclass
class ScrapedProperty:
    """Modelo de imóvel extraído"""
    id: str
    portal: str
    url: str
    title: str
    price: float
    area_m2: Optional[float]
    typology: str
    location: str
    parish: str
    municipality: str
    description: str = ""
    features: List[str] = None
    photos: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.photos is None:
            self.photos = []
        if self.created_at is None:
            self.created_at = datetime.now()


class BaseScraper:
    """Classe base para scrapers"""
    
    def __init__(self, delay_ms: int = 1000):
        self.delay_ms = delay_ms
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.get_headers()
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_headers(self) -> Dict[str, str]:
        """Headers HTTP para requisições"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    
    async def fetch(self, url: str) -> Optional[str]:
        """Faz requisição HTTP e retorna HTML"""
        try:
            await asyncio.sleep(self.delay_ms / 1000)
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} em {url}")
                    return None
        except Exception as e:
            logger.error(f"Erro ao buscar {url}: {e}")
            return None
    
    def extract_price(self, text: str) -> Optional[float]:
        """Extrai valor numérico de preço"""
        if not text:
            return None
        # Remover símbolos e espaços
        cleaned = re.sub(r'[^\d,\.]', '', text.replace(' ', ''))
        # Converter para float
        try:
            return float(cleaned.replace(',', '.'))
        except ValueError:
            return None
    
    def extract_area(self, text: str) -> Optional[float]:
        """Extrai área em m²"""
        if not text:
            return None
        match = re.search(r'(\d+[\.,]?\d*)\s*m[²2]?', text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', '.'))
            except ValueError:
                return None
        return None


class IdealistaScraper(BaseScraper):
    """Scraper para Idealista.pt"""
    
    BASE_URL = "https://www.idealista.pt"
    
    async def search(self, location: str = "lisboa", 
                     typology: str = "",
                     min_price: Optional[int] = None,
                     max_price: Optional[int] = None) -> List[ScrapedProperty]:
        """
        Busca imóveis no Idealista
        
        Args:
            location: Localização (ex: "lisboa", "cascais")
            typology: Tipologia (ex: "t1", "t2", "moradia")
            min_price: Preço mínimo
            max_price: Preço máximo
        """
        properties = []
        
        # Construir URL de busca
        search_url = f"{self.BASE_URL}/{location}/"
        if typology:
            search_url += f"{typology}-"
        
        logger.info(f"Buscando no Idealista: {search_url}")
        
        # Usar Playwright para JavaScript-rendered content
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(search_url, wait_until='networkidle')
                await asyncio.sleep(2)  # Esperar carregamento
                
                # Extrair dados dos imóveis
                items = await page.query_selector_all('article.item')
                
                for item in items[:20]:  # Limitar a 20 resultados
                    try:
                        prop = await self._parse_item(item)
                        if prop:
                            properties.append(prop)
                    except Exception as e:
                        logger.error(f"Erro ao parsear item: {e}")
                
            except Exception as e:
                logger.error(f"Erro na busca Idealista: {e}")
            finally:
                await browser.close()
        
        return properties
    
    async def _parse_item(self, item) -> Optional[ScrapedProperty]:
        """Parse de um item de imóvel"""
        try:
            # Título
            title_elem = await item.query_selector('.item-link')
            title = await title_elem.inner_text() if title_elem else ""
            href = await title_elem.get_attribute('href') if title_elem else ""
            url = urljoin(self.BASE_URL, href)
            
            # Preço
            price_elem = await item.query_selector('.item-price')
            price_text = await price_elem.inner_text() if price_elem else ""
            price = self.extract_price(price_text)
            
            # Área e tipologia
            details_elem = await item.query_selector('.item-detail-char')
            details = await details_elem.inner_text() if details_elem else ""
            area = self.extract_area(details)
            
            # Extrair tipologia
            typology = ""
            typ_match = re.search(r'(T\d+|Moradia|Apartamento)', details, re.IGNORECASE)
            if typ_match:
                typology = typ_match.group(1).upper()
            
            # Localização
            loc_elem = await item.query_selector('.item-detail-char .ellipsis')
            location = await loc_elem.inner_text() if loc_elem else ""
            
            # ID único
            prop_id = re.search(r'/\d+/', url)
            prop_id = prop_id.group(0).strip('/') if prop_id else str(hash(url))
            
            return ScrapedProperty(
                id=f"idealista_{prop_id}",
                portal="idealista",
                url=url,
                title=title.strip(),
                price=price or 0,
                area_m2=area,
                typology=typology,
                location=location.strip(),
                parish=location.strip(),
                municipality="Lisboa"
            )
            
        except Exception as e:
            logger.error(f"Erro no parse: {e}")
            return None


class ImovirtualScraper(BaseScraper):
    """Scraper para Imovirtual.pt"""
    
    BASE_URL = "https://www.imovirtual.pt"
    
    async def search(self, location: str = "lisboa",
                     typology: str = "") -> List[ScrapedProperty]:
        """Busca imóveis no Imovirtual"""
        properties = []
        
        # URL de busca simplificada
        search_url = f"{self.BASE_URL}/comprar/apartamento/{location}"
        
        logger.info(f"Buscando no Imovirtual: {search_url}")
        
        # Implementação similar ao Idealista
        # (simplificado para estrutura inicial)
        
        return properties


class CasaSapoScraper(BaseScraper):
    """Scraper para CasaSapo.pt"""
    
    BASE_URL = "https://casa.sapo.pt"
    
    async def search(self, location: str = "lisboa") -> List[ScrapedProperty]:
        """Busca imóveis no Casa Sapo"""
        properties = []
        
        search_url = f"{self.BASE_URL}/comprar-apartamentos/{location}"
        logger.info(f"Buscando no Casa Sapo: {search_url}")
        
        return properties


class SupercasaScraper(BaseScraper):
    """Scraper para Supercasa.pt"""
    
    BASE_URL = "https://www.supercasa.pt"
    
    async def search(self, location: str = "lisboa") -> List[ScrapedProperty]:
        """Busca imóveis no Supercasa"""
        properties = []
        
        search_url = f"{self.BASE_URL}/comprar-casas/apartamentos/{location}"
        logger.info(f"Buscando no Supercasa: {search_url}")
        
        return properties


class MultiPortalScraper:
    """Scraper unificado para múltiplos portais"""
    
    def __init__(self):
        self.scrapers = {
            'idealista': IdealistaScraper,
            'imovirtual': ImovirtualScraper,
            'casasapo': CasaSapoScraper,
            'supercasa': SupercasaScraper,
        }
    
    async def search_all(self, location: str = "lisboa",
                         typology: str = "") -> Dict[str, List[ScrapedProperty]]:
        """
        Busca em todos os portais disponíveis
        
        Returns:
            Dict com resultados por portal
        """
        results = {}
        
        for name, ScraperClass in self.scrapers.items():
            try:
                async with ScraperClass() as scraper:
                    properties = await scraper.search(location, typology)
                    results[name] = properties
                    logger.info(f"{name}: {len(properties)} imóveis encontrados")
            except Exception as e:
                logger.error(f"Erro no scraper {name}: {e}")
                results[name] = []
        
        return results
    
    def deduplicate(self, all_properties: Dict[str, List[ScrapedProperty]]) -> List[ScrapedProperty]:
        """
        Remove duplicados entre portais baseado em características similares
        """
        seen = set()
        unique = []
        
        for portal, properties in all_properties.items():
            for prop in properties:
                # Chave de deduplicação: localização + preço + área
                key = f"{prop.location}|{prop.price}|{prop.area_m2}"
                
                if key not in seen:
                    seen.add(key)
                    unique.append(prop)
        
        return unique


async def main():
    """Teste dos scrapers"""
    scraper = MultiPortalScraper()
    
    logger.info("Iniciando busca em múltiplos portais...")
    results = await scraper.search_all(location="lisboa", typology="t2")
    
    total = sum(len(props) for props in results.values())
    logger.info(f"Total de imóveis encontrados: {total}")
    
    # Deduplicar
    unique = scraper.deduplicate(results)
    logger.info(f"Imóveis únicos: {len(unique)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
