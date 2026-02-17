#!/usr/bin/env python3
"""
Lisboa Real Estate AI - Script Principal
Integração completa: scraping + análise + GitHub sync
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Adicionar diretório do agente ao path
sys.path.insert(0, str(Path(__file__).parent))

from bot import RealEstateBot, Property
from analyzer import MarketAnalyzer
from database import PropertyDatabase
from github_bridge import GitHubBridge, LocalDataStore

# Scrapers (com fallback)
try:
    from scrapers_v2 import MultiPortalScraper, ScrapedProperty
except ImportError:
    from scrapers import MultiPortalScraper, ScrapedProperty

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LisboaRealEstateAI:
    """Sistema completo de análise imobiliária"""
    
    def __init__(self):
        self.bot = RealEstateBot()
        self.analyzer = MarketAnalyzer()
        self.db = PropertyDatabase()
        self.github = GitHubBridge()
        self.local_store = LocalDataStore()
        self.scraper = MultiPortalScraper()
    
    async def scrape_and_analyze(self, 
                                  location: str = "lisboa",
                                  typology: str = "",
                                  max_pages: int = 3) -> list:
        """
        Executa scraping e análise completa
        
        Returns:
            Lista de propriedades analisadas
        """
        logger.info(f"Iniciando busca em {location}...")
        
        # 1. Scraping
        raw_results = await self.scraper.search_all(
            location=location,
            typology=typology,
            max_pages=max_pages
        )
        
        # 2. Deduplicar
        unique_properties = self.scraper.deduplicate(raw_results)
        logger.info(f"{len(unique_properties)} imóveis únicos encontrados")
        
        # 3. Converter para formato interno
        analyzed_properties = []
        
        for scraped in unique_properties:
            # Converter ScrapedProperty -> Property
            prop = Property(
                id=scraped.id,
                portal=scraped.portal,
                url=scraped.url,
                title=scraped.title,
                price=scraped.price,
                price_history=[],
                area_m2=scraped.area_m2,
                typology=scraped.typology,
                location=scraped.location,
                parish=scraped.parish,
                municipality=scraped.municipality,
                description=scraped.description,
                features=scraped.features,
                photos=scraped.photos,
                days_on_market=scraped.created_at and 
                    (datetime.now() - scraped.created_at).days or 0
            )
            
            # 4. Calcular score de oportunidade
            # Buscar dados de mercado da zona
            market_data = self.db.get_market_data(scraped.parish, scraped.typology) or {}
            
            metrics = self.bot.calculate_opportunity_score(prop, market_data)
            prop.opportunity_score = metrics.score
            prop.opportunity_category = metrics.category
            
            analyzed_properties.append(prop)
            
            # 5. Guardar na base de dados
            self.db.save_property({
                'id': prop.id,
                'portal': prop.portal,
                'url': prop.url,
                'title': prop.title,
                'price': prop.price,
                'area_m2': prop.area_m2,
                'typology': prop.typology,
                'location': prop.location,
                'parish': prop.parish,
                'municipality': prop.municipality,
                'opportunity_score': prop.opportunity_score,
                'opportunity_category': prop.opportunity_category,
                'days_on_market': prop.days_on_market,
            })
        
        # Ordenar por score
        analyzed_properties.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return analyzed_properties
    
    def filter_opportunities(self, 
                            properties: list,
                            min_score: int = 40,
                            category: str = None,
                            min_days: int = None) -> list:
        """Filtra oportunidades segundo critérios"""
        return self.bot.filter_opportunities(
            properties, 
            min_score=min_score,
            category=category,
            min_days=min_days
        )
    
    def generate_report(self, properties: list, output_file: str = None) -> str:
        """Gera relatório de oportunidades"""
        report = self.bot.generate_report(properties)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Relatório guardado em {output_file}")
        
        return report
    
    def sync_to_dashboard(self, properties: list) -> dict:
        """Sincroniza dados com dashboard"""
        # Converter para dict
        props_data = []
        for prop in properties:
            props_data.append({
                'id': prop.id,
                'portal': prop.portal,
                'url': prop.url,
                'title': prop.title,
                'price': prop.price,
                'pricePerM2': prop.price_per_m2,
                'areaM2': prop.area_m2,
                'typology': prop.typology,
                'location': prop.location,
                'parish': prop.parish,
                'municipality': prop.municipality,
                'daysOnMarket': prop.days_on_market,
                'opportunityScore': prop.opportunity_score,
                'opportunityCategory': prop.opportunity_category,
                'photos': prop.photos,
            })
        
        # Estatísticas
        stats = {
            'totalProperties': len(properties),
            'averageScore': sum(p.opportunity_score for p in properties) / len(properties) if properties else 0,
            'averageDays': sum(p.days_on_market for p in properties) / len(properties) if properties else 0,
            'averagePrice': sum(p.price for p in properties) / len(properties) if properties else 0,
            'byCategory': {},
        }
        
        for cat in ['A', 'B', 'C', 'D']:
            stats['byCategory'][cat] = len([p for p in properties if p.opportunity_category == cat])
        
        # Guardar localmente
        self.local_store.save('properties_latest', {
            'properties': props_data,
            'updatedAt': datetime.now().isoformat()
        })
        self.local_store.save('stats', stats)
        
        # Tentar sync com GitHub
        if self.github.token:
            results = self.github.sync_dashboard_data(props_data, stats)
            return results
        
        return {'local': True}
    
    def get_stats(self) -> dict:
        """Obtém estatísticas da base de dados"""
        return self.db.get_stats()
    
    def close(self):
        """Fecha recursos"""
        self.db.close()


async def main():
    """Função principal CLI"""
    parser = argparse.ArgumentParser(
        description='Lisboa Real Estate AI - Análise de Oportunidades Imobiliárias'
    )
    
    parser.add_argument('--search', '-s', 
                       help='Localização para busca (ex: lisboa, cascais)')
    parser.add_argument('--typology', '-t',
                       help='Tipologia (t0, t1, t2, t3, t4, moradia)')
    parser.add_argument('--max-pages', '-p', type=int, default=3,
                       help='Máximo de páginas a scrapear')
    parser.add_argument('--min-score', type=int, default=40,
                       help='Score mínimo de oportunidade')
    parser.add_argument('--category', '-c',
                       help='Filtrar por categoria (A, B, C, D)')
    parser.add_argument('--min-days', type=int,
                       help='Mínimo de dias no mercado')
    parser.add_argument('--report', '-r', action='store_true',
                       help='Gerar relatório')
    parser.add_argument('--output', '-o',
                       help='Ficheiro de saída para relatório')
    parser.add_argument('--sync', action='store_true',
                       help='Sincronizar com dashboard')
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estatísticas')
    parser.add_argument('--daemon', '-d', action='store_true',
                       help='Modo daemon (execução contínua)')
    parser.add_argument('--interval', '-i', type=int, default=3600,
                       help='Intervalo entre execuções (segundos)')
    
    args = parser.parse_args()
    
    # Inicializar sistema
    app = LisboaRealEstateAI()
    
    try:
        if args.stats:
            stats = app.get_stats()
            print(json.dumps(stats, indent=2))
            return
        
        if args.search:
            # Executar scraping e análise
            properties = await app.scrape_and_analyze(
                location=args.search,
                typology=args.typology or "",
                max_pages=args.max_pages
            )
            
            # Filtrar
            filtered = app.filter_opportunities(
                properties,
                min_score=args.min_score,
                category=args.category,
                min_days=args.min_days
            )
            
            print(f"\n{'='*60}")
            print(f"RESULTADOS: {len(filtered)} oportunidades encontradas")
            print(f"{'='*60}\n")
            
            # Mostrar top 10
            for i, prop in enumerate(filtered[:10], 1):
                cat_emoji = {'A': '🔴', 'B': '🟡', 'C': '🟢', 'D': '🔵'}.get(prop.opportunity_category, '⚪')
                print(f"{i}. {cat_emoji} {prop.title}")
                print(f"   💰 €{prop.price:,.0f} | Score: {prop.opportunity_score}/100")
                print(f"   📍 {prop.parish} | {prop.typology} | {prop.area_m2}m²")
                print(f"   🔗 {prop.url}\n")
            
            # Gerar relatório
            if args.report:
                output = args.output or f"report_{datetime.now():%Y%m%d_%H%M%S}.md"
                app.generate_report(filtered, output)
            
            # Sync com dashboard
            if args.sync:
                results = app.sync_to_dashboard(filtered)
                print(f"\nSync: {results}")
        
        elif args.daemon:
            # Modo daemon
            import schedule
            import time
            
            def job():
                logger.info("Executando atualização programada...")
                asyncio.run(app.scrape_and_analyze())
            
            schedule.every(args.interval).seconds.do(job)
            
            logger.info(f"Daemon iniciado (intervalo: {args.interval}s)")
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        else:
            parser.print_help()
    
    finally:
        app.close()


if __name__ == "__main__":
    asyncio.run(main())
