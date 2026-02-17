# 🏠 Lisboa Real Estate AI

Sistema de análise de oportunidades imobiliárias na Grande Lisboa.

## 🚀 Links

- **Dashboard:** https://lisboa-real-estate-ai-originaly-gmailcoms-projects.vercel.app
- **GitHub:** https://github.com/rebelpaulo/lisboa-real-estate-ai

## 📋 Como Usar

### Dashboard Web
Acede ao dashboard e explora as oportunidades com filtros:
- **Categoria:** A (Estagnado), B (Preço Agressivo), C (Intervenção), D (Fundamentada)
- **Score:** 0-100 pontos de oportunidade
- **Tempo no mercado:** >3, >6, >12 meses
- **Tipologia:** T0-T5, Moradia
- **Preço:** Faixa de preços
- **Localização:** Freguesia

### Agente Python (Local)

```bash
# 1. Entrar na pasta do agente
cd agent

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt
playwright install chromium

# 4. Executar busca
python main.py --search lisboa --typology t2 --min-score 60

# 5. Ver estatísticas
python main.py --stats

# 6. Modo daemon (atualização automática)
python main.py --daemon --interval 3600
```

### Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `--search LOCAL` | Busca imóveis numa localização |
| `--typology TIPO` | Filtra por tipologia (t0, t1, t2, etc.) |
| `--min-score N` | Score mínimo de oportunidade |
| `--category CAT` | Categoria (A, B, C, D) |
| `--min-days N` | Mínimo de dias no mercado |
| `--max-days N` | Máximo de dias no mercado |
| `--report` | Gera relatório markdown |
| `--sync` | Sincroniza com dashboard |
| `--daemon` | Modo contínuo |
| `--stats` | Mostra estatísticas |

## 🏗️ Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Agente    │────▶│   GitHub    │────▶│   Vercel    │
│   (Python)  │     │   (Dados)   │     │ (Dashboard) │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 📊 Categorias de Oportunidade

| Categoria | Descrição | Critérios |
|-----------|-----------|-----------|
| 🔴 **A** | Ativo Estagnado | ≥180 dias, ≥2 reduções, ≥10% desconto |
| 🟡 **B** | Preço Agressivo | ≤30 dias, ≥12% abaixo da média |
| 🟢 **C** | Potencial Intervenção | Preço baixo + drivers de valorização |
| 🔵 **D** | Outras Oportunidades | Casos especiais fundamentados |

## 👤 Equipa

- **Paulo** - Product Owner
- **Tomás** - Analista Sénior Imobiliário  
- **Jarbas** - Developer/AI

## 📝 Notas

- O dashboard usa dados mock para demonstração
- Para dados reais, executar o agente Python
- O agente pode fazer scraping de portais (Idealista, etc.)
- Dados são sincronizados via GitHub
