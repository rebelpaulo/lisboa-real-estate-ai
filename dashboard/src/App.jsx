import React, { useState, useMemo, useEffect } from 'react';
import { 
  Building2, MapPin, Euro, TrendingUp, Clock, Filter, 
  Grid3X3, List, Bell, Search, ChevronDown, BarChart3,
  Home, PieChart, ArrowUpRight, ArrowDownRight, Star,
  Target, Zap, Eye, Heart, Share2, Download, Settings
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart as RePieChart, Pie, Cell } from 'recharts';
import PropertyModal from './components/PropertyModal';
import { realProperties, realMarketTrends, realPriceDistribution } from './data/realData';

// Carregar dados reais ou mock
const loadProperties = async () => {
  try {
    const response = await fetch('/data/properties.json');
    const data = await response.json();
    return data.properties || [];
  } catch (e) {
    // Fallback para mock data
    return [
      {
        id: '1',
        title: 'T2 em Leilão - Lisboa, Benfica',
        location: 'Benfica',
        parish: 'Benfica',
        price: 145000,
        originalPrice: 165000,
        area: 75,
        typology: 'T2',
        bedrooms: 2,
        bathrooms: 1,
        category: 'A',
        opportunityScore: 72,
        daysOnMarket: 45,
        priceDrops: 1,
        vsMarket: -12,
        images: ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'],
        source: 'leilosoc.com',
        url: 'https://www.leilosoc.com/pt/leiloes/',
        description: 'Apartamento T2 para renovação total. Excelente oportunidade de investimento.',
        estado: 'Em Leilão',
        dataLeilao: '2025-03-15',
        contacto: 'leilosoc@email.pt',
        notas: 'Necessita obras de renovação',
        precoM2: 1933
      }
    ];
  }
};

// ============================================
// DESIGN SYSTEM - Cores e Estilos
// ============================================
const colors = {
  primary: '#3B82F6',
  primaryDark: '#1D4ED8',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  purple: '#8B5CF6',
  
  // Categorias
  catA: '#EF4444', // Estagnado - Vermelho
  catB: '#F59E0B', // Preço Agressivo - Laranja
  catC: '#10B981', // Intervenção - Verde
  catD: '#3B82F6', // Fundamentada - Azul
  
  // Backgrounds
  bgDark: '#0F172A',
  bgCard: '#1E293B',
  bgElevated: '#334155',
  
  // Texto
  textPrimary: '#F8FAFC',
  textSecondary: '#94A3B8',
  textMuted: '#64748B'
};

// ============================================
// COMPONENTE: Header Moderno
// ============================================
const Header = ({ activeTab, setActiveTab, notifications, onSearch }) => {
  const [searchFocused, setSearchFocused] = useState(false);
  
  const tabs = [
    { id: 'opportunities', label: 'Oportunidades', icon: Target },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'portfolio', label: 'Portfolio', icon: PieChart },
    { id: 'alerts', label: 'Alertas', icon: Bell },
  ];

  return (
    <header className="header-modern">
      <div className="header-left">
        <div className="logo">
          <Building2 className="logo-icon" />
          <span className="logo-text">Lisboa<span className="logo-accent">AI</span></span>
        </div>
        
        <nav className="nav-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={18} />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>
      
      <div className="header-right">
        <div className={`search-box ${searchFocused ? 'focused' : ''}`}>
          <Search size={18} />
          <input
            type="text"
            placeholder="Pesquisar imóveis, zonas..."
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
            onChange={(e) => onSearch(e.target.value)}
          />
        </div>
        
        <button className="icon-btn notification-btn">
          <Bell size={20} />
          {notifications > 0 && <span className="badge">{notifications}</span>}
        </button>
        
        <button className="icon-btn">
          <Settings size={20} />
        </button>
      </div>
    </header>
  );
};

