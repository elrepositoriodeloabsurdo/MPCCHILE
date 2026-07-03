const ontology = require('../../ontology.json');

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  const { id } = req.query;
  if (!id) return res.status(400).json({ error: 'Query parameter id required' });
  
  const concept = ontology.concepts.find(c => c.id === id);
  if (!concept) return res.status(404).json({ error: 'Not found' });
  
  res.json(concept);
}