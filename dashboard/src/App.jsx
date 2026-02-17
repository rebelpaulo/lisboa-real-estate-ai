import React, { useState, useEffect } from 'react'
import { 
  Building2, 
  TrendingUp, 
  Filter, 
  Bell, 
  Search,
  MapPin,
  Euro,
  Clock,
  Star,
  Menu,
  X
} from 'lucide-react'
import PropertyCard from './components/PropertyCard'
import FilterPanel from './components/FilterPanel'
import StatsPanel from './components/StatsPanel'
import { mockProperties, mockStats } from './data/mockData'

function App() {
  const [properties, setProperties] = useState(mockProperties)
  const [filteredProperties, setFilteredProperties] = useState(mockProperties)
  const [stats, setStats] = useState(mockStats)
  const [filters, setFilters] = useState({
    category: '',
    minScore: 0,
    minDays: null,
    maxDays: null,
    typology: '',
    parish: '',
    minPrice: null,
    maxPrice: null,
  })
  const [showFilters, setShowFilters] = useState(false)
  const [viewMode, setViewMode] = useState('grid') // 'grid' | 'list'
  const [selectedProperty, setSelectedProperty] = useState(null)

  // Aplicar filtros
  useEffect(() => {
    let filtered = [...properties]

    if (filters.category) {
      filtered = filtered.filter(p => p.opportunityCategory === filters.category)
    }

    if (filters.minScore > 0) {
      filtered = filtered.filter(p => p.opportunityScore >= filters.minScore)
    }

    if (filters.minDays !== null) {
      filtered = filtered.filter(p => p.daysOnMarket >= filters.minDays)
    }

    if (filters.maxDays !== null) {
      filtered = filtered.filter(p => p.daysOnMarket <= filters.maxDays)
    }

    if (filters.typology) {
      filtered = filtered.filter(p => p.typology === filters.typology)
    }

    if (filters.parish) {
      filtered = filtered.filter(p => 
        p.parish.toLowerCase().includes(filters.parish.toLowerCase())
      )
    }

    if (filters.minPrice !== null) {
      filtered = filtered.filter(p => p.price >= filters.minPrice)
    }

    if (filters.maxPrice !== null) {
      filtered = filtered.filter(p => p.price <= filters.maxPrice)
    }

    setFilteredProperties(filtered)
  }, [filters, properties])

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <Building2 size={28} className="logo-icon" />
              <div>
                <h1>Lisboa Real Estate AI</h1>
                <span className="subtitle">Oportunidades de Investimento</span>
              </div>
            </div>

            <div className="header-actions">
              <button className="btn btn-secondary">
                <Bell size={18} />
                <span className="badge-count">3</span>
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter size={18} />
                Filtros
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Overview */}
      <StatsPanel stats={stats} />

      {/* Main Content */}
      <main className="main">
        <div className="container">
          <div className="main-layout">
            {/* Sidebar Filters */}
            {showFilters && (
              <aside className="sidebar">
                <FilterPanel 
                  filters={filters} 
                  onChange={handleFilterChange}
                  onClose={() => setShowFilters(false)}
                />
              </aside>
            )}

            {/* Property Grid */}
            <div className="content">
              <div className="content-header">
                <div className="results-info">
                  <span className="text-lg font-semibold">
                    {filteredProperties.length} oportunidades
                  </span>
                  <span className="text-secondary">
                    {filteredProperties.length !== properties.length && ` (de ${properties.length} total)`}
                  </span>
                </div>

                <div className="view-toggle">
                  <button 
                    className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                    onClick={() => setViewMode('grid')}
                  >
                    Grid
                  </button>
                  <button 
                    className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                    onClick={() => setViewMode('list')}
                  >
                    Lista
                  </button>
                </div>
              </div>

              <div className={`properties-${viewMode}`}>
                {filteredProperties.map(property => (
                  <PropertyCard 
                    key={property.id}
                    property={property}
                    onClick={() => setSelectedProperty(property)}
                  />
                ))}
              </div>

              {filteredProperties.length === 0 && (
                <div className="empty-state">
                  <Search size={48} className="empty-icon" />
                  <h3>Nenhuma oportunidade encontrada</h3>
                  <p className="text-secondary">
                    Tente ajustar os filtros para ver mais resultados.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p className="text-muted text-sm">
            Lisboa Real Estate AI © 2025 • Dados atualizados em tempo real
          </p>
        </div>
      </footer>

      <style>{`
        .app {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .header {
          background: var(--bg-secondary);
          border-bottom: 1px solid var(--bg-tertiary);
          padding: 16px 0;
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .logo-icon {
          color: var(--primary);
        }

        .logo h1 {
          font-size: 20px;
          font-weight: 700;
        }

        .subtitle {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .header-actions {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .badge-count {
          background: var(--danger);
          color: white;
          font-size: 11px;
          padding: 2px 6px;
          border-radius: 10px;
          margin-left: 4px;
        }

        .main {
          flex: 1;
          padding: 24px 0;
        }

        .main-layout {
          display: grid;
          grid-template-columns: 280px 1fr;
          gap: 24px;
        }

        @media (max-width: 1024px) {
          .main-layout {
            grid-template-columns: 1fr;
          }

          .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: var(--bg-secondary);
            z-index: 200;
            padding: 20px;
            overflow-y: auto;
            box-shadow: var(--shadow-lg);
          }
        }

        .content {
          min-width: 0;
        }

        .content-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .results-info {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .view-toggle {
          display: flex;
          background: var(--bg-secondary);
          border-radius: var(--border-radius);
          padding: 4px;
        }

        .view-btn {
          padding: 6px 12px;
          border: none;
          background: transparent;
          color: var(--text-secondary);
          cursor: pointer;
          border-radius: 4px;
          font-size: 13px;
          transition: all 0.2s;
        }

        .view-btn.active {
          background: var(--primary);
          color: white;
        }

        .properties-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 20px;
        }

        .properties-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
        }

        .empty-icon {
          color: var(--text-muted);
          margin-bottom: 16px;
        }

        .empty-state h3 {
          margin-bottom: 8px;
        }

        .footer {
          background: var(--bg-secondary);
          border-top: 1px solid var(--bg-tertiary);
          padding: 16px 0;
          text-align: center;
        }
      `}</style>
    </div>
  )
}

export default App
