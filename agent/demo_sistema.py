"""
Demo do Sistema de Análise - Lisboa Real Estate AI
Gera oportunidades de exemplo para demonstrar o sistema completo
"""

from datetime import datetime, timedelta
from opportunity_analyzer import (
    OpportunityAnalyzer, PropertyOpportunity, Location, 
    BenchmarkData, ZoneDrivers, PriceHistory, AssetType, AssetCategory
)

def criar_oportunidades_demo():
    """Cria oportunidades de demonstração baseadas em cenários reais"""
    
    analyzer = OpportunityAnalyzer()
    
    # Oportunidade 1: T2 Estagnado em Belém (Categoria A)
    opp1 = PropertyOpportunity(
        id="demo_001",
        fontes=["https://idealista.pt/imovel/12345"],
        categoria=AssetCategory.ESTAGNADO,
        tipo=AssetType.T2,
        localizacao=Location(
            morada="Rua de Belém 45, 2º Esq",
            freguesia="Belém",
            concelho="Lisboa"
        ),
        area_m2=85,
        tipologia="T2",
        quartos=2,
        casas_banho=1,
        ano_construcao=1985,
        estado_conservacao="Necessita obras",
        preco_atual=285000,
        preco_original=320000,
        historico_precos=[
            PriceHistory(datetime(2024, 8, 1), 320000, "listagem"),
            PriceHistory(datetime(2024, 10, 15), 305000, "reducao"),
            PriceHistory(datetime(2024, 12, 1), 295000, "reducao"),
            PriceHistory(datetime(2025, 1, 15), 285000, "reducao"),
        ],
        dias_no_mercado=195,
        tempo_confirmado=True,
        metodo_tempo="Histórico de preços",
        benchmark=BenchmarkData(
            media_microzona=3800,
            mediana_microzona=3750,
            min_microzona=3200,
            max_microzona=4500,
            num_comparaveis=8,
            raio_metros=600,
            fonte_ine=3650,
            notas_ine="Dados INE 2024 T2 Belém"
        ),
        drivers_zona=ZoneDrivers(
            transportes=["Elétrico 15E", "Bus 728", "Estação CP Belém"],
            saude=["Hospital Egas Moniz"],
            educacao=["Universidade Nova"],
            emprego_comercio=["Mosteiro dos Jerónimos", "Torre de Belém", "Pasteis de Belém"],
            projetos_urbanos=["Reabilitação zona ribeirinha", "Parque Linear"],
            notas="Zona turística com forte procura"
        ),
        drivers_intervencao=[
            "Renovação completa de cozinha e casas de banho",
            "Substituição de caixilharia por PVC duplo",
            "Pavimentos flutuantes em madeira",
            "Sistema de ar condicionado",
            "Estima-se valorização pós-obra: €4200/m²"
        ],
        riscos=[
            "Condomínio antigo sem elevador",
            "Obras necessárias na fachada do prédio",
            "Estacionamento difícil na zona"
        ],
        sintese_executiva="T2 em Belém estagnado há 195 dias com 3 reduções (11% total). Preço/m² €3350 vs média €3800. Potencial de valorização €400/m² após renovação. Zona turística com liquidez garantida.",
        status="Observação"
    )
    analyzer.adicionar_oportunidade(opp1)
    
    # Oportunidade 2: Prédio Devoluto em Alcântara (Categoria C) - Score ALTO
    opp2 = PropertyOpportunity(
        id="demo_002",
        fontes=["https://imovirtual.pt/imovel/67890"],
        tipo=AssetType.PREDIO,
        localizacao=Location(
            morada="Rua das Janelas Verdes 12",
            freguesia="Estrela",
            concelho="Lisboa"
        ),
        area_m2=420,
        preco_atual=850000,
        preco_original=950000,
        historico_precos=[
            PriceHistory(datetime(2024, 6, 1), 950000, "listagem"),
            PriceHistory(datetime(2024, 9, 1), 900000, "reducao"),
            PriceHistory(datetime(2024, 12, 1), 850000, "reducao"),
        ],
        dias_no_mercado=260,
        tempo_confirmado=True,
        metodo_tempo="Histórico de preços",
        benchmark=BenchmarkData(
            media_microzona=2800,
            mediana_microzona=2750,
            min_microzona=2200,
            max_microzona=3500,
            num_comparaveis=6,
            raio_metros=800,
            fonte_ine=2650,
            notas_ine="Prédios devolutos raros na zona"
        ),
        drivers_zona=ZoneDrivers(
            transportes=["Metro Santos", "Bus 727, 732"],
            saude=["Hospital de Santa Maria"],
            educacao=["IST", "Faculdade de Belas Artes"],
            emprego_comercio=["LX Factory", "Docas", "Centro de Alcântara"],
            projetos_urbanos=["Regeneração de Alcântara", "Projeto de reabilitação urbana"],
            notas="Zona em gentrificação acelerada"
        ),
        drivers_intervencao=[
            "Conversão para 4 apartamentos T1/T2 (turismo/aluguel)",
            "Reabilitação completa com aumento de área",
            "Possibilidade de rooftop/terraço comum",
            "Valorização estimada: €4500/m² pós-obra",
            "Yield bruto estimado: 6-7%"
        ],
        riscos=[
            "Projeto de arquitetura complexo"
        ],
        sintese_executiva="Prédio devoluto em Alcântara com potencial de fracionamento. Preço/m² €2020 vs €2800 zona. LX Factory a 300m. Alto potencial valorização.",
        status="Due Diligence"
    )
    analyzer.adicionar_oportunidade(opp2)
    
    # Oportunidade 3: T1 Novo em Santos Preço Agressivo (Categoria B) - Score ALTO
    opp3 = PropertyOpportunity(
        id="demo_003",
        fontes=["https://casa.sapo.pt/imovel/11111"],
        tipo=AssetType.T1,
        localizacao=Location(
            morada="Rua de São Bento 89, R/C",
            freguesia="Estrela",
            concelho="Lisboa"
        ),
        area_m2=55,
        preco_atual=195000,
        historico_precos=[
            PriceHistory(datetime(2025, 2, 10), 195000, "listagem"),
        ],
        dias_no_mercado=8,
        tempo_confirmado=True,
        metodo_tempo="Data de listagem",
        benchmark=BenchmarkData(
            media_microzona=5200,
            mediana_microzona=5100,
            min_microzona=4500,
            max_microzona=6000,
            num_comparaveis=10,
            raio_metros=500,
            fonte_ine=4800,
            notas_ine="T1 novo Santos/Estrela"
        ),
        drivers_zona=ZoneDrivers(
            transportes=["Metro Rato", "Elétrico 28", "Bus 758"],
            saude=["Hospital de Santa Maria", "Clínicas privadas"],
            educacao=["Universidade Nova", "Escolas internacionais"],
            emprego_comercio=["Santos Design District", "Príncipe Real", "Chiado"],
            projetos_urbanos=["Gentrificação contínua", "Novos restaurantes/cafés"],
            notas="Zona jovem e trendy, alta procura"
        ),
        drivers_intervencao=[
            "Imóvel novo, não necessita obras",
            "Possibilidade de AL imediata",
            "Mobiliário moderno incluído"
        ],
        riscos=[
            "R/C pode ter menos procura"
        ],
        sintese_executiva="T1 novo em Santos a €3545/m² vs média €5200 (32% abaixo!). Recém-listado. Zona premium com liquidez imediata. Oportunidade de arbitragem clara.",
        status="Avançar"
    )
    analyzer.adicionar_oportunidade(opp3)
    
    # Oportunidade 4: Terreno Urbanizável Oeiras (Categoria D)
    opp4 = PropertyOpportunity(
        id="demo_004",
        fontes=["https://supercasa.pt/imovel/22222"],
        categoria=AssetCategory.OUTRAS_FUNDAMENTADAS,
        tipo=AssetType.TERRENO,
        localizacao=Location(
            morada="Rua dos Combatentes, Lote 12",
            freguesia="Oeiras",
            concelho="Oeiras"
        ),
        area_m2=850,
        tipologia="Terreno urbano",
        preco_atual=425000,
        preco_original=480000,
        historico_precos=[
            PriceHistory(datetime(2024, 5, 1), 480000, "listagem"),
            PriceHistory(datetime(2024, 11, 1), 450000, "reducao"),
            PriceHistory(datetime(2025, 1, 15), 425000, "reducao"),
        ],
        dias_no_mercado=290,
        tempo_confirmado=True,
        metodo_tempo="Histórico de preços",
        benchmark=BenchmarkData(
            media_microzona=650,
            mediana_microzona=620,
            min_microzona=500,
            max_microzona=800,
            num_comparaveis=4,
            raio_metros=1000,
            fonte_ine=None,
            notas_ine="Dados INE limitados para terrenos"
        ),
        drivers_zona=ZoneDrivers(
            transportes=["Linha de Cascais", "A5", "CRIL"],
            saude=["Hospital de São Francisco Xavier"],
            educacao=["Nova SBE", "Escolas internacionais"],
            emprego_comercio=["Taguspark", "Lagoas Park", "Paço de Arcos"],
            projetos_urbanos=["Expansão Oeiras Valley", "Nova linha de metro"],
            notas="Zona de forte crescimento empresarial"
        ),
        drivers_intervencao=[
            "Viability para moradia unifamiliar T4+1",
            "Possibilidade de geminado (2 unidades)",
            "Índice de construção: 0.5",
            "Projeto pré-aprovado disponível"
        ],
        riscos=[
            "Licenciamento demorado (12-18 meses)",
            "Custos de construção elevados",
            "Mercado de luxo em Oeiras competitivo",
            "Infraestruturas (água/luz) a confirmar"
        ],
        sintese_executiva="Terreno 850m² em Oeiras a €500/m². Potencial construção 425m². Projeto pré-aprovado. Zona Oeiras Valley em expansão. Investimento para construção própria ou especulação.",
        status="Observação"
    )
    analyzer.adicionar_oportunidade(opp4)
    
    # Oportunidade 5: Loja Térrea Campo de Ourique (Categoria C)
    opp5 = PropertyOpportunity(
        id="demo_005",
        fontes=["https://idealista.pt/imovel/33333"],
        categoria=AssetCategory.POTENCIAL_INTERVENCAO,
        tipo=AssetType.LOJA,
        localizacao=Location(
            morada="Rua Ferreira Borges 45, R/C",
            freguesia="Campo de Ourique",
            concelho="Lisboa"
        ),
        area_m2=75,
        tipologia="Loja",
        preco_atual=185000,
        preco_original=220000,
        historico_precos=[
            PriceHistory(datetime(2024, 7, 1), 220000, "listagem"),
            PriceHistory(datetime(2024, 10, 1), 200000, "reducao"),
            PriceHistory(datetime(2025, 1, 1), 185000, "reducao"),
        ],
        dias_no_mercado=230,
        tempo_confirmado=True,
        metodo_tempo="Histórico de preços",
        benchmark=BenchmarkData(
            media_microzona=3200,
            mediana_microzona=3100,
            min_microzona=2500,
            max_microzona=4000,
            num_comparaveis=6,
            raio_metros=400,
            fonte_ine=None,
            notas_ine="Dados comerciais limitados INE"
        ),
        drivers_zona=ZoneDrivers(
            transportes=["Metro Rato", "Elétrico 25, 28"],
            saude=["Hospital de Santa Maria"],
            educacao=["Colégios privados"],
            emprego_comercio=["Mercado de Campo de Ourique", "Comércio local"],
            projetos_urbanos=["Reabilitação Mercado", "Novos espaços comerciais"],
            notas="Bairro residencial com forte comércio de proximidade"
        ),
        drivers_intervencao=[
            "Conversão para T0/T1 (uso misto)",
            "Rentabilização como café/esplanada",
            "Possibilidade de rooftop comercial",
            "Licença de esplanada fácil"
        ],
        riscos=[
            "Mudança de uso requer licenciamento",
            "Restrições de estacionamento",
            "Concorrência de novos espaços"
        ],
        sintese_executiva="Loja térrea em Campo de Ourique a €2466/m² vs €3200 zona. Potencial conversão residencial ou F&B. Mercado reabilitado a 100m. Oportunidade de reposicionamento.",
        status="Negociação"
    )
    analyzer.adicionar_oportunidade(opp5)
    
    return analyzer

