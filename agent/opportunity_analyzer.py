"""
Lisboa Real Estate AI - Sistema de Análise de Oportunidades
Analista Sénior de Investimentos Imobiliários
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssetCategory(Enum):
    """Categorias de oportunidade"""
    ESTAGNADO = "A"  # ≥180 dias, ≥2 reduções, ≥10% desconto
    PRECO_AGRESSIVO = "B"  # ≤30 dias, ≥12% abaixo média
    POTENCIAL_INTERVENCAO = "C"  # Preço baixo + drivers valorização
    OUTRAS_FUNDAMENTADAS = "D"  # Casos especiais

class AssetType(Enum):
    """Tipos de ativos"""
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"
    T5 = "T5"
    MORADIA = "Moradia"
    PREDIO = "Prédio"
    LOJA = "Loja"
    ARMAZEM = "Armazém"
    TERRENO = "Terreno"
    ATIPICO = "Atípico"

@dataclass
class Location:
    """Localização do ativo"""
    morada: str
    freguesia: str
    concelho: str
    distrito: str = "Lisboa"
    codigo_postal: str = ""
    coordenadas: Optional[Tuple[float, float]] = None

@dataclass
class BenchmarkData:
    """Dados de benchmark €/m²"""
    media_microzona: float
    mediana_microzona: float
    min_microzona: float
    max_microzona: float
    num_comparaveis: int
    raio_metros: int
    fonte_ine: Optional[float] = None
    notas_ine: str = ""

@dataclass
class ZoneDrivers:
    """Drivers de valorização da zona"""
    transportes: List[str]
    saude: List[str]
    educacao: List[str]
    emprego_comercio: List[str]
    projetos_urbanos: List[str]
    notas: str

@dataclass
class PriceHistory:
    """Histórico de preços"""
    data: datetime
    preco: float
    evento: str  # "listagem", "reducao", "aumento"

@dataclass
class PropertyOpportunity:
    """Modelo completo de oportunidade imobiliária"""
    # Identificação (obrigatórios primeiro)
    id: str
    fontes: List[str]  # URLs dos portais
    tipo: AssetType
    localizacao: Location
    area_m2: float
    preco_atual: float
    
    # Opcionais com defaults
    categoria: AssetCategory = None
    area_bruta: Optional[float] = None
    tipologia: str = ""
    quartos: int = 0
    casas_banho: int = 0
    ano_construcao: Optional[int] = None
    estado_conservacao: str = ""
    preco_original: Optional[float] = None
    historico_precos: List[PriceHistory] = None
    dias_no_mercado: int = 0
    tempo_confirmado: bool = False
    metodo_tempo: str = ""
    benchmark: Optional[BenchmarkData] = None
    drivers_zona: Optional[ZoneDrivers] = None
    score_ineficiencia: int = 0  # 0-30
    score_valorizacao: int = 0   # 0-25
    score_liquidez: int = 0      # 0-20
    score_risco: int = 0         # -15 a 0
    score_qualidade: int = 0     # 0-10
    score_total: int = 0         # 0-100
    drivers_intervencao: List[str] = None
    riscos: List[str] = None
    status: str = "Observação"
    sintese_executiva: str = ""
    notas: str = ""
    data_analise: datetime = None
    analista: str = "Jarbas AI"

class OpportunityAnalyzer:
    """Analisador de oportunidades imobiliárias"""
    
    def __init__(self):
        self.oportunidades: List[PropertyOpportunity] = []
        
    def calcular_score(self, opp: PropertyOpportunity) -> int:
        """Calcula score total 0-100"""
        # 1. Ineficiência de mercado (0-30)
        score_inef = 0
        if opp.dias_no_mercado >= 365:
            score_inef = 30
        elif opp.dias_no_mercado >= 180:
            score_inef = 25
        elif opp.dias_no_mercado >= 90:
            score_inef = 15
        elif opp.dias_no_mercado >= 30:
            score_inef = 8
            
        # Reduções de preço
        if opp.preco_original and opp.preco_original > opp.preco_atual:
            reducao_pct = (opp.preco_original - opp.preco_atual) / opp.preco_original * 100
            if reducao_pct >= 20:
                score_inef += 15
            elif reducao_pct >= 10:
                score_inef += 10
            elif reducao_pct >= 5:
                score_inef += 5
        
        opp.score_ineficiencia = min(score_inef, 30)
        
        # 2. Potencial de valorização (0-25)
        score_val = 0
        if opp.benchmark:
            preco_m2_atual = opp.preco_atual / opp.area_m2
            vs_media = (preco_m2_atual - opp.benchmark.media_microzona) / opp.benchmark.media_microzona * 100
            
            if vs_media <= -20:
                score_val = 25
            elif vs_media <= -15:
                score_val = 20
            elif vs_media <= -10:
                score_val = 15
            elif vs_media <= -5:
                score_val = 10
        
        # Drivers de intervenção
        if opp.drivers_intervencao:
            score_val += min(len(opp.drivers_intervencao) * 3, 10)
        
        opp.score_valorizacao = min(score_val, 25)
        
        # 3. Liquidez de saída (0-20)
        score_liq = 15  # Base
        
        # Ajustar por tipologia
        tipos_liquidos = [AssetType.T1, AssetType.T2, AssetType.T3]
        if opp.tipo in tipos_liquidos:
            score_liq += 3
        elif opp.tipo == AssetType.T0:
            score_liq += 1
        else:
            score_liq -= 2
            
        # Ajustar por zona
        if opp.drivers_zona:
            num_drivers = len(opp.drivers_zona.transportes) + len(opp.drivers_zona.saude) + \
                         len(opp.drivers_zona.educacao) + len(opp.drivers_zona.emprego_comercio)
            if num_drivers >= 5:
                score_liq += 2
        
        opp.score_liquidez = min(max(score_liq, 0), 20)
        
        # 4. Risco (-15 a 0)
        score_risco = 0
        if opp.riscos:
            score_risco = -min(len(opp.riscos) * 3, 15)
        
        opp.score_risco = score_risco
        
        # 5. Qualidade (0-10)
        score_qual = 5  # Base
        if opp.estado_conservacao and "novo" in opp.estado_conservacao.lower():
            score_qual += 3
        if opp.ano_construcao and opp.ano_construcao >= 2000:
            score_qual += 2
        
        opp.score_qualidade = min(score_qual, 10)
        
        # Total
        opp.score_total = max(0, min(100, 
            opp.score_ineficiencia + 
            opp.score_valorizacao + 
            opp.score_liquidez + 
            opp.score_risco + 
            opp.score_qualidade
        ))
        
        return opp.score_total
    
    def classificar_categoria(self, opp: PropertyOpportunity) -> AssetCategory:
        """Classifica oportunidade na categoria A/B/C/D"""
        
        # Categoria A: Estagnado
        if opp.dias_no_mercado >= 180:
            if opp.preco_original and opp.preco_original > opp.preco_atual:
                reducao = (opp.preco_original - opp.preco_atual) / opp.preco_original * 100
                if reducao >= 10:
                    return AssetCategory.ESTAGNADO
        
        # Categoria B: Preço Agressivo
        if opp.dias_no_mercado <= 30 and opp.benchmark:
            preco_m2 = opp.preco_atual / opp.area_m2
            vs_media = (preco_m2 - opp.benchmark.media_microzona) / opp.benchmark.media_microzona * 100
            if vs_media <= -12:
                return AssetCategory.PRECO_AGRESSIVO
        
        # Categoria C: Potencial Intervenção
        if opp.benchmark:
            preco_m2 = opp.preco_atual / opp.area_m2
            vs_media = (preco_m2 - opp.benchmark.media_microzona) / opp.benchmark.media_microzona * 100
            if vs_media < 0 and opp.drivers_intervencao and len(opp.drivers_intervencao) > 0:
                return AssetCategory.POTENCIAL_INTERVENCAO
        
        # Categoria D: Outras
        return AssetCategory.OUTRAS_FUNDAMENTADAS
    
    def adicionar_oportunidade(self, opp: PropertyOpportunity):
        """Adiciona e analisa nova oportunidade"""
        opp.categoria = self.classificar_categoria(opp)
        self.calcular_score(opp)
        opp.data_analise = datetime.now()
        self.oportunidades.append(opp)
    
    def get_curadoria_final(self, max_ativos: int = 12) -> List[PropertyOpportunity]:
        """Retorna curadoria final ordenada por prioridade"""
        # Filtrar apenas score >= 70
        qualificados = [o for o in self.oportunidades if o.score_total >= 70]
        
        # Ordenar por score (descendente), depois por dias no mercado (ascendente)
        qualificados.sort(key=lambda x: (-x.score_total, x.dias_no_mercado))
        
        return qualificados[:max_ativos]
    
    def gerar_relatorio_json(self, output_file: str = "oportunidades.json"):
        """Gera relatório em JSON"""
        curadoria = self.get_curadoria_final()
        
        relatorio = {
            "data_geracao": datetime.now().isoformat(),
            "total_analisado": len(self.oportunidades),
            "total_curadoria": len(curadoria),
            "oportunidades": [asdict(o) for o in curadoria]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=2, default=str)
        
        return relatorio
    
    def gerar_relatorio_markdown(self, output_file: str = "oportunidades.md"):
        """Gera relatório em Markdown"""
        curadoria = self.get_curadoria_final()
        
        md = f"""# 🏠 Curadoria de Oportunidades Imobiliárias

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  
**Total Analisado:** {len(self.oportunidades)} ativos  
**Curadoria Final:** {len(curadoria)} ativos

