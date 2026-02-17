"""
Scrapers Avançados - Lisboa Real Estate AI
Com suporte a anti-detecção e rotação de proxies
"""

import asyncio
import logging
import json
import random
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, quote
import re
import time

try:
    import aiohttp
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright, Page, Browser
    from playwright_stealth import stealth_async
except ImportError:
    pass

logger = logging.getLogger(__name__)

# User agents rotativos
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]

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


class StealthScraper:
    """Scraper com técnicas de anti-detecção"""
    
    def __init__(self, delay_ms: int = 2000, use_proxy: bool = False):
        self.delay_ms = delay_ms
        self.use_proxy = use_proxy
        self.browser: Optional[Browser] = None
        self.context = None
    
    async def init_browser(self):
        """Inicializa browser com stealth mode"""
        playwright = await async_playwright().start()
        
        browser_args = ['--disable-blink-features=AutomationControlled']
        if self.use_proxy:
            # Adicionar proxy se configurado
            pass
        
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=browser_args
        )
        
        # Contexto com viewport e user agent realistas
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(USER_AGENTS),
            locale='pt-PT',
            timezone_id='Europe/Lisbon',
        )
        
        # Adicionar scripts de stealth
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        return self
    
    async def close(self):
        """Fecha o browser"""
        if self.browser:
            await self.browser.close()
    
    async def fetch_page(self, url: str) -> Optional[Page]:
        """Carrega página com delays e comportamento humano"""
        if not self.context:
            await self.init_browser()
        
        page = await self.context.new_page()
        
        try:
            # Delay aleatório antes de carregar
            await asyncio.sleep(random.uniform(1, 3))
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Simular comportamento humano
            await self._human_behavior(page)
            
            return page
            
        except Exception as e:
            logger.error(f"Erro ao carregar {url}: {e}")
            await page.close()
            return None
    
    async def _human_behavior(self, page: Page):
        """Simula comportamento humano na página"""
        # Scroll aleatório
        for _ in range(random.randint(2, 5)):
            await page.mouse.wheel(0, random.randint(300, 700))
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Movimento do mouse aleatório
        for _ in range(random.randint(3, 7)):
            await page.mouse.move(
                random.randint(100, 1800),
                random.randint(100, 900)
            )
            await asyncio.sleep(random.uniform(0.2, 0.8))