def gerar_relatorio_demo():
    """Gera relatório completo de demonstração"""
    print("=" * 80)
    print("🏠 LISBOA REAL ESTATE AI - SISTEMA DE ANÁLISE DE OPORTUNIDADES")
    print("=" * 80)
    print()
    
    analyzer = criar_oportunidades_demo()
    
    # Gerar curadoria final
    curadoria = analyzer.get_curadoria_final(12)
    
    print(f"📊 TOTAL ANALISADO: {len(analyzer.oportunidades)} ativos")
    print(f"🎯 CURADORIA FINAL: {len(curadoria)} ativos (score ≥70)")
    print()
    
    # Resumo por categoria
    print("📋 DISTRIBUIÇÃO POR CATEGORIA:")
    for cat in AssetCategory:
        count = len([o for o in curadoria if o.categoria == cat])
        print(f"   {cat.value} - {cat.name.replace('_', ' ')}: {count} ativos")
    print()
    
    # Tabela resumo
    print("=" * 80)
    print("🏆 TOP OPORTUNIDADES (ordenadas por prioridade)")
    print("=" * 80)
    print()
    print(f"{'Rank':<6} {'Cat':<4} {'Tipo':<12} {'Zona':<18} {'Área':<8} {'Preço':<12} {'€/m²':<8} {'Score':<6}")
    print("-" * 80)
    
    for i, opp in enumerate(curadoria, 1):
        preco_m2 = opp.preco_atual / opp.area_m2
        print(f"{i:<6} {opp.categoria.value:<4} {opp.tipo.value:<12} {opp.localizacao.freguesia:<18} "
              f"{opp.area_m2:<8.0f} €{opp.preco_atual:<10,.0f} €{preco_m2:<6.0f} {opp.score_total:<6}")
    
    print()
    print("=" * 80)
    print("📄 FICHAS DETALHADAS")
    print("=" * 80)
    print()
    
    for i, opp in enumerate(curadoria, 1):
        print(f"### #{i} - {opp.tipo.value} em {opp.localizacao.freguesia}")
        print()
        print(f"Categoria: {opp.categoria.value} ({opp.categoria.name.replace('_', ' ')})")
        print(f"Score Total: {opp.score_total}/100")
        print(f"Status: {opp.status}")
        print()
        print(f"💰 PREÇO:")
        print(f"   Atual: €{opp.preco_atual:,.0f}")
        if opp.preco_original:
            reducao = (opp.preco_original - opp.preco_atual) / opp.preco_original * 100
            print(f"   Original: €{opp.preco_original:,.0f} ({reducao:.1f}% redução)")
        print(f"   €/m²: €{opp.preco_atual / opp.area_m2:,.0f}")
        print(f"   Dias no mercado: {opp.dias_no_mercado} {'(confirmado)' if opp.tempo_confirmado else '(estimado)'}")
        print()
        print(f"📍 LOCALIZAÇÃO:")
        print(f"   {opp.localizacao.morada}")
        print(f"   {opp.localizacao.freguesia}, {opp.localizacao.concelho}")
        print()
        
        if opp.benchmark:
            print(f"📊 BENCHMARK:")
            print(f"   Média microzona: €{opp.benchmark.media_microzona:,.0f}/m²")
            print(f"   vs Mercado: {((opp.preco_atual/opp.area_m2 - opp.benchmark.media_microzona)/opp.benchmark.media_microzona*100):+.1f}%")
            print(f"   Comparáveis: {opp.benchmark.num_comparaveis} (raio {opp.benchmark.raio_metros}m)")
            print()
        
        if opp.drivers_intervencao:
            print(f"🔧 DRIVERS DE INTERVENÇÃO:")
            for d in opp.drivers_intervencao:
                print(f"   • {d}")
            print()
        
        if opp.riscos:
            print(f"⚠️  RISCOS:")
            for r in opp.riscos:
                print(f"   • {r}")
            print()
        
        print(f"📝 SÍNTESE:")
        print(f"   {opp.sintese_executiva}")
        print()
        print(f"🔗 Fonte: {', '.join(opp.fontes)}")
        print()
        print("-" * 80)
        print()
    
    # Guardar relatórios
    analyzer.gerar_relatorio_json("oportunidades_demo.json")
    analyzer.gerar_relatorio_markdown("oportunidades_demo.md")
    
    print("💾 Relatórios guardados:")
    print("   • oportunidades_demo.json")
    print("   • oportunidades_demo.md")
    print()
    print("=" * 80)

if __name__ == "__main__":
    gerar_relatorio_demo()