---

## 📊 Resumo por Categoria

"""
        
        for cat in AssetCategory:
            count = len([o for o in curadoria if o.categoria == cat])
            md += f"- **{cat.value}** ({cat.name.replace('_', ' ')}): {count} ativos\n"
        
        md += "\n---\n\n## 🎯 Top 12 Oportunidades\n\n"
        md += "| Rank | Categoria | Tipo | Zona | Área | Preço | €/m² | Score | Fonte |\n"
        md += "|------|-----------|------|------|------|-------|------|-------|-------|\n"
        
        for i, opp in enumerate(curadoria, 1):
            preco_m2 = opp.preco_atual / opp.area_m2
            md += f"| {i} | {opp.categoria.value} | {opp.tipo.value} | {opp.localizacao.freguesia} | {opp.area_m2}m² | €{opp.preco_atual:,.0f} | €{preco_m2:,.0f} | {opp.score_total} | [Link]({opp.fontes[0] if opp.fontes else ''}) |\n"
        
        md += "\n---\n\n## 📋 Fichas Detalhadas\n\n"
        
        for i, opp in enumerate(curadoria, 1):
            md += f"""### #{i} - {opp.tipo.value} em {opp.localizacao.freguesia}

**Categoria:** {opp.categoria.value} ({opp.categoria.name.replace('_', ' ')})  
**Score Total:** {opp.score_total}/100  
**Status:** {opp.status}

