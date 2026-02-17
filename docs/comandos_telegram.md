# Comandos do Jarbas - Grupo Imobiliário

## 🏠 Comandos de Análise

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `/analisa [URL]` | Analisa um imóvel específico | `/analisa https://idealista.pt/imovel/12345` |
| `/oportunidades` | Lista top 10 oportunidades | `/oportunidades` |
| `/oportunidades [zona]` | Oportunidades numa zona | `/oportunidades belém` |
| `/score [URL]` | Calcula score de oportunidade | `/score https://...` |

## 📊 Filtros

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `/categoria [A/B/C/D]` | Filtra por categoria | `/categoria A` |
| `/tipologia [T0-T5/moradia]` | Filtra por tipologia | `/tipologia T2` |
| `/preco [min] [max]` | Filtra por preço | `/preco 200000 400000` |
| `/tempo [dias]` | Imóveis há +X dias no mercado | `/tempo 180` |
| `/zona [freguesia]` | Filtra por zona | `/zona alfama` |

## 📈 Dados de Mercado

| Comando | Descrição |
|---------|-----------|
| `/mercado [zona]` | Média de preços numa zona |
| `/tendencia [zona]` | Tendência de preços (6m/12m) |
| `/comparaveis [URL]` | Mostra 6-12 comparáveis |

## 🔔 Alertas

| Comando | Descrição |
|---------|-----------|
| `/alerta [zona] [preço_max]` | Cria alerta para novos imóveis |
| `/alertas` | Lista alertas ativos |
| `/remover_alerta [id]` | Remove um alerta |

## 📋 Relatórios

| Comando | Descrição |
|---------|-----------|
| `/relatorio` | Gera relatório do dia |
| `/relatorio_semanal` | Relatório da semana |
| `/exportar` | Exporta dados (CSV/JSON) |

## ℹ️ Ajuda

| Comando | Descrição |
|---------|-----------|
| `/ajuda` | Mostra esta lista |
| `/status` | Verifica se o sistema está online |
| `/dashboard` | Link para o dashboard web |

---

**Nota:** Alguns comandos requerem que o agente Python esteja a correr no servidor.