// ============================================
// COMPONENTE: KPI Cards
// ============================================
const KPICards = ({ properties }) => {
  const stats = useMemo(() => {
    const total = properties.length;
    const avgPrice = properties.reduce((a, p) => a + p.price, 0) / total;
    const avgScore = properties.reduce((a, p) => a + p.opportunityScore, 0) / total;
    const highOpportunities = properties.filter(p => p.opportunityScore >= 70).length;
    const categoryA = properties.filter(p => p.category === 'A').length;
    
    return [
      { 
        label: 'Imóveis Analisados', 
        value: total, 
        change: '+12%', 
        trend: 'up',
        icon: Building2,
        color: colors.primary 
      },
      { 
        label: 'Preço Médio', 
        value: `€${(avgPrice / 1000).toFixed(0)}k`, 
        change: '-3.2%', 
        trend: 'down',
        icon: Euro,
        color: colors.success 
      },
      { 
        label: 'Score Médio', 
        value: avgScore.toFixed(1), 
        change: '+5.4%', 
        trend: 'up',
        icon: Star,
        color: colors.warning 
      },
      { 
        label: 'Oportunidades A', 
        value: categoryA, 
        change: '+8%', 
        trend: 'up',
        icon: Target,
        color: colors.danger 
      },
    ];
  }, [properties]);

  return (
    <div className="kpi-grid">
      {stats.map((stat, i) => (
        <div key={i} className="kpi-card">
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: `${stat.color}20`, color: stat.color }}>
              <stat.icon size={20} />
            </div>
            <div className={`kpi-trend ${stat.trend}`}>
              {stat.trend === 'up' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
              <span>{stat.change}</span>
            </div>
          </div>
          <div className="kpi-value">{stat.value}</div>
          <div className="kpi-label">{stat.label}</div>
        </div>
      ))}
    </div>
  );
};

