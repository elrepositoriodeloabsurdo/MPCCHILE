import { useState, useEffect } from 'react';

export default function Home() {
  const [stats, setStats] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedConcept, setSelectedConcept] = useState(null);

  useEffect(() => {
    fetch('/api/stats')
      .then(r => r.json())
      .then(setStats)
      .catch(console.error);
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSelectedConcept(null);
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=20`);
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch (err) {
      console.error(err);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectConcept = async (conceptId) => {
    try {
      const res = await fetch(`/api/concept?id=${encodeURIComponent(conceptId)}`);
      const data = await res.json();
      setSelectedConcept(data);
    } catch (err) {
      console.error(err);
    }
  };

  // SVG Icons
  const JusticeIcon = () => (
    <svg width="40" height="40" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Scale of Justice */}
      <circle cx="50" cy="15" r="5" fill="#007bff" stroke="#007bff" strokeWidth="2"/>
      <line x1="50" y1="20" x2="50" y2="35" stroke="#007bff" strokeWidth="2"/>
      <line x1="30" y1="35" x2="70" y2="35" stroke="#007bff" strokeWidth="2"/>
      {/* Left pan */}
      <rect x="15" y="35" width="25" height="8" fill="#007bff" stroke="#007bff" strokeWidth="2" rx="2"/>
      <line x1="27.5" y1="20" x2="27.5" y2="35" stroke="#007bff" strokeWidth="1.5"/>
      {/* Right pan */}
      <rect x="60" y="35" width="25" height="8" fill="#007bff" stroke="#007bff" strokeWidth="2" rx="2"/>
      <line x1="72.5" y1="20" x2="72.5" y2="35" stroke="#007bff" strokeWidth="1.5"/>
      {/* Sword/Authority */}
      <line x1="50" y1="50" x2="50" y2="90" stroke="#764ba2" strokeWidth="3"/>
      <rect x="45" y="45" width="10" height="8" fill="#764ba2" rx="1"/>
      {/* Base */}
      <rect x="40" y="90" width="20" height="5" fill="#764ba2" rx="1"/>
    </svg>
  );

  const LogoIcon = () => (
    <svg width="60" height="60" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Retro computer monitor */}
      <rect x="30" y="20" width="140" height="110" fill="none" stroke="#333" strokeWidth="3" rx="8"/>
      <rect x="35" y="25" width="130" height="100" fill="#f0f0f0" rx="4"/>
      {/* Screen face */}
      <circle cx="80" cy="60" r="8" fill="#333"/>
      <circle cx="120" cy="60" r="8" fill="#333"/>
      <path d="M 80 80 Q 100 95 120 80" stroke="#333" strokeWidth="2" fill="none" strokeLinecap="round"/>
      {/* Chip */}
      <rect x="110" y="45" width="35" height="35" fill="none" stroke="#764ba2" strokeWidth="2" rx="4"/>
      <circle cx="120" cy="55" r="2" fill="#764ba2"/>
      <circle cx="135" cy="55" r="2" fill="#764ba2"/>
      <circle cx="120" cy="70" r="2" fill="#764ba2"/>
      <circle cx="135" cy="70" r="2" fill="#764ba2"/>
      <line x1="125" y1="48" x2="125" y2="42" stroke="#764ba2" strokeWidth="1.5"/>
      <line x1="140" y1="48" x2="140" y2="42" stroke="#764ba2" strokeWidth="1.5"/>
      {/* Base */}
      <rect x="60" y="130" width="80" height="8" fill="#333" rx="2"/>
      <line x1="65" y1="138" x2="75" y2="155" stroke="#333" strokeWidth="2"/>
      <line x1="135" y1="138" x2="125" y2="155" stroke="#333" strokeWidth="2"/>
      {/* Pencil */}
      <g transform="translate(-30, -20)">
        <line x1="60" y1="80" x2="100" y2="40" stroke="#764ba2" strokeWidth="4" strokeLinecap="round"/>
        <polygon points="100,40 108,35 104,48" fill="#764ba2"/>
      </g>
    </svg>
  );

  const StatsIcon = () => (
    <svg width="32" height="32" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="20" y="60" width="15" height="35" fill="white" stroke="white" strokeWidth="2" rx="2"/>
      <rect x="42" y="40" width="15" height="55" fill="white" stroke="white" strokeWidth="2" rx="2"/>
      <rect x="64" y="20" width="15" height="75" fill="white" stroke="white" strokeWidth="2" rx="2"/>
    </svg>
  );

  const SearchIcon = () => (
    <svg width="32" height="32" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="40" r="25" fill="none" stroke="white" strokeWidth="3"/>
      <line x1="60" y1="60" x2="80" y2="80" stroke="white" strokeWidth="3" strokeLinecap="round"/>
    </svg>
  );

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <header style={{ marginBottom: '2rem', textAlign: 'center', borderBottom: '3px solid #007bff', paddingBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', marginBottom: '1rem' }}>
          <JusticeIcon />
          <LogoIcon />
          <JusticeIcon />
        </div>
        <h1 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>VibeCodingChile MCP Ontology</h1>
        <p style={{ margin: '0', color: '#666', fontSize: '1.1em' }}>
          Ley N°21.719 | ISO/IEC 42001 | EU AI Act | Gobernanza IA
        </p>
      </header>

      {stats && (
        <section style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '2rem', borderRadius: '8px', marginBottom: '2rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <StatsIcon />
            <h2 style={{ margin: '0' }}>Estadísticas</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
            <div>
              <div style={{ fontSize: '2em', fontWeight: 'bold' }}>{stats.total_concepts}</div>
              <div style={{ fontSize: '0.9em', opacity: 0.9 }}>Conceptos</div>
            </div>
            <div>
              <div style={{ fontSize: '2em', fontWeight: 'bold' }}>{stats.total_relations}</div>
              <div style={{ fontSize: '0.9em', opacity: 0.9 }}>Relaciones</div>
            </div>
            <div>
              <div style={{ fontSize: '2em', fontWeight: 'bold' }}>{stats.branches?.length || 0}</div>
              <div style={{ fontSize: '0.9em', opacity: 0.9 }}>Ramas</div>
            </div>
          </div>
        </section>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <section>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <SearchIcon />
            <h2 style={{ margin: '0' }}>Buscar</h2>
          </div>
          <form onSubmit={handleSearch} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' }}>
            <input
              type="text"
              placeholder="Ej: base de licitud, riesgo alto..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              style={{
                padding: '0.75rem',
                borderRadius: '4px',
                border: '2px solid #ddd',
                fontSize: '1em'
              }}
            />
            <button type="submit" disabled={loading} style={{
              padding: '0.75rem',
              background: loading ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'default' : 'pointer',
              fontWeight: 'bold'
            }}>
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
          </form>

          {searchResults.length > 0 && (
            <div>
              <h3>Resultados ({searchResults.length})</h3>
              <div style={{ display: 'grid', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
                {searchResults.map((concept) => (
                  <button
                    key={concept.id}
                    onClick={() => handleSelectConcept(concept.id)}
                    style={{
                      padding: '1rem',
                      background: selectedConcept?.id === concept.id ? '#e7f3ff' : '#fff',
                      border: selectedConcept?.id === concept.id ? '2px solid #007bff' : '1px solid #ddd',
                      borderRadius: '4px',
                      textAlign: 'left',
                      cursor: 'pointer'
                    }}
                  >
                    <div style={{ fontWeight: 'bold' }}>{concept.label_es}</div>
                    <div style={{ fontSize: '0.85em', color: '#666' }}>{concept.definition_es?.substring(0, 80)}...</div>
                    <code style={{ fontSize: '0.8em', color: '#999' }}>{concept.id}</code>
                  </button>
                ))}
              </div>
            </div>
          )}
        </section>

        <section>
          <h2>Detalle</h2>
          {selectedConcept ? (
            <div style={{
              padding: '1.5rem',
              background: '#f0f8ff',
              borderRadius: '8px',
              border: '1px solid #007bff'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#007bff' }}>{selectedConcept.label_es}</h3>
              {selectedConcept.label_en && <p style={{ margin: '0 0 1rem 0', color: '#666', fontStyle: 'italic' }}>{selectedConcept.label_en}</p>}
              <div style={{ marginBottom: '1rem' }}>
                <strong>Definición:</strong>
                <p style={{ margin: '0.5rem 0 0 0', background: '#fff', padding: '0.75rem', borderRadius: '4px' }}>{selectedConcept.definition_es}</p>
              </div>
              <div><strong>Rama:</strong> <span style={{ background: '#fff', padding: '0.25rem 0.75rem', borderRadius: '4px' }}>{selectedConcept.branch}</span></div>
            </div>
          ) : (
            <div style={{ padding: '2rem', background: '#f9f9f9', borderRadius: '8px', textAlign: 'center', color: '#999' }}>
              ← Selecciona un concepto
            </div>
          )}
        </section>
      </div>

      <footer style={{ marginTop: '3rem', paddingTop: '1.5rem', borderTop: '1px solid #ddd', fontSize: '0.85em', color: '#666' }}>
        <h3>API Endpoints</h3>
        <ul style={{ fontSize: '0.8em' }}>
          <li><code>/api/search?q=término</code> - Buscar</li>
          <li><code>/api/concept?id=id</code> - Detalle</li>
          <li><code>/api/stats</code> - Estadísticas</li>
          <li><code>/api/health</code> - Health check</li>
        </ul>
      </footer>
    </div>
  );
}
