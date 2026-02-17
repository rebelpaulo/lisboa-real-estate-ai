"""
Lisboa Real Estate AI - Bot Principal
Agente de análise de oportunidades imobiliárias
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Property:
    """Modelo de imóvel"""
    id: str
    portal: str
    url: str
    title: str
    price: float
    price_history: List[Dict]
    area_m2: Optional[float]
    typology: str
    location: str
    parish: str
    municipality: str
    district: str = "Lisboa"
    description: str = ""
    features: List[str] = None
    photos: List[str] = None
    contact: Dict = None
    days_on_market: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    
    # Campos calculados
    price_per_m2: Optional[float] = None
    opportunity_score: int = 0
    opportunity_category: str = ""
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.photos is None:
            self.photos = []
        if self.contact is None:
            self.contact = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        # Calcular preço/m²
        if self.area_m2 and self.area_m2 > 0:
            self.price_per_m2 = self.price / self.area_m2

@dataclass
class OpportunityMetrics:
    """Métricas de oportunidade"""
    score: int  # 0-100
    category: str  # A, B, C, D
    reasons: List[str]
    market_avg_price_m2: Optional[float]
    discount_vs_market: Optional[float]
    negotiation_potential: int  # 0-100

class RealEstateBot:
    """Bot principal de análise imobiliária"""
    
    CATEGORIES = {
        'A': {'name': 'Ativo Estagnado', 'emoji': '🔴', 'min_score': 70},
        'B': {'name': 'Preço Agressivo', 'emoji': '🟡', 'min_score': 60},
        'C': {'name': 'Potencial Intervenção', 'emoji': '🟢', 'min_score': 50},
        'D': {'name': 'Oportunidade Fundamentada', 'emoji': '🔵', 'min_score': 40},
    }
    
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "listings.db"
        self.properties: List[Property] = []
        
        logger.info(f"Bot inicializado. DB: {self.db_path}")
    
    def calculate_opportunity_score(self, prop: Property, market_data: Dict) -> OpportunityMetrics:
        """
        Calcula o score de oportunidade de um imóvel
        
        Args:
            prop: Imóvel a analisar
            market_data: Dados de mercado da zona (média de preços, etc.)
        
        Returns:
            OpportunityMetrics com score e categoria
        """
        score = 0
        reasons = []
        
        # 1. Tempo no mercado (0-25 pontos)
        if prop.days_on_market >= 365:
            score += 25
            reasons.append(f"Há mais de 1 ano no mercado ({prop.days_on_market} dias)")
        elif prop.days_on_market >= 180:
            score += 20
            reasons.append(f"Estagnado há {prop.days_on_market} dias")
        elif prop.days_on_market >= 90:
            score += 10
            reasons.append(f"{prop.days_on_market} dias no mercado")
        
        # 2. Reduções de preço (0-25 pontos)
        price_drops = len([h for h in prop.price_history if h.get('change', 0) < 0])
        total_discount = sum(abs(h.get('change', 0)) for h in prop.price_history if h.get('change', 0) < 0)
        
        if price_drops >= 3:
            score += 25
            reasons.append(f"{price_drops} reduções de preço ({total_discount:.1f}% total)")
        elif price_drops >= 2:
            score += 20
            reasons.append(f"{price_drops} reduções ({total_discount:.1f}%)")
        elif price_drops >= 1:
            score += 10
            reasons.append(f"1 redução de preço")
        
        # 3. Comparável com mercado (0-30 pontos)
        market_avg = market_data.get('avg_price_m2')
        discount_vs_market = None
        
        if market_avg and prop.price_per_m2:
            discount_vs_market = (market_avg - prop.price_per_m2) / market_avg * 100
            
            if discount_vs_market >= 20:
                score += 30
                reasons.append(f"{discount_vs_market:.1f}% abaixo da média da zona")
            elif discount_vs_market >= 15:
                score += 25
                reasons.append(f"{discount_vs_market:.1f}% abaixo da média")
            elif discount_vs_market >= 10:
                score += 20
                reasons.append(f"{discount_vs_market:.1f}% abaixo da média")
            elif discount_vs_market >= 5:
                score += 10
                reasons.append(f"{discount_vs_market:.1f}% abaixo da média")
        
        # 4. Potencial de negociação (0-20 pontos)
        negotiation = 0
        if prop.days_on_market >= 180:
            negotiation += 10
        if price_drops >= 2:
            negotiation += 10
        
        score += negotiation
        
        # Determinar categoria
        category = self._determine_category(score, prop, price_drops, total_discount, discount_vs_market)
        
        return OpportunityMetrics(
            score=min(score, 100),
            category=category,
            reasons=reasons,
            market_avg_price_m2=market_avg,
            discount_vs_market=discount_vs_market,
            negotiation_potential=negotiation
        )
    
    def _determine_category(self, score: int, prop: Property, 
                           price_drops: int, total_discount: float,
                           discount_vs_market: Optional[float]) -> str:
        """Determina a categoria de oportunidade"""
        
        # Categoria A: Estagnado com pressão
        if (prop.days_on_market >= 180 and 
            price_drops >= 2 and 
            total_discount >= 10):
            return 'A'
        
        # Categoria B: Recém-entrado com preço agressivo
        if (prop.days_on_market <= 30 and 
            discount_vs_market and 
            discount_vs_market >= 12):
            return 'B'
        
        # Categoria C: Potencial de intervenção (simplificado)
        # Seria necessário análise mais profunda do estado/imóvel
        if score >= 50 and prop.price_per_m2 and prop.price_per_m2 < 2000:
            return 'C'
        
        # Categoria D: Outros casos com score razoável
        if score >= 40:
            return 'D'
        
        return ''
    
    def filter_opportunities(self, properties: List[Property], 
                            min_score: int = 40,
                            category: Optional[str] = None,
                            min_days: Optional[int] = None,
                            max_days: Optional[int] = None) -> List[Property]:
        """
        Filtra oportunidades segundo critérios
        
        Args:
            properties: Lista de imóveis
            min_score: Score mínimo (0-100)
            category: Filtrar por categoria específica (A, B, C, D)
            min_days: Mínimo de dias no mercado
            max_days: Máximo de dias no mercado
        """
        filtered = []
        
        for prop in properties:
            # Filtro por score
            if prop.opportunity_score < min_score:
                continue
            
            # Filtro por categoria
            if category and prop.opportunity_category != category:
                continue
            
            # Filtro por tempo no mercado
            if min_days and prop.days_on_market < min_days:
                continue
            if max_days and prop.days_on_market > max_days:
                continue
            
            filtered.append(prop)
        
        # Ordenar por score decrescente
        filtered.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return filtered
    
    def generate_report(self, properties: List[Property], 
                       title: str = "Relatório de Oportunidades") -> str:
        """Gera relatório em formato markdown"""
        
        report = f"# {title}\n\n"
        report += f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Resumo por categoria
        report += "## Resumo por Categoria\n\n"
        for cat, info in self.CATEGORIES.items():
            count = len([p for p in properties if p.opportunity_category == cat])
            report += f"{info['emoji']} **{cat}** - {info['name']}: {count} imóveis\n"
        
        report += f"\n**Total:** {len(properties)} oportunidades identificadas\n\n"
        
        # Top oportunidades
        report += "## Top Oportunidades\n\n"
        
        for i, prop in enumerate(properties[:20], 1):
            cat_info = self.CATEGORIES.get(prop.opportunity_category, {})
            emoji = cat_info.get('emoji', '⚪')
            
            report += f"### {i}. {emoji} {prop.title}\n\n"
            report += f"- **Preço:** €{prop.price:,.0f}\n"
            if prop.price_per_m2:
                report += f"- **€/m²:** €{prop.price_per_m2:,.0f}\n"
            report += f"- **Localização:** {prop.location}\n"
            report += f"- **Tipologia:** {prop.typology}\n"
            report += f"- **Dias no mercado:** {prop.days_on_market}\n"
            report += f"- **Score:** {prop.opportunity_score}/100\n"
            report += f"- **Categoria:** {prop.opportunity_category}\n"
            report += f"- **Link:** {prop.url}\n\n"
        
        return report
    
    def export_to_json(self, properties: List[Property], filepath: str):
        """Exporta propriedades para JSON"""
        data = []
        for prop in properties:
            prop_dict = asdict(prop)
            # Converter datetime para string
            for key in ['created_at', 'updated_at']:
                if prop_dict.get(key):
                    prop_dict[key] = prop_dict[key].isoformat()
            data.append(prop_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exportado {len(data)} imóveis para {filepath}")


def main():
    """Função principal de demonstração"""
    bot = RealEstateBot()
    
    # Exemplo de uso
    logger.info("Lisboa Real Estate AI - Bot inicializado")
    logger.info(f"Categorias: {list(bot.CATEGORIES.keys())}")
    
    # Aqui seria integrado com os scrapers
    # e o sistema de base de dados

if __name__ == "__main__":
    main()
