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

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <header style={{ marginBottom: '2rem', textAlign: 'center', borderBottom: '3px solid #007bff', paddingBottom: '1rem' }}>
        <h1 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>🎯 VibeCodingChile MCP Ontology</h1>
        <p style={{ margin: '0', color: '#666', fontSize: '1.1em' }}>
          Ley N°21.719 | ISO/IEC 42001 | EU AI Act | Gobernanza IA
        </p>
      </header>

      {stats && (
        <section style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '2rem', borderRadius: '8px', marginBottom: '2rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <h2 style={{ margin: '0 0 1rem 0' }}>📊 Estadísticas</h2>
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
          <h2>🔍 Buscar</h2>
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
              {loading ? '⏳ Buscando...' : '🚀 Buscar'}
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
          <h2>📋 Detalle</h2>
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
              👈 Selecciona un concepto
            </div>
          )}
        </section>
      </div>

      <footer style={{ marginTop: '3rem', paddingTop: '1.5rem', borderTop: '1px solid #ddd', fontSize: '0.85em', color: '#666' }}>
        <h3>📡 API Endpoints</h3>
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