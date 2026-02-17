"""
Motor de Análise - Lisboa Real Estate AI
Análise de mercado, comparáveis e scoring
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from statistics import mean, median, stdev
import math

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Dados de mercado para uma zona específica"""
    parish: str
    municipality: str
    typology: str
    avg_price_m2: float
    median_price_m2: float
    min_price_m2: float
    max_price_m2: float
    std_dev: float
    sample_size: int
    trend_6m: float  # Variação percentual em 6 meses
    trend_12m: float  # Variação percentual em 12 meses

@dataclass
class Comparable:
    """Imóvel comparável para análise"""
    id: str
    price: float
    area_m2: float
    price_per_m2: float
    location: str
    distance_km: float
    days_on_market: int
    condition: str  # novo, bom, para_renovar
    similarity_score: float  # 0-1

class MarketAnalyzer:
    """Analisador de mercado imobiliário"""
    
    # Fatores de ajuste para comparáveis
    CONDITION_MULTIPLIERS = {
        'novo': 1.15,
        'excelente': 1.10,
        'bom': 1.00,
        'razoavel': 0.90,
        'para_renovar': 0.75,
        'ruina': 0.50,
    }
    
    # Drivers de valorização de zona
    VALUE_DRIVERS = {
        'hospital': {'radius_km': 1.0, 'impact': 0.05},
        'universidade': {'radius_km': 0.8, 'impact': 0.08},
        'metro': {'radius_km': 0.5, 'impact': 0.10},
        'comboio': {'radius_km': 0.8, 'impact': 0.06},
        'escola_top': {'radius_km': 1.0, 'impact': 0.07},
        'centro_comercial': {'radius_km': 0.5, 'impact': 0.03},
        'parque': {'radius_km': 0.3, 'impact': 0.04},
        'rio': {'radius_km': 0.5, 'impact': 0.08},
        'reabilitacao_urbana': {'radius_km': 0.0, 'impact': 0.15},  # Zona inteira
    }
    
    def __init__(self):
        self.cache = {}
    
    def calculate_market_metrics(self, comparables: List[Comparable]) -> MarketData:
        """
        Calcula métricas de mercado a partir de comparáveis
        
        Args:
            comparables: Lista de imóveis comparáveis
            
        Returns:
            MarketData com estatísticas da zona
        """
        if not comparables:
            raise ValueError("Lista de comparáveis vazia")
        
        prices = [c.price_per_m2 for c in comparables]
        
        return MarketData(
            parish=comparables[0].location,
            municipality="",
            typology="",
            avg_price_m2=mean(prices),
            median_price_m2=median(prices),
            min_price_m2=min(prices),
            max_price_m2=max(prices),
            std_dev=stdev(prices) if len(prices) > 1 else 0,
            sample_size=len(comparables),
            trend_6m=0.0,  # Seria calculado com dados históricos
            trend_12m=0.0
        )
    
    def find_comparables(self, target: Dict, 
                        listings: List[Dict],
                        max_results: int = 12) -> List[Comparable]:
        """
        Encontra imóveis comparáveis para um alvo
        
        Args:
            target: Imóvel alvo (dict com location, typology, area_m2, etc.)
            listings: Lista de todos os imóveis disponíveis
            max_results: Número máximo de comparáveis
            
        Returns:
            Lista de Comparable ordenada por similaridade
        """
        comparables = []
        
        for listing in listings:
            # Ignorar o próprio imóvel
            if listing.get('id') == target.get('id'):
                continue
            
            # Calcular score de similaridade
            similarity = self._calculate_similarity(target, listing)
            
            if similarity > 0.5:  # Mínimo de similaridade
                comparable = Comparable(
                    id=listing.get('id'),
                    price=listing.get('price', 0),
                    area_m2=listing.get('area_m2', 0),
                    price_per_m2=listing.get('price_per_m2', 0),
                    location=listing.get('parish', ''),
                    distance_km=listing.get('distance_km', 0),
                    days_on_market=listing.get('days_on_market', 0),
                    condition=listing.get('condition', 'bom'),
                    similarity_score=similarity
                )
                comparables.append(comparable)
        
        # Ordenar por similaridade e limitar resultados
        comparables.sort(key=lambda x: x.similarity_score, reverse=True)
        return comparables[:max_results]
    
    def _calculate_similarity(self, target: Dict, candidate: Dict) -> float:
        """Calcula score de similaridade entre dois imóveis (0-1)"""
        score = 0.0
        weights = 0.0
        
        # Mesma tipologia (peso alto)
        if target.get('typology') == candidate.get('typology'):
            score += 0.30
        weights += 0.30
        
        # Mesma freguesia (peso alto)
        if target.get('parish') == candidate.get('parish'):
            score += 0.25
        weights += 0.25
        
        # Área similar (peso médio)
        target_area = target.get('area_m2', 0)
        candidate_area = candidate.get('area_m2', 0)
        if target_area > 0 and candidate_area > 0:
            area_diff = abs(target_area - candidate_area) / target_area
            score += 0.20 * max(0, 1 - area_diff)
        weights += 0.20
        
        # Estado similar (peso médio)
        if target.get('condition') == candidate.get('condition'):
            score += 0.15
        weights += 0.15
        
        # Proximidade (peso baixo)
        distance = candidate.get('distance_km', 999)
        if distance < 0.5:
            score += 0.10
        elif distance < 1.0:
            score += 0.05
        weights += 0.10
        
        return score / weights if weights > 0 else 0
    
    def adjust_comparable_price(self, comparable: Comparable, 
                                target_condition: str) -> float:
        """
        Ajusta o preço de um comparável para o estado do alvo
        
        Args:
            comparable: Imóvel comparável
            target_condition: Estado do imóvel alvo
            
        Returns:
            Preço ajustado por m²
        """
        comp_mult = self.CONDITION_MULTIPLIERS.get(comparable.condition, 1.0)
        target_mult = self.CONDITION_MULTIPLIERS.get(target_condition, 1.0)
        
        # Ajustar para o estado do alvo
        adjusted_price = comparable.price_per_m2 * (target_mult / comp_mult)
        
        return adjusted_price
    
    def calculate_value_drivers(self, location: Dict) -> Dict[str, float]:
        """
        Calcula o impacto dos drivers de valorização numa localização
        
        Args:
            location: Dict com coordenadas e proximidades
            
        Returns:
            Dict com impacto de cada driver
        """
        impacts = {}
        total_impact = 0.0
        
        for driver, config in self.VALUE_DRIVERS.items():
            distance = location.get(f'distance_{driver}_km', 999)
            
            if distance <= config['radius_km']:
                # Impacto máximo se dentro do raio
                impact = config['impact']
            elif distance <= config['radius_km'] * 2:
                # Impacto decrescente até 2x o raio
                impact = config['impact'] * (1 - (distance - config['radius_km']) / config['radius_km'])
            else:
                impact = 0.0
            
            impacts[driver] = impact
            total_impact += impact
        
        impacts['total'] = total_impact
        return impacts
    
    def estimate_negotiation_room(self, property_data: Dict) -> Dict:
        """
        Estima a margem de negociação disponível
        
        Args:
            property_data: Dados do imóvel
            
        Returns:
            Dict com estimativas de negociação
        """
        factors = []
        base_discount = 0.0
        max_discount = 0.0
        
        # Tempo no mercado
        days = property_data.get('days_on_market', 0)
        if days > 365:
            base_discount += 10
            max_discount += 20
            factors.append("Há mais de 1 ano no mercado")
        elif days > 180:
            base_discount += 7
            max_discount += 15
            factors.append("Há mais de 6 meses no mercado")
        elif days > 90:
            base_discount += 3
            max_discount += 8
            factors.append("Há mais de 3 meses no mercado")
        
        # Reduções anteriores
        price_history = property_data.get('price_history', [])
        drops = len([h for h in price_history if h.get('change', 0) < 0])
        if drops >= 3:
            base_discount += 5
            max_discount += 10
            factors.append(f"{drops} reduções anteriores")
        elif drops >= 1:
            base_discount += 2
            max_discount += 5
            factors.append("Redução anterior de preço")
        
        # Comparáveis mais baratos
        market_avg = property_data.get('market_avg_price_m2')
        price_m2 = property_data.get('price_per_m2')
        if market_avg and price_m2 and price_m2 > market_avg:
            premium = (price_m2 - market_avg) / market_avg * 100
            if premium > 15:
                base_discount += 5
                max_discount += 10
                factors.append(f"{premium:.0f}% acima da média da zona")
        
        return {
            'base_discount_percent': min(base_discount, 25),
            'max_discount_percent': min(max_discount, 35),
            'factors': factors,
            'confidence': 'alta' if len(factors) >= 3 else 'média' if len(factors) >= 2 else 'baixa'
        }
    
    def generate_investment_analysis(self, property_data: Dict,
                                     comparables: List[Comparable],
                                     renovation_cost: Optional[float] = None) -> Dict:
        """
        Gera análise completa de investimento
        
        Args:
            property_data: Dados do imóvel
            comparables: Lista de comparáveis
            renovation_cost: Custo estimado de renovação (opcional)
            
        Returns:
            Dict com análise completa
        """
        # Calcular métricas de mercado
        market = self.calculate_market_metrics(comparables)
        
        # Análise de negociação
        negotiation = self.estimate_negotiation_room(property_data)
        
        # Drivers de valorização
        value_drivers = self.calculate_value_drivers(
            property_data.get('location', {})
        )
        
        # Preço justo estimado
        adjusted_prices = [
            self.adjust_comparable_price(c, property_data.get('condition', 'bom'))
            for c in comparables[:6]
        ]
        fair_price_m2 = mean(adjusted_prices) if adjusted_prices else market.median_price_m2
        
        area = property_data.get('area_m2', 0)
        fair_price = fair_price_m2 * area
        current_price = property_data.get('price', 0)
        
        analysis = {
            'current_price': current_price,
            'fair_price_estimate': fair_price,
            'price_vs_fair': ((current_price - fair_price) / fair_price * 100) if fair_price > 0 else 0,
            'market_metrics': {
                'avg_price_m2': market.avg_price_m2,
                'median_price_m2': market.median_price_m2,
                'sample_size': market.sample_size,
            },
            'negotiation': negotiation,
            'value_drivers': value_drivers,
            'comparables_summary': {
                'count': len(comparables),
                'avg_similarity': mean([c.similarity_score for c in comparables]) if comparables else 0,
            }
        }
        
        # Análise de renovação se fornecido custo
        if renovation_cost:
            post_renovation_value = fair_price * 1.15  # Estimativa conservadora
            total_investment = current_price + renovation_cost
            potential_profit = post_renovation_value - total_investment
            
            analysis['renovation'] = {
                'estimated_cost': renovation_cost,
                'post_renovation_estimate': post_renovation_value,
                'total_investment': total_investment,
                'potential_profit': potential_profit,
                'roi_percent': (potential_profit / total_investment * 100) if total_investment > 0 else 0,
            }
        
        return analysis


def main():
    """Demonstração do analisador"""
    analyzer = MarketAnalyzer()
    
    # Exemplo de uso
    logger.info("Market Analyzer inicializado")
    logger.info(f"Drivers de valorização: {list(analyzer.VALUE_DRIVERS.keys())}")

if __name__ == "__main__":
    main()
