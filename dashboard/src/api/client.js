// API client para o dashboard

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const GITHUB_RAW_URL = 'https://raw.githubusercontent.com';

class RealEstateAPI {
  constructor() {
    this.useLocalData = true; // Fallback para dados locais
    this.githubRepo = import.meta.env.VITE_GITHUB_REPO || 'username/lisboa-real-estate-data';
  }

  // Buscar propriedades
  async getProperties(filters = {}) {
    try {
      // Tentar dados locais primeiro
      const localData = localStorage.getItem('properties_cache');
      if (localData) {
        const parsed = JSON.parse(localData);
        return this.applyFilters(parsed.properties || [], filters);
      }

      // Fallback para mock data
      const { mockProperties } = await import('./mockData.js');
      return this.applyFilters(mockProperties, filters);
    } catch (error) {
      console.error('Erro ao carregar propriedades:', error);
      return [];
    }
  }

  // Buscar estatísticas
  async getStats() {
    try {
      const localStats = localStorage.getItem('stats_cache');
      if (localStats) {
        return JSON.parse(localStats);
      }

      const { mockStats } = await import('./mockData.js');
      return mockStats;
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
      return {};
    }
  }

  // Buscar do GitHub
  async fetchFromGitHub() {
    try {
      const response = await fetch(
        `${GITHUB_RAW_URL}/${this.githubRepo}/main/data/properties_latest.json`
      );
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('properties_cache', JSON.stringify(data));
        localStorage.setItem('last_sync', new Date().toISOString());
        return data;
      }
    } catch (error) {
      console.log('GitHub fetch falhou, usando dados locais');
    }
    return null;
  }

  // Aplicar filtros
  applyFilters(properties, filters) {
    return properties.filter(prop => {
      if (filters.category && prop.opportunityCategory !== filters.category) {
        return false;
      }
      if (filters.minScore && prop.opportunityScore < filters.minScore) {
        return false;
      }
      if (filters.minDays && prop.daysOnMarket < filters.minDays) {
        return false;
      }
      if (filters.maxDays && prop.daysOnMarket > filters.maxDays) {
        return false;
      }
      if (filters.typology && prop.typology !== filters.typology) {
        return false;
      }
      if (filters.parish && !prop.parish.toLowerCase().includes(filters.parish.toLowerCase())) {
        return false;
      }
      if (filters.minPrice && prop.price < filters.minPrice) {
        return false;
      }
      if (filters.maxPrice && prop.price > filters.maxPrice) {
        return false;
      }
      return true;
    });
  }

  // Forçar atualização
  async refresh() {
    const data = await this.fetchFromGitHub();
    if (data) {
      return data.properties || [];
    }
    return [];
  }

  // Última sincronização
  getLastSync() {
    return localStorage.getItem('last_sync');
  }
}

export const api = new RealEstateAPI();
