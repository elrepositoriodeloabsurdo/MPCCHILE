export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.json({ status: 'ok', service: 'VibeCodingChile MCP', version: '0.1.0' });
}