// ============================================
// COMPONENTE: Filtros Avançados
// ============================================
const AdvancedFilters = ({ filters, setFilters, onApply }) => {
  const [expanded, setExpanded] = useState(false);
  
  const categories = [
    { id: 'A', label: 'Estagnado', color: colors.catA, desc: '≥180 dias, ≥2 reduções' },
    { id: 'B', label: 'Preço Agressivo', color: colors.catB, desc: '≤30 dias, ≥12% abaixo' },
    { id: 'C', label: 'Intervenção', color: colors.catC, desc: 'Potencial valorização' },
    { id: 'D', label: 'Fundamentada', color: colors.catD, desc: 'Análise detalhada' },
  ];

  const timeFilters = [
    { label: 'Todos', min: null, max: null },
    { label: '> 3 meses', min: 90, max: null },
    { label: '> 6 meses', min: 180, max: null },
    { label: '> 1 ano', min: 365, max: null },
  ];

  return (
    <div className="filters-panel">
      <div className="filters-header" onClick={() => setExpanded(!expanded)}>
        <div className="filters-title">
          <Filter size={18} />
          <span>Filtros Avançados</span>
        </div>
        <ChevronDown size={18} className={`chevron ${expanded ? 'open' : ''}`} />
      </div>
      
      {expanded && (
        <div className="filters-content">
          {/* Categorias */}
          <div className="filter-section">
            <label>Categoria de Oportunidade</label>
            <div className="category-chips">
              {categories.map(cat => (
                <button
                  key={cat.id}
                  className={`category-chip ${filters.category === cat.id ? 'active' : ''}`}
                  style={{ 
                    '--cat-color': cat.color,
                    borderColor: filters.category === cat.id ? cat.color : 'transparent'
                  }}
                  onClick={() => setFilters(f => ({ ...f, category: f.category === cat.id ? '' : cat.id }))}
                >
                  <span className="cat-dot" style={{ background: cat.color }} />
                  <div className="cat-info">
                    <span className="cat-label">{cat.label}</span>
                    <span className="cat-desc">{cat.desc}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Score */}
          <div className="filter-section">
            <label>Score Mínimo: <strong>{filters.minScore}</strong></label>
            <input
              type="range"
              min="0"
              max="100"
              value={filters.minScore}
              onChange={(e) => setFilters(f => ({ ...f, minScore: parseInt(e.target.value) }))}
              className="score-slider"
            />
            <div className="score-labels">
              <span>0</span>
              <span>50</span>
              <span>100</span>
            </div>
          </div>

          {/* Tempo no Mercado */}
          <div className="filter-section">
            <label>Tempo no Mercado</label>
            <div className="time-chips">
              {timeFilters.map((tf, i) => (
                <button
                  key={i}
                  className={`time-chip ${filters.minDays === tf.min ? 'active' : ''}`}
                  onClick={() => setFilters(f => ({ ...f, minDays: tf.min, maxDays: tf.max }))}
                >
                  {tf.label}
                </button>
              ))}
            </div>
          </div>

          {/* Preço */}
          <div className="filter-section price-range">
            <label>Faixa de Preço</label>
            <div className="price-inputs">
              <input
                type="number"
                placeholder="Min €"
                value={filters.minPrice || ''}
                onChange={(e) => setFilters(f => ({ ...f, minPrice: e.target.value ? parseInt(e.target.value) : null }))}
              />
              <span>até</span>
              <input
                type="number"
                placeholder="Max €"
                value={filters.maxPrice || ''}
                onChange={(e) => setFilters(f => ({ ...f, maxPrice: e.target.value ? parseInt(e.target.value) : null }))}
              />
            </div>
          </div>

          {/* Tipologia */}
          <div className="filter-section">
            <label>Tipologia</label>
            <select
              value={filters.typology}
              onChange={(e) => setFilters(f => ({ ...f, typology: e.target.value }))}
            >
              <option value="">Todas</option>
              <option value="T0">T0</option>
              <option value="T1">T1</option>
              <option value="T2">T2</option>
              <option value="T3">T3</option>
              <option value="T4">T4</option>
              <option value="T5+">T5+</option>
              <option value="Moradia">Moradia</option>
            </select>
          </div>

          <button className="apply-filters-btn" onClick={onApply}>
            <Zap size={16} />
            Aplicar Filtros
          </button>
        </div>
      )}
    </div>
  );
};

// ============================================
// COMPONENTE: Property Card Moderno
// ============================================
const PropertyCard = ({ property, viewMode }) => {
  const categoryColors = {
    'A': colors.catA,
    'B': colors.catB,
    'C': colors.catC,
    'D': colors.catD
  };

  const categoryLabels = {
    'A': 'Estagnado',
    'B': 'Preço Agressivo',
    'C': 'Intervenção',
    'D': 'Fundamentada'
  };

  const getScoreColor = (score) => {
    if (score >= 80) return colors.success;
    if (score >= 60) return colors.warning;
    if (score >= 40) return colors.primary;
    return colors.textMuted;
  };

  if (viewMode === 'list') {
    return (
      <div className="property-row">
        <div className="row-image">
          <img src={property.images[0]} alt={property.title} />
          <span className="row-category" style={{ background: categoryColors[property.category] }}>
            {property.category}
          </span>
        </div>
        <div className="row-content">
          <h3>{property.title}</h3>
          <div className="row-location">
            <MapPin size={14} />
            <span>{property.location}</span>
          </div>
          <div className="row-features">
            <span>{property.typology}</span>
            <span>•</span>
            <span>{property.area} m²</span>
            <span>•</span>
            <span>{property.bedrooms} quartos</span>
          </div>
        </div>
        <div className="row-metrics">
          <div className="row-price">€{property.price.toLocaleString()}</div>
          <div className="row-price-m2">€{Math.round(property.price / property.area)}/m²</div>
        </div>
        <div className="row-score" style={{ color: getScoreColor(property.opportunityScore) }}>
          <div className="score-circle">
            <svg viewBox="0 0 36 36">
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#334155"
                strokeWidth="3"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke={getScoreColor(property.opportunityScore)}
                strokeWidth="3"
                strokeDasharray={`${property.opportunityScore}, 100`}
              />
            </svg>
            <span>{property.opportunityScore}</span>
          </div>
        </div>
        <div className="row-actions">
          <button className="action-btn"><Eye size={18} /></button>
          <button className="action-btn"><Heart size={18} /></button>
          <button className="action-btn"><Share2 size={18} /></button>
        </div>
      </div>
    );
  }

  return (
    <div className="property-card-modern">
      <div className="card-image">
        <img src={property.images[0]} alt={property.title} />
        <div className="card-badges">
          <span className="badge-category" style={{ background: categoryColors[property.category] }}>
            {property.category} - {categoryLabels[property.category]}
          </span>
          {property.priceDrops > 0 && (
            <span className="badge-drops">
              <TrendingUp size={12} />
              {property.priceDrops} reduções
            </span>
          )}
        </div>
        <button className="card-favorite">
          <Heart size={18} />
        </button>
      </div>
      
      <div className="card-content">
        <div className="card-header">
          <h3>{property.title}</h3>
          <div className="card-score" style={{ color: getScoreColor(property.opportunityScore) }}>
            <Zap size={14} />
            <span>{property.opportunityScore}</span>
          </div>
        </div>
        
        <div className="card-location">
          <MapPin size={14} />
          <span>{property.location}</span>
        </div>
        
        <div className="card-features">
          <div className="feature">
            <Home size={14} />
            <span>{property.typology}</span>
          </div>
          <div className="feature">
            <span className="feature-icon">📐</span>
            <span>{property.area} m²</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🛏️</span>
            <span>{property.bedrooms} qts</span>
          </div>
        </div>
        
        <div className="card-market">
          <div className="market-item">
            <span className="market-label">Preço/m²</span>
            <span className="market-value">€{Math.round(property.price / property.area)}</span>
          </div>
          <div className="market-item">
            <span className="market-label">vs Mercado</span>
            <span className={`market-value ${property.vsMarket < 0 ? 'negative' : 'positive'}`}>
              {property.vsMarket > 0 ? '+' : ''}{property.vsMarket}%
            </span>
          </div>
          <div className="market-item">
            <span className="market-label">Tempo</span>
            <span className="market-value">{property.daysOnMarket} dias</span>
          </div>
        </div>
        
        <div className="card-footer">
          <div className="card-price">
            <span className="price-value">€{property.price.toLocaleString()}</span>
            {property.originalPrice && (
              <span className="price-original">
                €{property.originalPrice.toLocaleString()}
              </span>
            )}
          </div>
          <button className="card-view-btn">
            <Eye size={16} />
            Ver
          </button>
        </div>
      </div>
    </div>
  );
};

// ============================================
// COMPONENTE: Analytics Dashboard
// ============================================
const AnalyticsPanel = () => {
  return (
    <div className="analytics-panel">
      <div className="analytics-grid">
        <div className="analytics-card">
          <h4>Tendência de Preços</h4>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={realMarketTrends}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors.primary} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={colors.primary} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="month" stroke="#64748B" fontSize={12} />
              <YAxis stroke="#64748B" fontSize={12} />
              <Tooltip 
                contentStyle={{ background: colors.bgCard, border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: colors.textSecondary }}
              />
              <Area type="monotone" dataKey="avgPrice" stroke={colors.primary} fillOpacity={1} fill="url(#colorPrice)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        <div className="analytics-card">
          <h4>Distribuição por Categoria</h4>
          <ResponsiveContainer width="100%" height={200}>
            <RePieChart>
              <Pie
                data={realPriceDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {realPriceDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={[colors.catA, colors.catB, colors.catC, colors.catD][index]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: colors.bgCard, border: 'none', borderRadius: '8px' }} />
            </RePieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// ============================================
// COMPONENTE PRINCIPAL: App
// ============================================
function App() {
  const [activeTab, setActiveTab] = useState('opportunities');
  const [viewMode, setViewMode] = useState('grid');
  const [filters, setFilters] = useState({
    category: '',
    minScore: 0,
    minDays: null,
    maxDays: null,
    minPrice: null,
    maxPrice: null,
    typology: '',
    parish: ''
  });
  const [searchQuery, setSearchQuery] = useState('');

  const filteredProperties = useMemo(() => {
    return realProperties.filter(p => {
      if (filters.category && p.category !== filters.category) return false;
      if (p.opportunityScore < filters.minScore) return false;
      if (filters.minDays && p.daysOnMarket < filters.minDays) return false;
      if (filters.maxDays && p.daysOnMarket > filters.maxDays) return false;
      if (filters.minPrice && p.price < filters.minPrice) return false;
      if (filters.maxPrice && p.price > filters.maxPrice) return false;
      if (filters.typology && p.typology !== filters.typology) return false;
      if (searchQuery && !p.title.toLowerCase().includes(searchQuery.toLowerCase()) && 
          !p.location.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [filters, searchQuery]);

  return (
    <div className="app-modern">
      <Header 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        notifications={3}
        onSearch={setSearchQuery}
      />
      
      <main className="main-content">
        {activeTab === 'opportunities' && (
          <>
            <KPICards properties={filteredProperties} />
            
            <AdvancedFilters 
              filters={filters} 
              setFilters={setFilters}
              onApply={() => {}}
            />
            
            <div className="toolbar">
              <div className="results-count">
                <strong>{filteredProperties.length}</strong> imóveis encontrados
              </div>
              <div className="view-toggle">
                <button 
                  className={viewMode === 'grid' ? 'active' : ''}
                  onClick={() => setViewMode('grid')}
                >
                  <Grid3X3 size={18} />
                </button>
                <button 
                  className={viewMode === 'list' ? 'active' : ''}
                  onClick={() => setViewMode('list')}
                >
                  <List size={18} />
                </button>
              </div>
            </div>
            
            <div className={`properties-container ${viewMode}`}>
              {filteredProperties.map(property => (
                <PropertyCard 
                  key={property.id} 
                  property={property}
                  viewMode={viewMode}
                />
              ))}
            </div>
          </>
        )}
        
        {activeTab === 'analytics' && <AnalyticsPanel />}
        
        {activeTab === 'portfolio' && (
          <div className="placeholder-panel">
            <PieChart size={48} />
            <h3>Portfolio em breve</h3>
            <p>Gestão de portfolio e tracking de investimentos.</p>
          </div>
        )}
        
        {activeTab === 'alerts' && (
          <div className="placeholder-panel">
            <Bell size={48} />
            <h3>Alertas em breve</h3>
            <p>Configure alertas para novas oportunidades.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
