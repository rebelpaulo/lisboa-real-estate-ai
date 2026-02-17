"""
GitHub Bridge - Lisboa Real Estate AI
Sincronização de dados com repositório GitHub
"""

import os
import json
import logging
import base64
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

try:
    import requests
except ImportError:
    pass

logger = logging.getLogger(__name__)

class GitHubBridge:
    """
    Bridge para sincronização com GitHub
    - Exporta dados para JSON
    - Commit para repositório
    - Serve como backend para dashboard
    """
    
    def __init__(self, 
                 token: Optional[str] = None,
                 repo: Optional[str] = None,
                 data_dir: str = "../data"):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.repo = repo or os.getenv('GITHUB_REPO', 'username/lisboa-real-estate-data')
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.api_base = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        } if self.token else {}
    
    def export_properties(self, properties: List[Dict], filename: Optional[str] = None) -> str:
        """
        Exporta imóveis para JSON local
        
        Returns:
            Caminho do ficheiro exportado
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"properties_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        # Adicionar metadados
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'count': len(properties),
            'properties': properties
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exportado {len(properties)} imóveis para {filepath}")
        return str(filepath)
    
    def export_stats(self, stats: Dict, filename: str = "stats.json") -> str:
        """Exporta estatísticas para JSON"""
        filepath = self.data_dir / filename
        
        export_data = {
            'updated_at': datetime.now().isoformat(),
            **stats
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def commit_to_github(self, filepath: str, commit_message: Optional[str] = None) -> bool:
        """
        Commit de um ficheiro para o GitHub
        
        Args:
            filepath: Caminho local do ficheiro
            commit_message: Mensagem do commit
            
        Returns:
            True se sucesso
        """
        if not self.token:
            logger.error("GitHub token não configurado")
            return False
        
        try:
            # Ler conteúdo do ficheiro
            with open(filepath, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            # Nome do ficheiro no repo
            filename = Path(filepath).name
            path_in_repo = f"data/{filename}"
            
            # Verificar se ficheiro já existe
            url = f"{self.api_base}/repos/{self.repo}/contents/{path_in_repo}"
            response = requests.get(url, headers=self.headers)
            
            sha = None
            if response.status_code == 200:
                sha = response.json().get('sha')
            
            # Criar/Atualizar ficheiro
            data = {
                'message': commit_message or f"Update {filename}",
                'content': content,
            }
            if sha:
                data['sha'] = sha
            
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                logger.info(f"Commit bem-sucedido: {path_in_repo}")
                return True
            else:
                logger.error(f"Erro no commit: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao fazer commit: {e}")
            return False
    
    def sync_dashboard_data(self, properties: List[Dict], stats: Dict) -> Dict[str, bool]:
        """
        Sincroniza todos os dados para o dashboard
        
        Returns:
            Dict com status de cada operação
        """
        results = {}
        
        # Exportar propriedades
        props_file = self.export_properties(properties, "properties_latest.json")
        results['properties'] = self.commit_to_github(
            props_file, 
            f"Update properties - {len(properties)} listings"
        )
        
        # Exportar estatísticas
        stats_file = self.export_stats(stats)
        results['stats'] = self.commit_to_github(
            stats_file,
            "Update stats"
        )
        
        # Criar arquivo histórico
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_file = self.export_properties(properties, f"archive/properties_{timestamp}.json")
        results['archive'] = self.commit_to_github(archive_file, f"Archive {timestamp}")
        
        return results
    
    def get_latest_data(self) -> Optional[Dict]:
        """
        Obtém dados mais recentes do GitHub
        
        Returns:
            Dict com propriedades e stats
        """
        if not self.token:
            logger.error("GitHub token não configurado")
            return None
        
        try:
            # Buscar properties_latest.json
            url = f"{self.api_base}/repos/{self.repo}/contents/data/properties_latest.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Erro ao buscar dados: {response.status_code}")
                return None
            
            content = base64.b64decode(response.json()['content'])
            data = json.loads(content)
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados: {e}")
            return None
    
    def create_workflow_dispatch(self, workflow_name: str = "update-data.yml") -> bool:
        """
        Dispara workflow do GitHub Actions
        
        Returns:
            True se sucesso
        """
        if not self.token:
            return False
        
        try:
            url = f"{self.api_base}/repos/{self.repo}/actions/workflows/{workflow_name}/dispatches"
            data = {'ref': 'main'}
            
            response = requests.post(url, headers=self.headers, json=data)
            
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Erro ao disparar workflow: {e}")
            return False


class LocalDataStore:
    """
    Armazenamento local de dados (fallback quando GitHub não configurado)
    """
    
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, key: str, data: Dict):
        """Guarda dados localmente"""
        filepath = self.data_dir / f"{key}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, key: str) -> Optional[Dict]:
        """Carrega dados locais"""
        filepath = self.data_dir / f"{key}.json"
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_keys(self) -> List[str]:
        """Lista todas as chaves disponíveis"""
        return [f.stem for f in self.data_dir.glob("*.json")]


def main():
    """Teste do GitHub Bridge"""
    logging.basicConfig(level=logging.INFO)
    
    # Teste com dados mock
    bridge = GitHubBridge()
    
    mock_properties = [
        {
            'id': 'test_1',
            'title': 'Apartamento T2 Teste',
            'price': 250000,
            'opportunity_score': 75,
        }
    ]
    
    mock_stats = {
        'total_properties': 1,
        'average_score': 75,
    }
    
    # Exportar local
    bridge.export_properties(mock_properties)
    bridge.export_stats(mock_stats)
    
    # Tentar sync com GitHub se token existir
    if bridge.token:
        results = bridge.sync_dashboard_data(mock_properties, mock_stats)
        logger.info(f"Sync results: {results}")
    else:
        logger.info("GitHub token não configurado - dados guardados localmente")

if __name__ == "__main__":
    main()
