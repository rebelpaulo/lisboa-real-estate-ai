# 🤖 Comandos do Jarbas - Grupo Jarbas Imobiliário

## 💬 Comandos no Telegram (Menciona-me @Frndsgrpbot)

### 🔍 Análise de Imóveis

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `@Frndsgrpbot analisa [URL]` | Analisa um imóvel específico | `@Frndsgrpbot analisa https://idealista.pt/imovel/12345` |
| `@Frndsgrpbot score [URL]` | Calcula score de oportunidade (0-100) | `@Frndsgrpbot score https://...` |
| `@Frndsgrpbot comparaveis [URL]` | Mostra 6-12 comparáveis na zona | `@Frndsgrpbot comparaveis https://...` |

### 📊 Oportunidades

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `@Frndsgrpbot oportunidades` | Top 10 oportunidades (todas as zonas) | `@Frndsgrpbot oportunidades` |
| `@Frndsgrpbot oportunidades [zona]` | Oportunidades numa zona específica | `@Frndsgrpbot oportunidades belém` |
| `@Frndsgrpbot categoria [A/B/C/D]` | Filtra por categoria de oportunidade | `@Frndsgrpbot categoria A` |
| `@Frndsgrpbot tipologia [T0-T5/moradia]` | Filtra por tipologia | `@Frndsgrpbot tipologia T2` |

### 💰 Filtros de Preço & Tempo

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `@Frndsgrpbot preco [min] [max]` | Filtra por faixa de preço | `@Frndsgrpbot preco 200000 400000` |
| `@Frndsgrpbot tempo [dias]` | Imóveis há +X dias no mercado | `@Frndsgrpbot tempo 180` |
| `@Frndsgrpbot zona [freguesia]` | Filtra por freguesia/zona | `@Frndsgrpbot zona alfama` |

### 📈 Dados de Mercado

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `@Frndsgrpbot mercado [zona]` | Média de preços €/m² numa zona | `@Frndsgrpbot mercado cascais` |
| `@Frndsgrpbot tendencia [zona]` | Tendência de preços (6m/12m) | `@Frndsgrpbot tendencia lisboa` |

### 📋 Relatórios

| Comando | Descrição |
|---------|-----------|
| `@Frndsgrpbot relatorio` | Gera relatório do dia em PDF/MD |
| `@Frndsgrpbot relatorio semanal` | Relatório da semana |
| `@Frndsgrpbot stats` | Estatísticas gerais do mercado |

### 🔗 Links Úteis

| Comando | Descrição |
|---------|-----------|
| `@Frndsgrpbot dashboard` | Link para o dashboard web |
| `@Frndsgrpbot github` | Link para o repositório |
| `@Frndsgrpbot ajuda` | Mostra esta lista de comandos |

---

## 💻 Comandos do Agente Python (Servidor Local)

### Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/rebelpaulo/lisboa-real-estate-ai.git
cd lisboa-real-estate-ai/agent

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt
playwright install chromium
```

### Comandos Principais

```bash
# Buscar oportunidades numa zona
python main.py --search lisboa --typology t2 --min-score 60

# Buscar com filtros completos
python main.py --search cascais --typology t3 --min-score 50 --category A --min-days 180

# Ver estatísticas da base de dados
python main.py --stats

# Gerar relatório em Markdown
python main.py --report --output relatorio.md

# Sincronizar dados com dashboard
python main.py --sync

# Modo daemon - atualização automática a cada hora
python main.py --daemon --interval 3600
```

### Opções de Linha de Comando

| Flag | Descrição | Exemplo |
|------|-----------|---------|
| `--search LOCAL` | Localização para busca | `--search "lisboa"` |
| `--typology TIPO` | Tipologia (t0,t1,t2,t3,t4,t5,moradia) | `--typology t2` |
| `--min-score N` | Score mínimo (0-100) | `--min-score 60` |
| `--category CAT` | Categoria (A,B,C,D) | `--category A` |
| `--min-days N` | Mínimo dias no mercado | `--min-days 180` |
| `--max-days N` | Máximo dias no mercado | `--max-days 365` |
| `--min-price N` | Preço mínimo | `--min-price 200000` |
| `--max-price N` | Preço máximo | `--max-price 500000` |
| `--report` | Gera relatório markdown | `--report` |
| `--output FILE` | Ficheiro de saída | `--output report.md` |
| `--sync` | Sincroniza com dashboard | `--sync` |
| `--daemon` | Modo contínuo | `--daemon` |
| `--interval SEG` | Intervalo entre atualizações | `--interval 3600` |
| `--stats` | Mostra estatísticas | `--stats` |

---

## 📊 Categorias de Oportunidade

| Categoria | Emoji | Descrição | Critérios |
|-----------|-------|-----------|-----------|
| **A** | 🔴 | Ativo Estagnado | ≥180 dias, ≥2 reduções, ≥10% desconto |
| **B** | 🟡 | Preço Agressivo | ≤30 dias, ≥12% abaixo da média |
| **C** | 🟢 | Potencial Intervenção | Preço baixo + drivers valorização |
| **D** | 🔵 | Oportunidade Fundamentada | Casos especiais com análise |

---

## 🚀 Dashboard Web

### Desenvolvimento Local
```bash
cd lisboa-real-estate-ai/dashboard
npm install
npm run dev
# Abre http://localhost:5173
```

### Build para Produção
```bash
npm run build
# Output em dist/
```

---

## 📝 Exemplos de Uso

### Exemplo 1: Análise rápida
```
@Frndsgrpbot analisa https://www.idealista.pt/imovel/12345678/
```

### Exemplo 2: Oportunidades em Belém
```
@Frndsgrpbot oportunidades belém
```

### Exemplo 3: T2s estagnados há mais de 6 meses
```
@Frndsgrpbot categoria A
@Frndsgrpbot tipologia T2
@Frndsgrpbot tempo 180
```

### Exemplo 4: Preços em Cascais
```
@Frndsgrpbot mercado cascais
```

---

## ⚠️ Notas Importantes

1. **Comandos no Telegram** - Requerem que o agente Python esteja a correr num servidor com acesso à internet

2. **Scraping** - Os portais (Idealista, etc.) têm proteções anti-bot. O agente usa técnicas de stealth, mas pode precisar de ajustes

3. **Dados** - O sistema funciona com dados mock para demonstração. Para dados reais, é necessário executar o scraper

4. **GitHub** - Código fonte: https://github.com/rebelpaulo/lisboa-real-estate-ai

---

*Última atualização: 2025-02-17*
