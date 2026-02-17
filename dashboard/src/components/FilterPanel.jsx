import React from 'react'
import { X, Sliders } from 'lucide-react'

function FilterPanel({ filters, onChange, onClose }) {
  const typologies = ['', 'T0', 'T1', 'T2', 'T3', 'T4', 'T5+', 'Moradia']
  const categories = [
    { value: '', label: 'Todas' },
    { value: 'A', label: '🔴 A - Estagnado' },
    { value: 'B', label: '🟡 B - Preço Agressivo' },
    { value: 'C', label: '🟢 C - Intervenção' },
    { value: 'D', label: '🔵 D - Fundamentada' },
  ]

  const handleChange = (field, value) => {
    onChange({ ...filters, [field]: value })
  }

  const handleReset = () => {
    onChange({
      category: '',
      minScore: 0,
      minDays: null,
      maxDays: null,
      typology: '',
      parish: '',
      minPrice: null,
      maxPrice: null,
    })
  }

  return (
    <div className="filter-panel">
      <div className="filter-header">
        <div className="filter-title">
          <Sliders size={18} />
          <h3>Filtros</h3>
        </div>
        <button className="close-btn" onClick={onClose}>
          <X size={20} />
        </button>
      </div>

      <div className="filter-content">
        {/* Categoria */}
        <div className="filter-group">
          <label>Categoria de Oportunidade</label>
          <select 
            value={filters.category}
            onChange={(e) => handleChange('category', e.target.value)}
          >
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        {/* Score mínimo */}
        <div className="filter-group">
          <label>Score mínimo: {filters.minScore}</label>
          <input
            type="range"
            min="0"
            max="100"
            value={filters.minScore}
            onChange={(e) => handleChange('minScore', parseInt(e.target.value))}
          />
          <div className="range-labels">
            <span>0</span>
            <span>50</span>
            <span>100</span>
          </div>
        </div>

        {/* Tempo no mercado */}
        <div className="filter-group">
          <label>Tempo no mercado (dias)</label>
          <div className="range-inputs">
            <input
              type="number"
              placeholder="Mín"
              value={filters.minDays || ''}
              onChange={(e) => handleChange('minDays', e.target.value ? parseInt(e.target.value) : null)}
            />
            <span>até</span>
            <input
              type="number"
              placeholder="Máx"
              value={filters.maxDays || ''}
              onChange={(e) => handleChange('maxDays', e.target.value ? parseInt(e.target.value) : null)}
            />
          </div>
          <div className="quick-filters">
            <button onClick={() => { handleChange('minDays', 90); handleChange('maxDays', null); }}>
              > 3 meses
            </button>
            <button onClick={() => { handleChange('minDays', 180); handleChange('maxDays', null); }}>
              > 6 meses
            </button>
            <button onClick={() => { handleChange('minDays', 365); handleChange('maxDays', null); }}>
              > 1 ano
            </button>
          </div>
        </div>

        {/* Tipologia */}
        <div className="filter-group">
          <label>Tipologia</label>
          <select
            value={filters.typology}
            onChange={(e) => handleChange('typology', e.target.value)}
          >
            <option value="">Todas</option>
            {typologies.filter(t => t).map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        {/* Localização */}
        <div className="filter-group">
          <label>Freguesia</label>
          <input
            type="text"
            placeholder="Ex: Belém, Alfama..."
            value={filters.parish}
            onChange={(e) => handleChange('parish', e.target.value)}
          />
        </div>

        {/* Preço */}
        <div className="filter-group">
          <label>Faixa de preço (€)</label>
          <div className="range-inputs">
            <input
              type="number"
              placeholder="Mín"
              value={filters.minPrice || ''}
              onChange={(e) => handleChange('minPrice', e.target.value ? parseInt(e.target.value) : null)}
            />
            <span>até</span>
            <input
              type="number"
              placeholder="Máx"
              value={filters.maxPrice || ''}
              onChange={(e) => handleChange('maxPrice', e.target.value ? parseInt(e.target.value) : null)}
            />
          </div>
        </div>
      </div>

      <div className="filter-footer">
        <button className="btn btn-secondary" onClick={handleReset}>
          Limpar filtros
        </button>
      </div>

      <style>{`
        .filter-panel {
          background: var(--bg-secondary);
          border-radius: var(--border-radius);
          padding: 20px;
          height: fit-content;
          position: sticky;
          top: 100px;
        }

        .filter-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 16px;
          border-bottom: 1px solid var(--bg-tertiary);
        }

        .filter-title {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .filter-title h3 {
          font-size: 16px;
          font-weight: 600;
        }

        .close-btn {
          background: none;
          border: none;
          color: var(--text-secondary);
          cursor: pointer;
          padding: 4px;
          display: none;
        }

        @media (max-width: 1024px) {
          .close-btn {
            display: block;
          }
        }

        .filter-content {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .filter-group label {
          font-size: 13px;
          font-weight: 500;
          color: var(--text-secondary);
        }

        .filter-group select,
        .filter-group input[type="text"],
        .filter-group input[type="number"] {
          padding: 10px 12px;
          background: var(--bg-tertiary);
          border: 1px solid transparent;
          border-radius: var(--border-radius);
          color: var(--text-primary);
          font-size: 14px;
          outline: none;
          transition: all 0.2s;
        }

        .filter-group select:focus,
        .filter-group input:focus {
          border-color: var(--primary);
        }

        .filter-group input[type="range"] {
          width: 100%;
          height: 6px;
          background: var(--bg-tertiary);
          border-radius: 3px;
          outline: none;
          -webkit-appearance: none;
        }

        .filter-group input[type="range"]::-webkit-slider-thumb {
          -webkit-appearance: none;
          width: 18px;
          height: 18px;
          background: var(--primary);
          border-radius: 50%;
          cursor: pointer;
        }

        .range-labels {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          color: var(--text-muted);
        }

        .range-inputs {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .range-inputs input {
          flex: 1;
        }

        .range-inputs span {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .quick-filters {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-top: 8px;
        }

        .quick-filters button {
          padding: 4px 10px;
          background: var(--bg-tertiary);
          border: none;
          border-radius: 4px;
          color: var(--text-secondary);
          font-size: 11px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .quick-filters button:hover {
          background: var(--primary);
          color: white;
        }

        .filter-footer {
          margin-top: 20px;
          padding-top: 16px;
          border-top: 1px solid var(--bg-tertiary);
        }

        .filter-footer button {
          width: 100%;
        }
      `}</style>
    </div>
  )
}

export default FilterPanel