class IdealistaScraper:
    """Scraper para Idealista.pt"""
    
    BASE_URL = "https://www.idealista.pt"
    
    def __init__(self, stealth: Optional[StealthScraper] = None):
        self.stealth = stealth or StealthScraper()
    
    async def search(self, 
                     location: str = "lisboa",
                     typology: str = "",
                     min_price: Optional[int] = None,
                     max_price: Optional[int] = None,
                     max_pages: int = 3) -> List[ScrapedProperty]:
        """
        Busca imóveis no Idealista
        """
        properties = []
        
        # Construir URL de busca
        search_paths = {
            "": "apartamentos",
            "t0": "estudios",
            "t1": "t1",
            "t2": "t2",
            "t3": "t3",
            "t4": "t4",
            "t5": "t5",
            "moradia": "moradias",
        }
        
        tipo_path = search_paths.get(typology.lower(), "apartamentos")
        search_url = f"{self.BASE_URL}/{location}/{tipo_path}/"
        
        # Adicionar parâmetros de preço
        params = []
        if min_price:
            params.append(f"preco-desde_{min_price}")
        if max_price:
            params.append(f"preco-ate_{max_price}")
        
        if params:
            search_url += "?" + "&".join(params)
        
        logger.info(f"Buscando no Idealista: {search_url}")
        
        await self.stealth.init_browser()
        
        try:
            for page_num in range(1, max_pages + 1):
                page_url = f"{search_url}?pagina={page_num}" if page_num > 1 else search_url
                
                page = await self.stealth.fetch_page(page_url)
                if not page:
                    break
                
                # Extrair imóveis da página
                items = await self._extract_properties(page)
                properties.extend(items)
                
                logger.info(f"Página {page_num}: {len(items)} imóveis")
                
                # Verificar se há próxima página
                has_next = await page.query_selector('a.icon-arrow-right-after')
                await page.close()
                
                if not has_next or len(items) == 0:
                    break
                
                await asyncio.sleep(random.uniform(3, 6))
                
        finally:
            await self.stealth.close()
        
        return properties
    
    async def _extract_properties(self, page) -> List[ScrapedProperty]:
        """Extrai lista de imóveis da página"""
        properties = []
        
        # Seletores atualizados (podem mudar)
        selectors = {
            'items': 'article.item',
            'title': '.item-link',
            'price': '.item-price',
            'details': '.item-detail-char',
            'location': '.item-detail-char .ellipsis',
            'description': '.item-description',
        }
        
        items = await page.query_selector_all(selectors['items'])
        
        for item in items:
            try:
                prop = await self._parse_item(item, selectors)
                if prop and prop.price > 0:
                    properties.append(prop)
            except Exception as e:
                logger.error(f"Erro ao parsear item: {e}")
        
        return properties
    
    async def _parse_item(self, item, selectors) -> Optional[ScrapedProperty]:
        """Parse de um item de imóvel"""
        try:
            # Título e URL
            title_elem = await item.query_selector(selectors['title'])
            title = await title_elem.inner_text() if title_elem else ""
            href = await title_elem.get_attribute('href') if title_elem else ""
            url = urljoin(self.BASE_URL, href)
            
            # Extrair ID do URL
            prop_id = re.search(r'/\d+/', url)
            prop_id = prop_id.group(0).strip('/') if prop_id else str(hash(url))
            
            # Preço
            price_elem = await item.query_selector(selectors['price'])
            price_text = await price_elem.inner_text() if price_elem else ""
            price = self._extract_price(price_text)
            
            # Detalhes (área, tipologia)
            details_elem = await item.query_selector(selectors['details'])
            details = await details_elem.inner_text() if details_elem else ""
            area = self._extract_area(details)
            typology = self._extract_typology(details)
            
            # Localização
            loc_elem = await item.query_selector(selectors['location'])
            location = await loc_elem.inner_text() if loc_elem else ""
            parish, municipality = self._parse_location(location)
            
            return ScrapedProperty(
                id=f"idealista_{prop_id}",
                portal="idealista",
                url=url,
                title=title.strip(),
                price=price or 0,
                area_m2=area,
                typology=typology,
                location=location.strip(),
                parish=parish,
                municipality=municipality
            )
            
        except Exception as e:
            logger.error(f"Erro no parse: {e}")
            return None
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extrai valor numérico de preço"""
        if not text:
            return None
        cleaned = re.sub(r'[^\d,\.]', '', text.replace(' ', ''))
        try:
            return float(cleaned.replace(',', '.'))
        except ValueError:
            return None
    
    def _extract_area(self, text: str) -> Optional[float]:
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
    
    def _extract_typology(self, text: str) -> str:
        """Extrai tipologia do texto"""
        patterns = [
            (r'\b(T\d+)\b', lambda m: m.group(1).upper()),
            (r'\bestudio\b', 'T0'),
            (r'\bmoradia\b', 'Moradia'),
        ]
        
        for pattern, extractor in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return extractor(match)
        
        return ""
    
    def _parse_location(self, location: str) -> tuple:
        """Parse de localização em parish, municipality"""
        parts = location.split(',')
        if len(parts) >= 2:
            return parts[0].strip(), parts[-1].strip()
        return location, "Lisboa"


class MultiPortalScraper:
    """Scraper unificado para múltiplos portais"""
    
    def __init__(self):
        self.stealth = StealthScraper()
    
    async def search_portal(self, portal: str, **kwargs) -> List[ScrapedProperty]:
        """Busca num portal específico"""
        scrapers = {
            'idealista': IdealistaScraper,
        }
        
        ScraperClass = scrapers.get(portal)
        if not ScraperClass:
            logger.error(f"Portal não suportado: {portal}")
            return []
        
        scraper = ScraperClass(stealth=self.stealth)
        return await scraper.search(**kwargs)
    
    async def search_all(self, **kwargs) -> Dict[str, List[ScrapedProperty]]:
        """Busca em todos os portais"""
        portals = ['idealista']  # Adicionar mais quando implementados
        results = {}
        
        for portal in portals:
            try:
                properties = await self.search_portal(portal, **kwargs)
                results[portal] = properties
                logger.info(f"{portal}: {len(properties)} imóveis")
            except Exception as e:
                logger.error(f"Erro em {portal}: {e}")
                results[portal] = []
        
        return results
    
    def deduplicate(self, all_properties: Dict[str, List[ScrapedProperty]]) -> List[ScrapedProperty]:
        """Remove duplicados entre portais"""
        seen = set()
        unique = []
        
        for portal, properties in all_properties.items():
            for prop in properties:
                # Chave de deduplicação
                key = f"{prop.parish}|{prop.price}|{prop.area_m2}|{prop.typology}"
                
                if key not in seen:
                    seen.add(key)
                    unique.append(prop)
        
        return unique


async def main():
    """Teste dos scrapers"""
    logging.basicConfig(level=logging.INFO)
    
    scraper = MultiPortalScraper()
    
    logger.info("Iniciando busca...")
    results = await scraper.search_all(
        location="lisboa",
        typology="t2",
        max_pages=2
    )
    
    total = sum(len(props) for props in results.values())
    logger.info(f"Total: {total} imóveis")
    
    # Deduplicar
    unique = scraper.deduplicate(results)
    logger.info(f"Únicos: {len(unique)}")
    
    # Mostrar primeiros resultados
    for prop in unique[:5]:
        print(f"\n{prop.title}")
        print(f"  Preço: €{prop.price:,.0f}")
        print(f"  {prop.typology} - {prop.area_m2}m²")
        print(f"  {prop.parish}, {prop.municipality}")

if __name__ == "__main__":
    asyncio.run(main())
