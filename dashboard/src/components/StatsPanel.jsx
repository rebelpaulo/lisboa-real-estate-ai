import React from 'react'
import { 
  Building2, 
  TrendingUp, 
  Clock, 
  Star,
  Euro,
  MapPin
} from 'lucide-react'

function StatsPanel({ stats }) {
  const statCards = [
    {
      icon: Building2,
      label: 'Total de Oportunidades',
      value: stats.totalProperties,
      color: 'var(--primary)'
    },
    {
      icon: Star,
      label: 'Score Médio',
      value: `${stats.averageScore}/100`,
      color: 'var(--warning)'
    },
    {
      icon: Clock,
      label: 'Tempo Médio no Mercado',
      value: `${stats.averageDays} dias`,
      color: 'var(--info)'
    },
    {
      icon: Euro,
      label: 'Preço Médio',
      value: `€${stats.averagePrice?.toLocaleString()}`,
      color: 'var(--success)'
    },
  ]

  const categoryDistribution = [
    { category: 'A', count: stats.byCategory?.A || 0, color: '#ef4444', label: 'Estagnado' },
    { category: 'B', count: stats.byCategory?.B || 0, color: '#f59e0b', label: 'Preço Agressivo' },
    { category: 'C', count: stats.byCategory?.C || 0, color: '#10b981', label: 'Intervenção' },
    { category: 'D', count: stats.byCategory?.D || 0, color: '#3b82f6', label: 'Fundamentada' },
  ]

  return (
    <div className="stats-panel">
      <div className="container">
        <div className="stats-grid">
          {statCards.map((card, index) => (
            <div key={index} className="stat-card">
              <div className="stat-icon" style={{ background: `${card.color}20`, color: card.color }}>
                <card.icon size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{card.value}</div>
                <div className="stat-label">{card.label}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="category-distribution">
          <h4>Distribuição por Categoria</h4>
          <div className="distribution-bars">
            {categoryDistribution.map((cat) => {
              const total = categoryDistribution.reduce((sum, c) => sum + c.count, 0)
              const percentage = total > 0 ? (cat.count / total) * 100 : 0
              
              return (
                <div key={cat.category} className="distribution-item">
                  <div className="distribution-header">
                    <span className="dist-label">
                      <span className="dist-dot" style={{ background: cat.color }}></span>
                      {cat.category} - {cat.label}
                    </span>
                    <span className="dist-count">{cat.count}</span>
                  </div>
                  <div className="dist-bar-bg">
                    <div 
                      className="dist-bar-fill"
                      style={{ 
                        width: `${percentage}%`,
                        background: cat.color
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <style>{`
        .stats-panel {
          background: var(--bg-secondary);
          border-bottom: 1px solid var(--bg-tertiary);
          padding: 24px 0;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 20px;
          margin-bottom: 24px;
        }

        @media (max-width: 1024px) {
          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (max-width: 640px) {
          .stats-grid {
            grid-template-columns: 1fr;
          }
        }

        .stat-card {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 20px;
          background: var(--bg-primary);
          border-radius: var(--border-radius);
        }

        .stat-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 48px;
          height: 48px;
          border-radius: 12px;
        }

        .stat-content {
          flex: 1;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 700;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 13px;
          color: var(--text-secondary);
        }

        .category-distribution {
          background: var(--bg-primary);
          border-radius: var(--border-radius);
          padding: 20px;
        }

        .category-distribution h4 {
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 16px;
          color: var(--text-secondary);
        }

        .distribution-bars {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
        }

        @media (max-width: 768px) {
          .distribution-bars {
            grid-template-columns: 1fr;
          }
        }

        .distribution-item {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .distribution-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 13px;
        }

        .dist-label {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .dist-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }

        .dist-count {
          font-weight: 600;
        }

        .dist-bar-bg {
          height: 6px;
          background: var(--bg-tertiary);
          border-radius: 3px;
          overflow: hidden;
        }

        .dist-bar-fill {
          height: 100%;
          border-radius: 3px;
          transition: width 0.5s ease;
        }
      `}</style>
    </div>
  )
}

export default StatsPanel
