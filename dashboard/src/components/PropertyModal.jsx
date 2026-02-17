import React, { useState } from 'react';
import { 
  X, MapPin, Euro, Calendar, Building, Phone, Mail, 
  ExternalLink, Clock, Maximize, Bed, Bath, Tag,
  TrendingDown, Star, AlertCircle, CheckCircle
} from 'lucide-react';

function PropertyModal({ property, onClose }) {
  if (!property) return null;

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-PT', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    }).format(price);
  };

  const getCategoryInfo = (category) => {
    const info = {
      'A': { color: '#EF4444', label: 'Estagnado', desc: '≥180 dias, ≥2 reduções' },
      'B': { color: '#F59E0B', label: 'Preço Agressivo', desc: '≤30 dias, ≥12% abaixo' },
      'C': { color: '#10B981', label: 'Intervenção', desc: 'Potencial valorização' },
      'D': { color: '#3B82F6', label: 'Fundamentada', desc: 'Análise detalhada' },
    };
    return info[category] || { color: '#64748B', label: 'N/A', desc: '' };
  };

  const catInfo = getCategoryInfo(property.category);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-category" style={{ background: catInfo.color }}>
            {property.category} - {catInfo.label}
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        {/* Image */}
        <div className="modal-image">
          {property.images?.[0] ? (
            <img src={property.images[0]} alt={property.title} />
          ) : (
            <div className="modal-no-image">🏠</div>
          )}
        </div>

        {/* Content */}
        <div className="modal-body">
          <h2 className="modal-title">{property.title}</h2>
          
          <div className="modal-location">
            <MapPin size={18} />
            <span>{property.parish}, {property.location}</span>
          </div>

          {/* Price Section */}
          <div className="modal-price-section">
            <div className="modal-main-price">
              {formatPrice(property.price)}
            </div>
            {property.originalPrice && (
              <div className="modal-original-price">
                Preço original: {formatPrice(property.originalPrice)}
                <span className="discount-pill">
                  <TrendingDown size={14} />
                  {((property.originalPrice - property.price) / property.originalPrice * 100).toFixed(1)}%
                </span>
              </div>
            )}
            <div className="modal-price-m2">
              €{property.precoM2 || Math.round(property.price / property.area)}/m²
            </div>
          </div>

          {/* Key Stats */}
          <div className="modal-stats">
            <div className="stat-box">
              <Maximize size={20} />
              <span className="stat-value">{property.area} m²</span>
              <span className="stat-label">Área</span>
            </div>
            <div className="stat-box">
              <Building size={20} />
              <span className="stat-value">{property.typology}</span>
              <span className="stat-label">Tipologia</span>
            </div>
            <div className="stat-box">
              <Bed size={20} />
              <span className="stat-value">{property.bedrooms}</span>
              <span className="stat-label">Quartos</span>
            </div>
            <div className="stat-box">
              <Bath size={20} />
              <span className="stat-value">{property.bathrooms}</span>
              <span className="stat-label">Casas de Banho</span>
            </div>
          </div>

          {/* Score */}
          <div className="modal-score-section">
            <div className="score-header">
              <Star size={20} color="#F59E0B" />
              <span className="score-title">Score de Oportunidade</span>
              <span className="score-value">{property.opportunityScore}/100</span>
            </div>
            <div className="score-bar-large">
              <div 
                className="score-fill"
                style={{ 
                  width: `${property.opportunityScore}%`,
                  background: property.opportunityScore >= 70 ? '#10B981' : 
                             property.opportunityScore >= 50 ? '#F59E0B' : '#EF4444'
                }}
              />
            </div>
          </div>

          {/* Market Info */}
          <div className="modal-market">
            <h4><Tag size={16} /> Informação de Mercado</h4>
            <div className="market-grid">
              <div className="market-item">
                <span className="market-label">Dias no mercado</span>
                <span className="market-value">
                  <Clock size={14} /> {property.daysOnMarket} dias
                </span>
              </div>
              <div className="market-item">
                <span className="market-label">vs Mercado</span>
                <span className={`market-value ${property.vsMarket < 0 ? 'negative' : 'positive'}`}>
                  {property.vsMarket}%
                </span>
              </div>
              <div className="market-item">
                <span className="market-label">Reduções</span>
                <span className="market-value">{property.priceDrops}</span>
              </div>
              <div className="market-item">
                <span className="market-label">Estado</span>
                <span className="market-value">{property.estado || 'Em Leilão'}</span>
              </div>
            </div>
          </div>

          {/* Description */}
          {property.description && (
            <div className="modal-description">
              <h4><AlertCircle size={16} /> Descrição</h4>
              <p>{property.description}</p>
            </div>
          )}

          {/* Notes */}
          {property.notas && (
            <div className="modal-notes">
              <h4><CheckCircle size={16} /> Notas</h4>
              <p>{property.notas}</p>
            </div>
          )}

          {/* Contact */}
          {property.contacto && (
            <div className="modal-contact">
              <h4><Phone size={16} /> Contacto</h4>
              <p><Mail size={14} /> {property.contacto}</p>
            </div>
          )}

          {/* Source */}
          <div className="modal-source">
            <span>Fonte: <strong>{property.source}</strong></span>
            {property.dataLeilao && (
              <span className="auction-date">
                <Calendar size={14} />
                Leilão: {new Date(property.dataLeilao).toLocaleDateString('pt-PT')}
              </span>
            )}
          </div>

          {/* Actions */}
          <div className="modal-actions">
            <a 
              href={property.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn-primary"
            >
              <ExternalLink size={18} />
              Ver Anúncio Original
            </a>
            <button className="btn-secondary" onClick={onClose}>
              Fechar
            </button>
          </div>
        </div>
      </div>

      <style>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
        }

        .modal-content {
          background: #1E293B;
          border-radius: 16px;
          max-width: 700px;
          width: 100%;
          max-height: 90vh;
          overflow-y: auto;
          position: relative;
        }

        .modal-header {
          position: absolute;
          top: 16px;
          left: 16px;
          right: 16px;
          display: flex;
          justify-content: space-between;
          z-index: 10;
        }

        .modal-category {
          padding: 8px 16px;
          border-radius: 20px;
          color: white;
          font-size: 13px;
          font-weight: 600;
        }

        .modal-close {
          width: 40px;
          height: 40px;
          background: rgba(0, 0, 0, 0.5);
          border: none;
          border-radius: 50%;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }

        .modal-close:hover {
          background: rgba(0, 0, 0, 0.8);
        }

        .modal-image {
          height: 300px;
          background: #0F172A;
        }

        .modal-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .modal-no-image {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 80px;
        }

        .modal-body {
          padding: 24px;
        }

        .modal-title {
          font-size: 24px;
          font-weight: 700;
          margin-bottom: 8px;
        }

        .modal-location {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #94A3B8;
          margin-bottom: 20px;
        }

        .modal-price-section {
          background: #0F172A;
          padding: 20px;
          border-radius: 12px;
          margin-bottom: 20px;
        }

        .modal-main-price {
          font-size: 32px;
          font-weight: 700;
          color: #10B981;
        }

        .modal-original-price {
          display: flex;
          align-items: center;
          gap: 12px;
          color: #64748B;
          text-decoration: line-through;
          margin-top: 8px;
        }

        .discount-pill {
          display: flex;
          align-items: center;
          gap: 4px;
          background: rgba(239, 68, 68, 0.2);
          color: #EF4444;
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          text-decoration: none;
        }

        .modal-price-m2 {
          margin-top: 8px;
          color: #94A3B8;
        }

        .modal-stats {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 12px;
          margin-bottom: 24px;
        }

        .stat-box {
          background: #0F172A;
          padding: 16px;
          border-radius: 12px;
          text-align: center;
        }

        .stat-box svg {
          color: #3B82F6;
          margin-bottom: 8px;
        }

        .stat-value {
          display: block;
          font-size: 18px;
          font-weight: 700;
        }

        .stat-label {
          font-size: 12px;
          color: #64748B;
        }

        .modal-score-section {
          background: #0F172A;
          padding: 20px;
          border-radius: 12px;
          margin-bottom: 20px;
        }

        .score-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .score-title {
          flex: 1;
          font-weight: 600;
        }

        .score-value {
          font-size: 24px;
          font-weight: 700;
        }

        .score-bar-large {
          height: 12px;
          background: #334155;
          border-radius: 6px;
          overflow: hidden;
        }

        .score-fill {
          height: 100%;
          border-radius: 6px;
          transition: width 0.3s ease;
        }

        .modal-market, .modal-description, .modal-notes, .modal-contact {
          margin-bottom: 20px;
        }

        .modal-market h4, .modal-description h4, .modal-notes h4, .modal-contact h4 {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
          color: #94A3B8;
        }

        .market-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
        }

        .market-item {
          display: flex;
          justify-content: space-between;
          padding: 12px;
          background: #0F172A;
          border-radius: 8px;
        }

        .market-label {
          color: #64748B;
          font-size: 13px;
        }

        .market-value {
          display: flex;
          align-items: center;
          gap: 4px;
          font-weight: 600;
        }

        .market-value.negative {
          color: #10B981;
        }

        .market-value.positive {
          color: #EF4444;
        }

        .modal-description p, .modal-notes p, .modal-contact p {
          color: #94A3B8;
          line-height: 1.6;
        }

        .modal-source {
          display: flex;
          justify-content: space-between;
          padding: 16px;
          background: #0F172A;
          border-radius: 8px;
          margin-bottom: 20px;
          font-size: 13px;
        }

        .auction-date {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #F59E0B;
        }

        .modal-actions {
          display: flex;
          gap: 12px;
        }

        .btn-primary, .btn-secondary {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 14px 24px;
          border-radius: 8px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          text-decoration: none;
        }

        .btn-primary {
          background: #3B82F6;
          color: white;
          border: none;
        }

        .btn-primary:hover {
          background: #2563EB;
        }

        .btn-secondary {
          background: transparent;
          color: #94A3B8;
          border: 1px solid #334155;
        }

        .btn-secondary:hover {
          background: #334155;
          color: white;
        }

        @media (max-width: 600px) {
          .modal-stats {
            grid-template-columns: repeat(2, 1fr);
          }
          
          .market-grid {
            grid-template-columns: 1fr;
          }
          
          .modal-actions {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
}

export default PropertyModal;
