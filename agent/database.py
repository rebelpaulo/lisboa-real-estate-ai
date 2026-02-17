"""
Database - Lisboa Real Estate AI
Gestão da base de dados SQLite
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

logger = logging.getLogger(__name__)

class PropertyDatabase:
    """Base de dados para imóveis"""
    
    def __init__(self, db_path: str = "../data/listings.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.cursor = None
        self._init_db()
    
    def _init_db(self):
        """Inicializa a base de dados e tabelas"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Tabela de imóveis
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                portal TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                price REAL,
                price_history TEXT,  -- JSON array
                area_m2 REAL,
                typology TEXT,
                location TEXT,
                parish TEXT,
                municipality TEXT,
                district TEXT DEFAULT 'Lisboa',
                description TEXT,
                features TEXT,  -- JSON array
                photos TEXT,  -- JSON array
                contact TEXT,  -- JSON object
                days_on_market INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price_per_m2 REAL,
                opportunity_score INTEGER DEFAULT 0,
                opportunity_category TEXT,
                status TEXT DEFAULT 'active',  -- active, sold, inactive
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de histórico de preços
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id TEXT NOT NULL,
                price REAL NOT NULL,
                change_percent REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')
        
        # Tabela de dados de mercado
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parish TEXT NOT NULL,
                municipality TEXT NOT NULL,
                typology TEXT NOT NULL,
                avg_price_m2 REAL,
                median_price_m2 REAL,
                min_price_m2 REAL,
                max_price_m2 REAL,
                sample_size INTEGER,
                trend_6m REAL,
                trend_12m REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(parish, municipality, typology, recorded_at)
            )
        ''')
        
        # Tabela de alertas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,  -- price_drop, new_opportunity, etc.
                message TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')
        
        # Índices para performance
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_properties_score 
            ON properties(opportunity_score DESC)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_properties_category 
            ON properties(opportunity_category)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_properties_location 
            ON properties(parish, municipality)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_properties_status 
            ON properties(status)
        ''')
        
        self.conn.commit()
        logger.info(f"Base de dados inicializada: {self.db_path}")
    
    def save_property(self, property_data: Dict) -> bool:
        """
        Guarda ou atualiza um imóvel
        
        Args:
            property_data: Dict com dados do imóvel
            
        Returns:
            True se foi inserido, False se foi atualizado
        """
        prop_id = property_data.get('id')
        
        # Verificar se já existe
        self.cursor.execute('SELECT id, price FROM properties WHERE id = ?', (prop_id,))
        existing = self.cursor.fetchone()
        
        # Preparar dados
        fields = [
            'id', 'portal', 'url', 'title', 'price', 'price_history',
            'area_m2', 'typology', 'location', 'parish', 'municipality',
            'district', 'description', 'features', 'photos', 'contact',
            'days_on_market', 'price_per_m2', 'opportunity_score',
            'opportunity_category', 'status'
        ]
        
        values = []
        for field in fields:
            val = property_data.get(field)
            if isinstance(val, (list, dict)):
                val = json.dumps(val, ensure_ascii=False)
            values.append(val)
        
        if existing:
            # Atualizar
            old_price = existing['price']
            new_price = property_data.get('price')
            
            # Registrar mudança de preço
            if old_price and new_price and old_price != new_price:
                change_pct = ((new_price - old_price) / old_price) * 100
                self.cursor.execute('''
                    INSERT INTO price_history (property_id, price, change_percent)
                    VALUES (?, ?, ?)
                ''', (prop_id, new_price, change_pct))
            
            # Update
            set_clause = ', '.join([f"{f} = ?" for f in fields[1:]])
            set_clause += ', updated_at = CURRENT_TIMESTAMP, last_seen = CURRENT_TIMESTAMP'
            
            self.cursor.execute(f'''
                UPDATE properties SET {set_clause} WHERE id = ?
            ''', values[1:] + [prop_id])
            
            self.conn.commit()
            return False
        
        else:
            # Inserir novo
            placeholders = ', '.join(['?' for _ in fields])
            
            self.cursor.execute(f'''
                INSERT INTO properties ({', '.join(fields)})
                VALUES ({placeholders})
            ''', values)
            
            # Registrar preço inicial no histórico
            if property_data.get('price'):
                self.cursor.execute('''
                    INSERT INTO price_history (property_id, price, change_percent)
                    VALUES (?, ?, ?)
                ''', (prop_id, property_data['price'], 0))
            
            self.conn.commit()
            return True
    
    def get_property(self, prop_id: str) -> Optional[Dict]:
        """Obtém um imóvel pelo ID"""
        self.cursor.execute('SELECT * FROM properties WHERE id = ?', (prop_id,))
        row = self.cursor.fetchone()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_properties(self, 
                      min_score: Optional[int] = None,
                      category: Optional[str] = None,
                      parish: Optional[str] = None,
                      typology: Optional[str] = None,
                      min_days: Optional[int] = None,
                      max_days: Optional[int] = None,
                      status: str = 'active',
                      limit: int = 100,
                      offset: int = 0) -> List[Dict]:
        """
        Busca imóveis com filtros
        """
        conditions = ['status = ?']
        params = [status]
        
        if min_score is not None:
            conditions.append('opportunity_score >= ?')
            params.append(min_score)
        
        if category:
            conditions.append('opportunity_category = ?')
            params.append(category)
        
        if parish:
            conditions.append('parish LIKE ?')
            params.append(f'%{parish}%')
        
        if typology:
            conditions.append('typology = ?')
            params.append(typology)
        
        if min_days is not None:
            conditions.append('days_on_market >= ?')
            params.append(min_days)
        
        if max_days is not None:
            conditions.append('days_on_market <= ?')
            params.append(max_days)
        
        where_clause = ' AND '.join(conditions)
        
        self.cursor.execute(f'''
            SELECT * FROM properties 
            WHERE {where_clause}
            ORDER BY opportunity_score DESC, created_at DESC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])
        
        rows = self.cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def get_price_history(self, prop_id: str) -> List[Dict]:
        """Obtém histórico de preços de um imóvel"""
        self.cursor.execute('''
            SELECT * FROM price_history 
            WHERE property_id = ? 
            ORDER BY recorded_at ASC
        ''', (prop_id,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def save_market_data(self, data: Dict):
        """Guarda dados de mercado"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO market_data 
            (parish, municipality, typology, avg_price_m2, median_price_m2,
             min_price_m2, max_price_m2, sample_size, trend_6m, trend_12m)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('parish'),
            data.get('municipality'),
            data.get('typology'),
            data.get('avg_price_m2'),
            data.get('median_price_m2'),
            data.get('min_price_m2'),
            data.get('max_price_m2'),
            data.get('sample_size'),
            data.get('trend_6m'),
            data.get('trend_12m')
        ))
        self.conn.commit()
    
    def get_market_data(self, parish: str, typology: str) -> Optional[Dict]:
        """Obtém dados de mercado mais recentes"""
        self.cursor.execute('''
            SELECT * FROM market_data 
            WHERE parish = ? AND typology = ?
            ORDER BY recorded_at DESC
            LIMIT 1
        ''', (parish, typology))
        
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def create_alert(self, prop_id: str, alert_type: str, message: str):
        """Cria um novo alerta"""
        self.cursor.execute('''
            INSERT INTO alerts (property_id, alert_type, message)
            VALUES (?, ?, ?)
        ''', (prop_id, alert_type, message))
        self.conn.commit()
    
    def get_alerts(self, unread_only: bool = False, limit: int = 50) -> List[Dict]:
        """Obtém alertas"""
        if unread_only:
            self.cursor.execute('''
                SELECT a.*, p.title, p.url 
                FROM alerts a
                JOIN properties p ON a.property_id = p.id
                WHERE a.is_read = 0
                ORDER BY a.created_at DESC
                LIMIT ?
            ''', (limit,))
        else:
            self.cursor.execute('''
                SELECT a.*, p.title, p.url 
                FROM alerts a
                JOIN properties p ON a.property_id = p.id
                ORDER BY a.created_at DESC
                LIMIT ?
            ''', (limit,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def mark_alert_read(self, alert_id: int):
        """Marca alerta como lido"""
        self.cursor.execute('''
            UPDATE alerts SET is_read = 1 WHERE id = ?
        ''', (alert_id,))
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        """Obtém estatísticas da base de dados"""
        stats = {}
        
        # Total de imóveis
        self.cursor.execute('SELECT COUNT(*) FROM properties WHERE status = "active"')
        stats['total_properties'] = self.cursor.fetchone()[0]
        
        # Por categoria
        self.cursor.execute('''
            SELECT opportunity_category, COUNT(*) 
            FROM properties 
            WHERE status = 'active'
            GROUP BY opportunity_category
        ''')
        stats['by_category'] = {row[0] or 'N/A': row[1] for row in self.cursor.fetchall()}
        
        # Por portal
        self.cursor.execute('''
            SELECT portal, COUNT(*) 
            FROM properties 
            WHERE status = 'active'
            GROUP BY portal
        ''')
        stats['by_portal'] = dict(self.cursor.fetchall())
        
        # Alertas não lidos
        self.cursor.execute('SELECT COUNT(*) FROM alerts WHERE is_read = 0')
        stats['unread_alerts'] = self.cursor.fetchone()[0]
        
        return stats
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Converte row SQLite para dict"""
        result = dict(row)
        
        # Parse JSON fields
        for field in ['price_history', 'features', 'photos', 'contact']:
            if result.get(field) and isinstance(result[field], str):
                try:
                    result[field] = json.loads(result[field])
                except json.JSONDecodeError:
                    result[field] = []
        
        return result
    
    def close(self):
        """Fecha conexão com a base de dados"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Teste da base de dados"""
    with PropertyDatabase() as db:
        stats = db.get_stats()
        logger.info(f"Estatísticas: {stats}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
