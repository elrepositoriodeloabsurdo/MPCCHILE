const ontology = require('../../ontology.json');
const relations = require('../../relations.json');

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  const branches = {};
  ontology.concepts.forEach(c => {
    if (!branches[c.branch]) branches[c.branch] = { id: c.branch, count: 0 };
    branches[c.branch].count++;
  });
  
  res.json({
    version: '0.1.0',
    total_concepts: ontology.concepts.length,
    total_relations: relations.relations.length,
    branches: Object.values(branches)
  });
}