#### 💰 Preço
- **Atual:** €{opp.preco_atual:,.0f}
- **Original:** €{f'{opp.preco_original:,.0f}' if opp.preco_original else 'N/A'}
- **€/m²:** €{opp.preco_atual / opp.area_m2:,.0f}
- **Dias no mercado:** {opp.dias_no_mercado} {'(confirmado)' if opp.tempo_confirmado else '(estimado)'}

#### 📍 Localização
- {opp.localizacao.morada}
- {opp.localizacao.freguesia}, {opp.localizacao.concelho}

#### 📊 Benchmark
"""
            if opp.benchmark:
                md += f"""- Média microzona: €{opp.benchmark.media_microzona:,.0f}/m²
- Mediana: €{opp.benchmark.mediana_microzona:,.0f}/m²
- Comparáveis: {opp.benchmark.num_comparaveis} (raio {opp.benchmark.raio_metros}m)
"""
            
            if opp.drivers_intervencao:
                md += f"\n#### 🔧 Drivers de Intervenção\n"
                for driver in opp.drivers_intervencao:
                    md += f"- {driver}\n"
            
            if opp.riscos:
                md += f"\n#### ⚠️ Riscos\n"
                for risco in opp.riscos:
                    md += f"- {risco}\n"
            
            md += f"\n#### 📝 Síntese Executiva\n{opp.sintese_executiva}\n\n"
            md += f"**Fonte:** {', '.join(opp.fontes)}\n\n---\n\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return md

# Instância global
analyzer = OpportunityAnalyzer()
