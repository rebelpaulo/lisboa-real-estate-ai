import React from 'react'
import { 
  Euro, 
  MapPin, 
  Clock, 
  Maximize, 
  TrendingDown,
  ExternalLink,
  Star
} from 'lucide-react'

function PropertyCard({ property, onClick, viewMode = 'grid' }) {
  const getCategoryBadge = (category) => {
    const badges = {
      'A': { class: 'badge-a', emoji: '🔴', label: 'Estagnado' },
      'B': { class: 'badge-b', emoji: '🟡', label: 'Preço Agressivo' },
      'C': { class: 'badge-c', emoji: '🟢', label: 'Intervenção' },
      'D': { class: 'badge-d', emoji: '🔵', label: 'Fundamentada' },
    }
    return badges[category] || { class: '', emoji: '⚪', label: 'N/A' }
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'score-high'
    if (score >= 50) return 'score-medium'
    return 'score-low'
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-PT', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    }).format(price)
  }

  const category = getCategoryBadge(property.opportunityCategory)

  if (viewMode === 'list') {
    return (
      <div className="property-card-list" onClick={onClick}>
        <div className="card-list-image">
          {property.photos?.[0] ? (
            <img src={property.photos[0]} alt={property.title} />
          ) : (
            <div className="no-image">🏠</div>
          )}
        </div>

        <div className="card-list-content">
          <div className="card-list-header">
            <div>
              <span className={`badge ${category.class}`}>
                {category.emoji} {category.label}
              </span>
              <h3 className="property-title">{property.title}</h3>
            </div>
            <div className="property-price">
              {formatPrice(property.price)}
            </div>
          </div>

          <div className="card-list-details">
            <div className="detail-item">
              <MapPin size={16} />
              {property.parish}, {property.municipality}
            </div>
            <div className="detail-item">
              <Maximize size={16} />
              {property.typology} • {property.areaM2} m²
            </div>
            <div className="detail-item">
              <Clock size={16} />
              {property.daysOnMarket} dias no mercado
            </div>
          </div>

          <div className="card-list-footer">
            <div className="score-section">
              <div className="score-header">
                <Star size={14} />
                <span>Score: {property.opportunityScore}/100</span>
              </div>
              <div className="score-bar">
                <div 
                  className={`score-bar-fill ${getScoreColor(property.opportunityScore)}`}
                  style={{ width: `${property.opportunityScore}%` }}
                />
              </div>
            </div>

            {property.discountVsMarket > 0 && (
              <div className="discount-badge">
                <TrendingDown size={14} />
                {property.discountVsMarket.toFixed(1)}% vs mercado
              </div>
            )}

            <a 
              href={property.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn btn-secondary btn-sm"
              onClick={(e) => e.stopPropagation()}
            >
              Ver anúncio
              <ExternalLink size={14} />
            </a>
          </div>
        </div>

        <style>{`
          .property-card-list {
            display: flex;
            background: var(--bg-secondary);
            border-radius: var(--border-radius);
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s;
          }

          .property-card-list:hover {
            box-shadow: var(--shadow-lg);
          }

          .card-list-image {
            width: 200px;
            min-height: 150px;
            flex-shrink: 0;
          }

          .card-list-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          .no-image {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            background: var(--bg-tertiary);
          }

          .card-list-content {
            flex: 1;
            padding: 16px;
            display: flex;
            flex-direction: column;
          }

          .card-list-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
          }

          .property-title {
            font-size: 16px;
            font-weight: 600;
            margin-top: 8px;
            max-width: 400px;
          }

          .property-price {
            font-size: 20px;
            font-weight: 700;
            color: var(--success);
          }

          .card-list-details {
            display: flex;
            gap: 20px;
            margin-bottom: 12px;
          }

          .detail-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: var(--text-secondary);
          }

          .card-list-footer {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-top: auto;
          }

          .score-section {
            flex: 1;
            max-width: 200px;
          }

          .score-header {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            margin-bottom: 4px;
          }

          .discount-badge {
            display: flex;
            align-items: center;
            gap: 4px;
            background: rgba(16, 185, 129, 0.15);
            color: var(--success);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
          }

          .btn-sm {
            padding: 6px 12px;
            font-size: 12px;
          }
        `}</style>
      </div>
    )
  }

  // Grid view
  return (
    <div className="property-card" onClick={onClick}>
      <div className="card-image">
        {property.photos?.[0] ? (
          <img src={property.photos[0]} alt={property.title} />
        ) : (
          <div className="no-image">🏠</div>
        )}
        <div className={`category-badge ${category.class}`}>
          {category.emoji} {category.label}
        </div>
      </div>

      <div className="card-content">
        <div className="card-header">
          <div className="price">{formatPrice(property.price)}</div>
          {property.pricePerM2 && (
            <div className="price-per-m2">€{property.pricePerM2.toLocaleString()}/m²</div>
          )}
        </div>

        <h3 className="title">{property.title}</h3>

        <div className="location">
          <MapPin size={14} />
          {property.parish}, {property.municipality}
        </div>

        <div className="details">
          <span><Maximize size={14} /> {property.typology}</span>
          <span><Euro size={14} /> {property.areaM2} m²</span>
          <span><Clock size={14} /> {property.daysOnMarket}d</span>
        </div>

        <div className="score-section">
          <div className="score-label">
            <Star size={14} />
            Score: {property.opportunityScore}/100
          </div>
          <div className="score-bar">
            <div 
              className={`score-bar-fill ${getScoreColor(property.opportunityScore)}`}
              style={{ width: `${property.opportunityScore}%` }}
            />
          </div>
        </div>

        {property.discountVsMarket > 0 && (
          <div className="discount">
            <TrendingDown size={14} />
            {property.discountVsMarket.toFixed(1)}% abaixo do mercado
          </div>
        )}

        <a 
          href={property.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="view-link"
          onClick={(e) => e.stopPropagation()}
        >
          Ver anúncio
          <ExternalLink size={14} />
        </a>
      </div>

      <style>{`
        .property-card {
          background: var(--bg-secondary);
          border-radius: var(--border-radius);
          overflow: hidden;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          flex-direction: column;
        }

        .property-card:hover {
          box-shadow: var(--shadow-lg);
          transform: translateY(-2px);
        }

        .card-image {
          position: relative;
          height: 180px;
          background: var(--bg-tertiary);
        }

        .card-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .no-image {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 48px;
        }

        .category-badge {
          position: absolute;
          top: 12px;
          left: 12px;
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 11px;
          font-weight: 600;
        }

        .card-content {
          padding: 16px;
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .card-header {
          display: flex;
          align-items: baseline;
          gap: 8px;
          margin-bottom: 8px;
        }

        .price {
          font-size: 20px;
          font-weight: 700;
          color: var(--success);
        }

        .price-per-m2 {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .title {
          font-size: 14px;
          font-weight: 500;
          line-height: 1.4;
          margin-bottom: 8px;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .location {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 12px;
        }

        .details {
          display: flex;
          gap: 12px;
          margin-bottom: 12px;
        }

        .details span {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: var(--text-secondary);
        }

        .score-section {
          margin-bottom: 12px;
        }

        .score-label {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          margin-bottom: 4px;
        }

        .discount {
          display: flex;
          align-items: center;
          gap: 4px;
          background: rgba(16, 185, 129, 0.15);
          color: var(--success);
          padding: 6px 10px;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 600;
          margin-bottom: 12px;
        }

        .view-link {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          padding: 10px;
          background: var(--bg-tertiary);
          border-radius: var(--border-radius);
          color: var(--text-primary);
          text-decoration: none;
          font-size: 13px;
          font-weight: 500;
          margin-top: auto;
          transition: all 0.2s;
        }

        .view-link:hover {
          background: var(--primary);
        }
      `}</style>
    </div>
  )
}

export default PropertyCard
