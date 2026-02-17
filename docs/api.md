# API Endpoints (Futuro)

## REST API

### GET /api/properties
Lista imóveis com filtros

**Query Parameters:**
- `category` - A, B, C, D
- `min_score` - Score mínimo (0-100)
- `min_days` - Mínimo dias no mercado
- `max_days` - Máximo dias no mercado
- `typology` - T0, T1, T2, T3, T4, T5+
- `parish` - Nome da freguesia
- `limit` - Limite de resultados (default: 50)
- `offset` - Offset para paginação

**Response:**
```json
{
  "total": 156,
  "properties": [
    {
      "id": "idealista_12345",
      "title": "T2 em Belém",
      "price": 285000,
      "opportunity_score": 87,
      "opportunity_category": "A",
      ...
    }
  ]
}
```

### GET /api/properties/:id
Detalhes de um imóvel específico

### GET /api/stats
Estatísticas gerais

### GET /api/market-data/:parish/:typology
Dados de mercado para uma zona

### POST /api/alerts/mark-read
Marcar alertas como lidos

## WebSocket

### ws://localhost:8080/ws
Stream em tempo real de novas oportunidades

**Eventos:**
- `new_property` - Novo imóvel detectado
- `price_drop` - Redução de preço
- `opportunity_alert` - Nova oportunidade categoria A/B

## Integração com Dashboard

O dashboard consome a API para:
1. Listar imóveis com filtros
2. Mostrar estatísticas
3. Atualizações em tempo real (WebSocket)
4. Exportar dados
