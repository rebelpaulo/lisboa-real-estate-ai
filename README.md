# Lisboa Real Estate AI

Sistema híbrido (Agente + Dashboard) para identificar oportunidades imobiliárias na Grande Lisboa com análise de ineficiência de mercado.

## 🎯 Objetivo

Identificar oportunidades de investimento imobiliário através de análise automatizada de dados de múltiplas fontes, classificando imóveis por potencial de negociação e valorização.

## 📊 Categorias de Oportunidades

| Categoria | Descrição | Critérios |
|-----------|-----------|-----------|
| 🔴 **A** | Ativo estagnado com pressão | ≥180 dias no mercado, ≥2 reduções de preço, ≥10% desconto acumulado |
| 🟡 **B** | Recém-entrado com preço agressivo | ≤30 dias no mercado, ≥12% abaixo da média da zona |
| 🟢 **C** | Potencial valorização por intervenção | Preço baixo + drivers de valorização (obras, layout, etc.) |
| 🔵 **D** | Outras oportunidades fundamentadas | Casos especiais com análise fundamentada |

## 🌐 Fontes de Dados

### Portais Imobiliários
- Idealista.pt
- Imovirtual.pt
- CasaSapo.pt
- Supercasa.pt

### Plataformas de Leilões
- Leilosoc
- E-leiloes
- Citius
- +40 outras plataformas

## 📈 Funcionalidades

### Filtros de Tempo no Mercado
- > 3 meses
- > 6 meses
- > 12 meses

### Score de Negociação (0-100)
Baseado em:
- Tempo no mercado
- Reduções de preço históricas
- Comparáveis na zona
- Motivação do vendedor (indicadores)

### Benchmark €/m²
- 6-12 comparáveis na zona
- Ajuste por tipologia, estado, amenities
- Tendência de preços (6-12 meses)

### Mais-Valias de Zona
- Proximidade a hospitais
- Universidades e escolas
- Transportes públicos
- Zonas de reabilitação urbana

## 🏗️ Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Agent     │────▶│  GitHub     │────▶│  Dashboard  │
│  (Python)   │     │   Bridge    │     │  (React)    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                        │
       ▼                                        ▼
┌─────────────┐                          ┌─────────────┐
│   SQLite    │                          │   SQLite    │
│   (local)   │                          │   (sync)    │
└─────────────┘                          └─────────────┘
```

## 📁 Estrutura do Projeto

```
lisboa-real-estate-ai/
├── agent/              # Código Python do agente
│   ├── bot.py         # Script principal
│   ├── analyzer.py    # Motor de análise
│   ├── scrapers.py    # Scrapers dos portais
│   ├── database.py    # Gestão da base de dados
│   └── requirements.txt
├── dashboard/          # Dashboard web
│   ├── index.html     # Ponto de entrada
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── styles/
│   └── package.json
├── data/              # Dados locais
│   ├── listings.db    # SQLite
│   └── cache/         # Cache de requisições
└── docs/              # Documentação
    └── api/           # Documentação de APIs
```

## 🚀 Instalação

```bash
# Clonar repositório
git clone <repo-url>
cd lisboa-real-estate-ai

# Instalar dependências do agente
cd agent
pip install -r requirements.txt

# Instalar dependências do dashboard
cd ../dashboard
npm install
```

## 🏃 Execução

```bash
# Iniciar agente
cd agent
python bot.py

# Iniciar dashboard (desenvolvimento)
cd dashboard
npm run dev
```

## 👤 Equipa

- **Paulo** - Product Owner
- **Tomás** - Analista Sénior Imobiliário
- **Jarbas** - Developer/AI

## 📝 Roadmap

- [x] Estrutura inicial do projeto
- [ ] Scrapers dos 4 portais principais
- [ ] Classificação A/B/C/D
- [ ] Dashboard web básico
- [ ] Filtros do Tomás (tempo, score, benchmark)
- [ ] Integração com dados INE
- [ ] Alertas em tempo real
- [ ] Machine learning para scoring
