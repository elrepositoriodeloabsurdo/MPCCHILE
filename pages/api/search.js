const ontology = require('../../ontology.json');

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  const { q, limit = '10' } = req.query;
  if (!q) return res.status(400).json({ error: 'Query parameter q required' });

  const lowQuery = q.toLowerCase();
  let results = ontology.concepts.filter(c => 
    c.label_es?.toLowerCase().includes(lowQuery) ||
    c.label_en?.toLowerCase().includes(lowQuery) ||
    c.definition_es?.toLowerCase().includes(lowQuery)
  ).slice(0, Math.min(parseInt(limit), 50));

  res.json({ query: q, count: results.length, results });
}