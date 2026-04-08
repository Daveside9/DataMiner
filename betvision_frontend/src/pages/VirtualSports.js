import React, { useState, useEffect, useCallback } from 'react';

const API = 'http://localhost:5055/api/virt';

const SITE_LABELS = {
  bet9ja_zoom:        'Bet9ja Zoom',
  sportybet_virtual:  'SportyBet Virtual',
  msport_virtual:     'Msport Virtual',
  '1xbet_virtual':    '1xBet Virtual',
  manual:             'Manual Entry',
};

const col = {
  bg:      '#0f172a',
  card:    '#1e293b',
  border:  '#334155',
  text:    '#e2e8f0',
  muted:   '#64748b',
  blue:    '#38bdf8',
  green:   '#22c55e',
  red:     '#ef4444',
  yellow:  '#f59e0b',
  purple:  '#8b5cf6',
};

const Badge = ({ label, color }) => (
  <span style={{ background: color, color: '#fff', borderRadius: 6, padding: '2px 10px', fontSize: 12, fontWeight: 700, marginLeft: 6 }}>
    {label}
  </span>
);

const Card = ({ children, style }) => (
  <div style={{ background: col.card, borderRadius: 12, padding: 20, ...style }}>{children}</div>
);

const resultColor = r =>
  r === 'Home Win' || r === 'home_win' ? col.green :
  r === 'Away Win' || r === 'away_win' ? col.red : col.yellow;

