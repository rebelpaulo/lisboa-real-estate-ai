# Configuração do Agente

## Variáveis de Ambiente

Criar ficheiro `.env` na pasta `agent/`:

```env
# Base de dados
DB_PATH=../data/listings.db

# Scraping
SCRAPING_DELAY_MS=1000
MAX_CONCURRENT_REQUESTS=3

# APIs (opcional)
GOOGLE_MAPS_API_KEY=sua_chave_aqui
INE_API_KEY=sua_chave_aqui

# GitHub Bridge (para sincronização)
GITHUB_TOKEN=seu_token_aqui
GITHUB_REPO=username/lisboa-real-estate-data

# Notificações
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id

# Modo
DEBUG=false
LOG_LEVEL=INFO
```

## Instalação

```bash
cd agent
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

pip install -r requirements.txt
playwright install
```

## Execução

```bash
# Modo interativo
python bot.py

# Modo daemon (atualização periódica)
python bot.py --daemon --interval 3600

# Busca manual
python bot.py --search "lisboa" --typology "t2"

# Gerar relatório
python bot.py --report --min-score 60
```

## Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `--search LOCATION` | Busca imóveis numa localização |
| `--typology TIPO` | Filtra por tipologia (t0, t1, t2, etc.) |
| `--min-score N` | Score mínimo de oportunidade |
| `--category CAT` | Categoria (A, B, C, D) |
| `--daemon` | Executa em modo contínuo |
| `--interval SEGUNDOS` | Intervalo entre atualizações |
| `--report` | Gera relatório markdown |
| `--export JSON` | Exporta para JSON |
| `--stats` | Mostra estatísticas |

## Estrutura da Base de Dados

### Tabela `properties`
- Dados dos imóveis + metadados de oportunidade
- Índices: score, categoria, localização

### Tabela `price_history`
- Histórico de alterações de preço
- Permite detetar reduções e calcular tendências

### Tabela `market_data`
- Estatísticas de mercado por zona/tipologia
- Usado para benchmark de preços

### Tabela `alerts`
- Alertas gerados (novas oportunidades, reduções de preço)
- Integração com notificações
