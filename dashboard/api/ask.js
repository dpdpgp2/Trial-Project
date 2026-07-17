// Ask-the-Analyst intake: password gate -> GitHub Issue queue (label: analyst-question).
// Env vars (set in Vercel): ASK_PASSWORD, GITHUB_TOKEN (fine-grained PAT, this repo,
// Issues read/write ONLY), GITHUB_REPO ("owner/repo").
// The pipeline (dc_qa.py) answers the oldest 5 open questions each run and closes them.
const LABEL = 'analyst-question';
const MAX_OPEN = 20;

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });
  const { question, password } = req.body || {};
  if (!process.env.ASK_PASSWORD || password !== process.env.ASK_PASSWORD)
    return res.status(401).json({ error: 'wrong password' });
  const q = String(question || '').replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim();
  if (q.length < 10 || q.length > 300)
    return res.status(400).json({ error: 'question must be 10-300 characters' });

  const repo = process.env.GITHUB_REPO, token = process.env.GITHUB_TOKEN;
  if (!repo || !token) return res.status(503).json({ error: 'queue not configured' });
  const gh = (path, opts = {}) => fetch(`https://api.github.com${path}`, {
    ...opts,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'analyst-desk',
      ...(opts.body ? { 'Content-Type': 'application/json' } : {}),
    },
  });

  const list = await gh(`/repos/${repo}/issues?labels=${LABEL}&state=open&per_page=${MAX_OPEN}`);
  if (!list.ok) return res.status(503).json({ error: 'queue unavailable' });
  const open = await list.json();
  if (open.length >= MAX_OPEN)
    return res.status(429).json({ error: 'Cannot accept any more questions at this time — queue is full.' });
  const dupe = open.some(i => {
    try { return JSON.parse(i.body.match(/\{[\s\S]*\}/)[0]).q === q; } catch { return false; }
  });
  if (dupe) return res.status(200).json({ status: 'already queued' });

  const r = await gh(`/repos/${repo}/issues`, {
    method: 'POST',
    body: JSON.stringify({
      title: `Q: ${q.slice(0, 60)}`,
      labels: [LABEL],
      body: '```json\n' + JSON.stringify({ q, asked_at: new Date().toISOString() }) + '\n```',
    }),
  });
  if (!r.ok) return res.status(503).json({ error: 'could not queue question' });
  return res.status(200).json({ status: 'queued' });
};