export default function VirtualSports() {
  const [tab, setTab]             = useState('predict');
  const [sites, setSites]         = useState([]);
  const [selectedSite, setSite]   = useState('bet9ja_zoom');
  const [prediction, setPred]     = useState(null);
  const [results, setResults]     = useState([]);
  const [dbStats, setDbStats]     = useState({});
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState('');
  const [msg, setMsg]             = useState('');

  // Manual entry form
  const [manHome, setManHome]     = useState('');
  const [manAway, setManAway]     = useState('');
  const [manHS, setManHS]         = useState('');
  const [manAS, setManAS]         = useState('');

  // Bulk paste
  const [bulkText, setBulkText]   = useState('');

  const fetchSites = useCallback(() => {
    fetch(`${API}/sites`).then(r => r.json()).then(d => setSites(d.sites || [])).catch(() => {});
  }, []);

  const fetchStats = useCallback(() => {
    fetch(`${API}/stats`).then(r => r.json()).then(d => setDbStats(d)).catch(() => {});
  }, []);

  useEffect(() => {
    fetchSites();
    fetchStats();
    const t = setInterval(() => { fetchSites(); fetchStats(); }, 10000);
    return () => clearInterval(t);
  }, [fetchSites, fetchStats]);

  useEffect(() => {
    if (tab === 'results') {
      fetch(`${API}/results?site=${selectedSite}&limit=60`)
        .then(r => r.json()).then(d => setResults(d.results || [])).catch(() => {});
    }
  }, [tab, selectedSite]);

  const startScraper = async () => {
    setLoading(true); setError(''); setMsg('');
    try {
      const r = await fetch(`${API}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site: selectedSite, headless: true, interval: 60 }),
      });
      const d = await r.json();
      setMsg(d.message || d.error);
      fetchSites();
    } catch { setError('API not reachable. Run: python virtual_api.py'); }
    setLoading(false);
  };

  const stopScraper = async () => {
    await fetch(`${API}/stop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ site: selectedSite }),
    });
    fetchSites();
  };

  const getPrediction = async () => {
    setLoading(true); setError(''); setPred(null);
    try {
      const r = await fetch(`${API}/predict?site=${selectedSite}`);
      const d = await r.json();
      if (d.error) setError(d.error);
      else setPred(d);
    } catch { setError('API not reachable. Run: python virtual_api.py'); }
    setLoading(false);
  };

  const addManualResult = async () => {
    if (!manHome || !manAway || manHS === '' || manAS === '') {
      setError('Fill all fields'); return;
    }
    setError(''); setMsg('');
    const r = await fetch(`${API}/add-result`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        site: selectedSite,
        home_team: manHome, away_team: manAway,
        home_score: parseInt(manHS), away_score: parseInt(manAS),
      }),
    });
    const d = await r.json();
    setMsg(d.message);
    setManHome(''); setManAway(''); setManHS(''); setManAS('');
    fetchStats();
  };

  const addBulkResults = async () => {
    // Parse lines like: Arsenal 2-1 Chelsea  OR  Arsenal,Chelsea,2,1
    const lines = bulkText.trim().split('\n').filter(Boolean);
    const parsed = [];
    for (const line of lines) {
      const m1 = line.match(/^(.+?)\s+(\d+)\s*[-:]\s*(\d+)\s+(.+)$/);
      const m2 = line.match(/^(.+?),(.+?),(\d+),(\d+)$/);
      if (m1) parsed.push({ home_team: m1[1].trim(), away_team: m1[4].trim(), home_score: parseInt(m1[2]), away_score: parseInt(m1[3]) });
      else if (m2) parsed.push({ home_team: m2[1].trim(), away_team: m2[2].trim(), home_score: parseInt(m2[3]), away_score: parseInt(m2[4]) });
    }
    if (!parsed.length) { setError('No valid lines found. Format: "Arsenal 2-1 Chelsea"'); return; }
    const r = await fetch(`${API}/bulk-add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ site: selectedSite, results: parsed }),
    });
    const d = await r.json();
    setMsg(`Saved ${d.saved} of ${d.total} results`);
    setBulkText('');
    fetchStats();
  };

  const currentSite = sites.find(s => s.id === selectedSite);
  const isRunning   = currentSite?.running;

  const tabs = [
    { id: 'predict', label: '🔮 Predict' },
    { id: 'manual',  label: '✏️ Add Results' },
    { id: 'results', label: '📋 History' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: col.bg, color: col.text, fontFamily: 'Inter,sans-serif' }}>

      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg,#1e3a5f,#0f172a)', padding: '22px 28px', borderBottom: `1px solid ${col.border}` }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800, color: col.blue }}>⚽ Virtual Sports AI Predictor</h1>
        <p style={{ margin: '4px 0 0', color: col.muted, fontSize: 13 }}>
          Bet9ja Zoom · SportyBet Virtual · Msport Virtual · 1xBet Virtual
        </p>

        {/* Stats */}
        <div style={{ display: 'flex', gap: 16, marginTop: 14, flexWrap: 'wrap' }}>
          {[
            { label: 'Total Results', value: dbStats.total || 0 },
            ...Object.entries(dbStats.by_site || {}).map(([k, v]) => ({ label: SITE_LABELS[k] || k, value: v })),
            { label: 'Last Hour', value: dbStats.last_hour || 0 },
          ].map(s => (
            <div key={s.label} style={{ background: col.card, borderRadius: 8, padding: '8px 16px', minWidth: 100 }}>
              <div style={{ fontSize: 20, fontWeight: 800, color: col.blue }}>{s.value}</div>
              <div style={{ fontSize: 11, color: col.muted }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ padding: '20px 28px' }}>

        {/* Site selector + scraper controls */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 20, flexWrap: 'wrap' }}>
          <select
            value={selectedSite}
            onChange={e => setSite(e.target.value)}
            style={{ background: col.card, color: col.text, border: `1px solid ${col.border}`, borderRadius: 8, padding: '8px 14px', fontSize: 14 }}
          >
            {Object.entries(SITE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>

          {isRunning ? (
            <button onClick={stopScraper} style={{ background: col.red, color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontWeight: 700, fontSize: 13 }}>
              ⏹ Stop Scraper
            </button>
          ) : (
            <button onClick={startScraper} disabled={loading} style={{ background: col.green, color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontWeight: 700, fontSize: 13 }}>
              ▶ Start Auto-Scraper
            </button>
          )}

          {isRunning && (
            <span style={{ fontSize: 12, color: col.green }}>
              🟢 Scraping {currentSite?.name} · {currentSite?.collected} collected
            </span>
          )}

          {msg   && <span style={{ fontSize: 13, color: col.green }}>✅ {msg}</span>}
          {error && <span style={{ fontSize: 13, color: col.red }}>⚠️ {error}</span>}
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 20, borderBottom: `1px solid ${col.border}` }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              background: tab === t.id ? '#1e3a5f' : 'transparent',
              color: tab === t.id ? col.blue : col.muted,
              border: 'none', borderBottom: tab === t.id ? `2px solid ${col.blue}` : '2px solid transparent',
              padding: '9px 18px', cursor: 'pointer', fontWeight: 600, fontSize: 14, borderRadius: '6px 6px 0 0',
            }}>{t.label}</button>
          ))}
        </div>

        {/* ══ TAB: PREDICT ══════════════════════════════════════════════════ */}
        {tab === 'predict' && (
          <div style={{ maxWidth: 780 }}>
            <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
              <button onClick={getPrediction} disabled={loading} style={{
                background: col.purple, color: '#fff', border: 'none', borderRadius: 8,
                padding: '10px 24px', cursor: 'pointer', fontWeight: 700, fontSize: 15,
              }}>
                {loading ? '⏳ Analyzing…' : '🔮 Get AI Prediction'}
              </button>
              <span style={{ fontSize: 12, color: col.muted, alignSelf: 'center' }}>
                Uses all collected results for {SITE_LABELS[selectedSite]}
              </span>
            </div>

            {prediction && !prediction.error && (() => {
              const p = prediction.prediction;
              return (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

                  {/* Main prediction card */}
                  <Card>
                    <div style={{ fontSize: 13, color: col.muted, marginBottom: 10 }}>
                      Based on {prediction.total_analyzed} results · {SITE_LABELS[selectedSite]}
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: 12 }}>
                      {[
                        { label: 'Predicted Result', value: p.predicted_result, color: resultColor(p.predicted_result), conf: p.result_confidence },
                        { label: 'Predicted Score',  value: p.predicted_score,  color: col.blue,   conf: null },
                        { label: 'Over/Under',       value: p.over_under,       color: col.yellow, conf: p.ou_confidence },
                        { label: 'BTTS',             value: p.btts,             color: col.purple, conf: p.btts_confidence },
                      ].map(item => (
                        <div key={item.label} style={{ background: col.bg, borderRadius: 10, padding: 14, textAlign: 'center' }}>
                          <div style={{ fontSize: 11, color: col.muted, marginBottom: 6 }}>{item.label}</div>
                          <div style={{ fontSize: 22, fontWeight: 900, color: item.color }}>{item.value}</div>
                          {item.conf && <div style={{ fontSize: 11, color: col.muted, marginTop: 4 }}>{item.conf}% conf</div>}
                        </div>
                      ))}
                    </div>

                    {/* Overall confidence bar */}
                    <div style={{ marginTop: 16 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: col.muted, marginBottom: 4 }}>
                        <span>Overall Confidence</span>
                        <span style={{ color: col.blue, fontWeight: 700 }}>{p.confidence}%</span>
                      </div>
                      <div style={{ height: 8, background: col.border, borderRadius: 4 }}>
                        <div style={{ height: '100%', width: `${p.confidence}%`, background: `linear-gradient(90deg,${col.purple},${col.blue})`, borderRadius: 4 }} />
                      </div>
                    </div>

                    {/* Suggestions */}
                    {p.suggestions?.length > 0 && (
                      <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {p.suggestions.map((s, i) => (
                          <div key={i} style={{ background: '#1e3a5f', borderRadius: 6, padding: '6px 12px', fontSize: 13, color: col.blue }}>
                            💡 {s}
                          </div>
                        ))}
                      </div>
                    )}

                    <div style={{ marginTop: 12, fontSize: 11, color: col.muted, fontStyle: 'italic' }}>
                      ⚠️ {p.disclaimer}
                    </div>
                  </Card>

                  {/* Result distribution */}
                  <Card>
                    <div style={{ fontSize: 13, fontWeight: 700, color: col.text, marginBottom: 12 }}>Result Distribution</div>
                    <div style={{ display: 'flex', gap: 10 }}>
                      {[
                        { label: 'Home Win', val: prediction.result_distribution.home_win, color: col.green },
                        { label: 'Draw',     val: prediction.result_distribution.draw,     color: col.yellow },
                        { label: 'Away Win', val: prediction.result_distribution.away_win, color: col.red },
                      ].map(item => (
                        <div key={item.label} style={{ flex: 1, background: col.bg, borderRadius: 8, padding: 12, textAlign: 'center' }}>
                          <div style={{ fontSize: 20, fontWeight: 800, color: item.color }}>{item.val}%</div>
                          <div style={{ fontSize: 11, color: col.muted }}>{item.label}</div>
                          <div style={{ height: 4, background: col.border, borderRadius: 2, marginTop: 6 }}>
                            <div style={{ height: '100%', width: `${item.val}%`, background: item.color, borderRadius: 2 }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>

                  {/* Goals stats */}
                  <Card>
                    <div style={{ fontSize: 13, fontWeight: 700, color: col.text, marginBottom: 12 }}>Goals Analysis</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 }}>
                      {[
                        { label: 'Avg Goals',  val: prediction.goals.average },
                        { label: 'Over 1.5',   val: `${prediction.goals.over_1_5}%` },
                        { label: 'Over 2.5',   val: `${prediction.goals.over_2_5}%` },
                        { label: 'BTTS Rate',  val: `${prediction.goals.btts}%` },
                      ].map(item => (
                        <div key={item.label} style={{ background: col.bg, borderRadius: 8, padding: 12, textAlign: 'center' }}>
                          <div style={{ fontSize: 18, fontWeight: 800, color: col.blue }}>{item.val}</div>
                          <div style={{ fontSize: 11, color: col.muted }}>{item.label}</div>
                        </div>
                      ))}
                    </div>
                  </Card>

                  {/* Hot scores + streaks */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                    <Card>
                      <div style={{ fontSize: 13, fontWeight: 700, color: col.text, marginBottom: 10 }}>🔥 Hot Scores</div>
                      {prediction.hot_scores.map((s, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: `1px solid ${col.border}` }}>
                          <span style={{ fontWeight: 700, color: col.blue }}>{s.score}</span>
                          <span style={{ color: col.muted, fontSize: 13 }}>{s.count}x · {s.pct}%</span>
                        </div>
                      ))}
                    </Card>

                    <Card>
                      <div style={{ fontSize: 13, fontWeight: 700, color: col.text, marginBottom: 10 }}>📈 Current Streaks</div>
                      {[
                        { label: 'Result streak',   val: `${prediction.streaks.result_streak}x ${prediction.streaks.current_result?.replace('_',' ')}` },
                        { label: 'Over 2.5 streak', val: `${prediction.streaks.over25_streak} games` },
                        { label: 'Under 2.5 streak',val: `${prediction.streaks.under25_streak} games` },
                        { label: 'BTTS streak',     val: `${prediction.streaks.btts_streak} games` },
                        { label: 'No BTTS streak',  val: `${prediction.streaks.no_btts_streak} games` },
                      ].map(item => (
                        <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: `1px solid ${col.border}`, fontSize: 13 }}>
                          <span style={{ color: col.muted }}>{item.label}</span>
                          <span style={{ fontWeight: 700, color: col.text }}>{item.val}</span>
                        </div>
                      ))}
                      <div style={{ marginTop: 10, fontSize: 12, color: col.muted }}>
                        Last 5: {prediction.streaks.last_5_results?.map(r =>
                          r === 'home_win' ? '🟢' : r === 'away_win' ? '🔴' : '🟡'
                        ).join(' ')}
                      </div>
                    </Card>
                  </div>

                </div>
              );
            })()}

            {prediction?.error && (
              <Card style={{ borderLeft: `4px solid ${col.yellow}` }}>
                <div style={{ color: col.yellow, fontWeight: 700, marginBottom: 8 }}>⚠️ Not enough data yet</div>
                <div style={{ color: col.muted, fontSize: 14 }}>{prediction.error}</div>
                <div style={{ marginTop: 12, fontSize: 13, color: col.text }}>
                  You need at least <strong style={{ color: col.blue }}>{prediction.needed}</strong> results.
                  Currently have <strong style={{ color: col.blue }}>{prediction.collected}</strong>.
                </div>
                <div style={{ marginTop: 10, fontSize: 13, color: col.muted }}>
                  👉 Either start the auto-scraper above, or manually enter results in the "✏️ Add Results" tab.
                </div>
              </Card>
            )}
          </div>
        )}

        {/* ══ TAB: MANUAL ENTRY ═════════════════════════════════════════════ */}
        {tab === 'manual' && (
          <div style={{ maxWidth: 700 }}>

            {/* Single result */}
            <Card style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 700, color: col.text, marginBottom: 14 }}>
                Add Single Result
              </div>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
                {[
                  { label: 'Home Team', val: manHome, set: setManHome, ph: 'e.g. Arsenal',  w: 160 },
                  { label: 'Home Score', val: manHS,  set: setManHS,   ph: '0',             w: 70, type: 'number' },
                  { label: 'Away Score', val: manAS,  set: setManAS,   ph: '0',             w: 70, type: 'number' },
                  { label: 'Away Team', val: manAway, set: setManAway, ph: 'e.g. Chelsea',  w: 160 },
                ].map(f => (
                  <div key={f.label}>
                    <label style={{ display: 'block', fontSize: 11, color: col.muted, marginBottom: 4 }}>{f.label}</label>
                    <input
                      type={f.type || 'text'}
                      value={f.val}
                      onChange={e => f.set(e.target.value)}
                      placeholder={f.ph}
                      style={{ background: col.bg, color: col.text, border: `1px solid ${col.border}`, borderRadius: 8, padding: '8px 12px', fontSize: 14, width: f.w }}
                    />
                  </div>
                ))}
                <button onClick={addManualResult} style={{ background: col.green, color: '#fff', border: 'none', borderRadius: 8, padding: '9px 20px', cursor: 'pointer', fontWeight: 700, fontSize: 14 }}>
                  + Add
                </button>
              </div>
            </Card>

            {/* Bulk paste */}
            <Card>
              <div style={{ fontSize: 15, fontWeight: 700, color: col.text, marginBottom: 6 }}>
                Bulk Paste Results
              </div>
              <div style={{ fontSize: 12, color: col.muted, marginBottom: 10 }}>
                One result per line. Format: <code style={{ color: col.blue }}>Arsenal 2-1 Chelsea</code> or <code style={{ color: col.blue }}>Arsenal,Chelsea,2,1</code>
              </div>
              <textarea
                value={bulkText}
                onChange={e => setBulkText(e.target.value)}
                placeholder={"Arsenal 2-1 Chelsea\nReal Madrid 3-0 Barcelona\nMan City 1-1 Liverpool"}
                rows={8}
                style={{ width: '100%', background: col.bg, color: col.text, border: `1px solid ${col.border}`, borderRadius: 8, padding: 12, fontSize: 13, fontFamily: 'monospace', resize: 'vertical', boxSizing: 'border-box' }}
              />
              <button onClick={addBulkResults} style={{ marginTop: 10, background: col.blue, color: '#fff', border: 'none', borderRadius: 8, padding: '9px 20px', cursor: 'pointer', fontWeight: 700, fontSize: 14 }}>
                📥 Import All
              </button>
            </Card>

          </div>
        )}

        {/* ══ TAB: HISTORY ══════════════════════════════════════════════════ */}
        {tab === 'results' && (
          <div>
            <div style={{ fontSize: 14, color: col.muted, marginBottom: 14 }}>
              Showing last 60 results for {SITE_LABELS[selectedSite]}
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ background: col.card, color: col.muted }}>
                    {['Home','Score','Away','Result','Goals','BTTS','Time'].map(h => (
                      <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, i) => (
                    <tr key={i} style={{ borderBottom: `1px solid ${col.border}`, background: i % 2 === 0 ? '#0f172a' : 'transparent' }}>
                      <td style={{ padding: '8px 14px', fontWeight: 600 }}>{r.home_team}</td>
                      <td style={{ padding: '8px 14px', fontWeight: 900, color: col.blue, textAlign: 'center' }}>
                        {r.home_score}-{r.away_score}
                      </td>
                      <td style={{ padding: '8px 14px', fontWeight: 600 }}>{r.away_team}</td>
                      <td style={{ padding: '8px 14px' }}>
                        <span style={{ color: resultColor(r.result), fontWeight: 700, fontSize: 12 }}>
                          {r.result?.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td style={{ padding: '8px 14px', color: col.muted }}>{r.total_goals}</td>
                      <td style={{ padding: '8px 14px' }}>
                        <span style={{ color: r.btts ? col.green : col.red, fontSize: 12 }}>
                          {r.btts ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td style={{ padding: '8px 14px', color: col.muted, fontSize: 11 }}>
                        {r.scraped_at?.slice(11, 16)}
                      </td>
                    </tr>
                  ))}
                  {results.length === 0 && (
                    <tr><td colSpan={7} style={{ padding: 24, textAlign: 'center', color: col.muted }}>
                      No results yet. Start the scraper or add results manually.
                    </td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
