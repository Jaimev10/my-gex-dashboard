<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>GEX Heatmap · Dealer Positioning</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
  :root {
    --bg: #090c0f;
    --bg2: #0f1318;
    --bg3: #161c24;
    --bg4: #1e2730;
    --border: rgba(255,255,255,0.07);
    --border2: rgba(255,255,255,0.12);
    --text: #e8edf2;
    --muted: #6b7c8f;
    --dim: #3a4a5a;
    --green: #00d4a0;
    --green-bg: rgba(0,212,160,0.08);
    --green-border: rgba(0,212,160,0.2);
    --red: #ff5f52;
    --red-bg: rgba(255,95,82,0.08);
    --red-border: rgba(255,95,82,0.2);
    --purple: #a78bfa;
    --purple-bg: rgba(167,139,250,0.08);
    --amber: #f59e0b;
    --accent: #00d4a0;
    --font-mono: 'JetBrains Mono', monospace;
    --font-display: 'Syne', sans-serif;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 13px;
    min-height: 100vh;
    display: flex;
    overflow-x: hidden;
  }

  /* ── Sidebar ── */
  .sidebar {
    width: 220px;
    min-height: 100vh;
    background: var(--bg2);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    position: fixed;
    top: 0; left: 0; bottom: 0;
    z-index: 10;
  }

  .sidebar-logo {
    padding: 24px 20px 20px;
    border-bottom: 1px solid var(--border);
  }

  .logo-mark {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
  }

  .logo-icon {
    width: 30px; height: 30px;
    background: var(--green);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
  }

  .logo-icon svg { width: 16px; height: 16px; }

  .logo-title {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.04em;
    color: var(--text);
  }

  .logo-sub {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding-left: 40px;
  }

  .sidebar-section {
    padding: 20px 20px 0;
  }

  .sidebar-label {
    font-size: 9px;
    color: var(--dim);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 12px;
  }

  /* Watchlist tickers */
  .ticker-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 20px;
  }

  .chip {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 4px;
    background: var(--bg3);
    border: 1px solid var(--border2);
    color: var(--text);
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
  }

  .chip.active { border-color: var(--green); color: var(--green); background: var(--green-bg); }

  .chip .x {
    color: var(--muted);
    font-size: 10px;
    line-height: 1;
  }

  /* Slider filter */
  .filter-row {
    margin-bottom: 18px;
  }

  .filter-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .filter-name { font-size: 11px; color: var(--muted); }
  .filter-val { font-size: 11px; color: var(--text); font-weight: 500; }

  input[type=range] {
    -webkit-appearance: none;
    width: 100%;
    height: 2px;
    background: var(--bg4);
    border-radius: 2px;
    outline: none;
    cursor: pointer;
  }

  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px; height: 12px;
    border-radius: 50%;
    background: var(--green);
    border: 2px solid var(--bg2);
    cursor: pointer;
  }

  .toggle-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    cursor: pointer;
  }

  .toggle {
    width: 30px; height: 16px;
    background: var(--bg4);
    border-radius: 8px;
    position: relative;
    transition: background 0.2s;
    flex-shrink: 0;
    border: 1px solid var(--border2);
  }

  .toggle.on { background: var(--green); border-color: var(--green); }

  .toggle::after {
    content: '';
    position: absolute;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: white;
    top: 2px; left: 2px;
    transition: transform 0.2s;
  }

  .toggle.on::after { transform: translateX(14px); }

  .toggle-label { font-size: 11px; color: var(--muted); }

  .sidebar-footer {
    margin-top: auto;
    padding: 16px 20px;
    border-top: 1px solid var(--border);
    font-size: 10px;
    color: var(--dim);
    letter-spacing: 0.04em;
  }

  /* ── Main ── */
  .main {
    margin-left: 220px;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  /* Top nav */
  .topnav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    height: 56px;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    position: sticky;
    top: 0;
    z-index: 5;
  }

  .nav-left {
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .page-title {
    font-family: var(--font-display);
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: 0.02em;
  }

  .nav-tabs {
    display: flex;
    gap: 2px;
  }

  .nav-tab {
    font-size: 11px;
    color: var(--muted);
    padding: 4px 12px;
    border-radius: 4px;
    cursor: pointer;
    letter-spacing: 0.04em;
    transition: color 0.15s, background 0.15s;
  }

  .nav-tab:hover { color: var(--text); background: var(--bg3); }
  .nav-tab.active { color: var(--text); background: var(--bg3); }

  .nav-right {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .live-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 10px;
    color: var(--green);
    background: var(--green-bg);
    border: 1px solid var(--green-border);
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .live-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--green);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  .timestamp {
    font-size: 11px;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }

  .refresh-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    padding: 6px 14px;
    border-radius: 5px;
    border: 1px solid var(--border2);
    background: transparent;
    color: var(--muted);
    cursor: pointer;
    font-family: var(--font-mono);
    letter-spacing: 0.04em;
    transition: color 0.15s, border-color 0.15s, background 0.15s;
  }

  .refresh-btn:hover { color: var(--text); border-color: var(--border2); background: var(--bg3); }

  /* ── Content ── */
  .content { padding: 28px; }

  /* Ticker cards */
  .ticker-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0,1fr));
    gap: 16px;
    margin-bottom: 28px;
  }

  .ticker-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }

  .ticker-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--green);
    opacity: 0;
    transition: opacity 0.2s;
  }

  .ticker-card.bear::before { background: var(--red); }

  .ticker-card:hover { border-color: var(--border2); }
  .ticker-card:hover::before { opacity: 1; }

  .tc-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 14px;
  }

  .tc-name {
    font-family: var(--font-display);
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.04em;
  }

  .tc-time {
    font-size: 10px;
    color: var(--dim);
    margin-top: 3px;
    font-variant-numeric: tabular-nums;
  }

  .pin-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 4px;
  }

  .pin-badge.bull {
    background: var(--green-bg);
    border: 1px solid var(--green-border);
    color: var(--green);
  }

  .pin-badge.bear {
    background: var(--red-bg);
    border: 1px solid var(--red-border);
    color: var(--red);
  }

  .pin-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
  }

  .pin-badge.bull .pin-dot { background: var(--green); }
  .pin-badge.bear .pin-dot { background: var(--red); }

  .tc-gex-label {
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--dim);
    margin-top: 16px;
    margin-bottom: 4px;
  }

  .tc-gex-value {
    font-family: var(--font-display);
    font-size: 26px;
    font-weight: 700;
    color: var(--text);
    font-variant-numeric: tabular-nums;
    margin-bottom: 16px;
  }

  .tc-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .tc-stat {
    background: var(--bg3);
    border-radius: 6px;
    padding: 9px 11px;
  }

  .tc-stat-label {
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--dim);
    margin-bottom: 3px;
  }

  .tc-stat-val {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    font-variant-numeric: tabular-nums;
  }

  /* ── Heatmap section ── */
  .heatmap-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
  }

  .section-title {
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: 0.04em;
  }

  .section-sub {
    font-size: 10px;
    color: var(--muted);
    margin-top: 2px;
  }

  .tab-strip {
    display: flex;
    gap: 4px;
    background: var(--bg3);
    padding: 3px;
    border-radius: 6px;
    border: 1px solid var(--border);
  }

  .tab-btn {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 5px 16px;
    border-radius: 4px;
    border: none;
    background: transparent;
    color: var(--muted);
    cursor: pointer;
    font-family: var(--font-mono);
    transition: color 0.15s, background 0.15s;
  }

  .tab-btn.active {
    background: var(--bg2);
    color: var(--text);
    border: 1px solid var(--border2);
  }

  .legend {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    color: var(--muted);
  }

  .legend-dot {
    width: 8px; height: 8px;
    border-radius: 2px;
  }

  /* Table */
  .table-wrap {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    background: var(--bg2);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-variant-numeric: tabular-nums;
  }

  thead tr {
    background: var(--bg3);
    border-bottom: 1px solid var(--border);
  }

  th {
    padding: 10px 16px;
    text-align: right;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--dim);
    font-weight: 600;
    white-space: nowrap;
  }

  th:first-child { text-align: left; }

  td {
    padding: 9px 16px;
    text-align: right;
    font-size: 12px;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
  }

  td:first-child {
    text-align: left;
    color: var(--text);
    font-weight: 600;
    font-size: 13px;
  }

  tbody tr:last-child td { border-bottom: none; }

  tbody tr { transition: background 0.1s; }
  tbody tr:hover { background: var(--bg3); }

  tbody tr.highlight { background: rgba(167,139,250,0.05); }
  tbody tr.highlight td:first-child { color: var(--purple); }

  .gex-cell {
    display: inline-flex;
    align-items: center;
    justify-content: flex-end;
    gap: 4px;
    font-size: 12px;
    font-weight: 500;
    min-width: 90px;
  }

  .gex-pos { color: var(--green); }
  .gex-neg { color: var(--red); }
  .gex-hot { color: var(--purple); }

  .bar-bg {
    height: 3px;
    border-radius: 2px;
    background: var(--bg4);
    width: 60px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.3s ease;
  }

  .bar-pos { background: var(--green); }
  .bar-neg { background: var(--red); }
  .bar-hot { background: var(--purple); }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--bg4); border-radius: 4px; }
</style>
</head>
<body>

<!-- ── Sidebar ── -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-mark">
      <div class="logo-icon">
        <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="9" width="3" height="5" rx="1" fill="#090c0f"/>
          <rect x="6.5" y="6" width="3" height="8" rx="1" fill="#090c0f"/>
          <rect x="11" y="2" width="3" height="12" rx="1" fill="#090c0f"/>
        </svg>
      </div>
      <span class="logo-title">GEX</span>
    </div>
    <div class="logo-sub">Dealer Positioning</div>
  </div>

  <div class="sidebar-section" style="margin-top:20px;">
    <div class="sidebar-label">Watchlist</div>
    <div class="ticker-chips">
      <div class="chip active">SPX <span class="x">✕</span></div>
      <div class="chip active">SPY <span class="x">✕</span></div>
      <div class="chip active">QQQ <span class="x">✕</span></div>
      <div class="chip" style="color:var(--dim);border-style:dashed;">+ Add</div>
    </div>
  </div>

  <div class="sidebar-section">
    <div class="sidebar-label">Filters</div>

    <div class="filter-row">
      <div class="filter-top">
        <span class="filter-name">Strike range ±%</span>
        <span class="filter-val" id="range-val">1%</span>
      </div>
      <input type="range" min="1" max="10" value="1" id="range-slider" oninput="document.getElementById('range-val').textContent=this.value+'%'" />
    </div>

    <div class="filter-row">
      <div class="filter-top">
        <span class="filter-name">Min |GEX| ($k)</span>
        <span class="filter-val" id="gex-val">0</span>
      </div>
      <input type="range" min="0" max="500" value="0" id="gex-slider" oninput="document.getElementById('gex-val').textContent=this.value" />
    </div>

    <div class="filter-row">
      <div class="filter-top">
        <span class="filter-name">Min Volume</span>
        <span class="filter-val" id="vol-val">0</span>
      </div>
      <input type="range" min="0" max="50000" step="500" value="0" id="vol-slider" oninput="document.getElementById('vol-val').textContent=Number(this.value).toLocaleString()" />
    </div>

    <div class="filter-row">
      <div class="filter-top">
        <span class="filter-name">Min OI</span>
        <span class="filter-val" id="oi-val">0</span>
      </div>
      <input type="range" min="0" max="100000" step="1000" value="0" id="oi-slider" oninput="document.getElementById('oi-val').textContent=Number(this.value).toLocaleString()" />
    </div>

    <div style="height:1px;background:var(--border);margin:16px 0;"></div>

    <div class="toggle-row" onclick="this.querySelector('.toggle').classList.toggle('on')">
      <div class="toggle on"></div>
      <span class="toggle-label">Show all strikes</span>
    </div>
    <div class="toggle-row" onclick="this.querySelector('.toggle').classList.toggle('on')">
      <div class="toggle"></div>
      <span class="toggle-label">Positive GEX only</span>
    </div>
    <div class="toggle-row" onclick="this.querySelector('.toggle').classList.toggle('on')">
      <div class="toggle"></div>
      <span class="toggle-label">Negative GEX only</span>
    </div>
  </div>

  <div class="sidebar-footer">
    Options data · Delayed 15m<br/>
    © 2026 GEX Dashboard
  </div>
</aside>

<!-- ── Main ── -->
<div class="main">

  <!-- Top nav -->
  <nav class="topnav">
    <div class="nav-left">
      <div class="page-title">Heatmap Tool</div>
      <div class="nav-tabs">
        <div class="nav-tab active">Full Chain</div>
        <div class="nav-tab">Term Structure</div>
        <div class="nav-tab">Flow Summary</div>
        <div class="nav-tab">Settings</div>
      </div>
    </div>
    <div class="nav-right">
      <div class="live-pill"><div class="live-dot"></div>Live</div>
      <span class="timestamp" id="clock">--:--:--</span>
      <button class="refresh-btn">↺ Refresh</button>
    </div>
  </nav>

  <!-- Content -->
  <div class="content">

    <!-- Ticker cards -->
    <div class="ticker-grid">

      <!-- SPX -->
      <div class="ticker-card">
        <div class="tc-header">
          <div>
            <div class="tc-name">SPX</div>
            <div class="tc-time">Last update: 06:49:28</div>
          </div>
          <span class="pin-badge bull"><span class="pin-dot"></span>Bullish Pin</span>
        </div>
        <div class="tc-gex-label">Total Net GEX</div>
        <div class="tc-gex-value">$162,826M</div>
        <div class="tc-stats">
          <div class="tc-stat">
            <div class="tc-stat-label">Gamma Flip</div>
            <div class="tc-stat-val">7,300</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Max OI Strike</div>
            <div class="tc-stat-val">7,300</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Top Call</div>
            <div class="tc-stat-val" style="color:var(--green)">7,325</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Top Put</div>
            <div class="tc-stat-val" style="color:var(--red)">7,295</div>
          </div>
        </div>
      </div>

      <!-- SPY -->
      <div class="ticker-card">
        <div class="tc-header">
          <div>
            <div class="tc-name">SPY</div>
            <div class="tc-time">Last update: 06:49:29</div>
          </div>
          <span class="pin-badge bull"><span class="pin-dot"></span>Bullish Pin</span>
        </div>
        <div class="tc-gex-label">Total Net GEX</div>
        <div class="tc-gex-value">$10,042M</div>
        <div class="tc-stats">
          <div class="tc-stat">
            <div class="tc-stat-label">Gamma Flip</div>
            <div class="tc-stat-val">729</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Max OI Strike</div>
            <div class="tc-stat-val">729</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Top Call</div>
            <div class="tc-stat-val" style="color:var(--green)">734</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Top Put</div>
            <div class="tc-stat-val" style="color:var(--red)">728</div>
          </div>
        </div>
      </div>

      <!-- QQQ -->
      <div class="ticker-card bear">
        <div class="tc-header">
          <div>
            <div class="tc-name">QQQ</div>
            <div class="tc-time">Last update: 06:49:30</div>
          </div>
          <span class="pin-badge bear"><span class="pin-dot"></span>Bearish Pin</span>
        </div>
        <div class="tc-gex-label">Total Net GEX</div>
        <div class="tc-gex-value">$118.7M</div>
        <div class="tc-stats">
          <div class="tc-stat">
            <div class="tc-stat-label">Gamma Flip</div>
            <div class="tc-stat-val">705</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Max OI Strike</div>
            <div class="tc-stat-val">706</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Top Call</div>
            <div class="tc-stat-val" style="color:var(--green)">710</div>
          </div>
          <div class="tc-stat">
            <div class="tc-stat-label">Top Put</div>
            <div class="tc-stat-val" style="color:var(--red)">702</div>
          </div>
        </div>
      </div>

    </div>

    <!-- Heatmap table -->
    <div class="heatmap-header">
      <div>
        <div class="section-title">Full Chain — Dealer GEX</div>
        <div class="section-sub">Strike-level gamma exposure, sorted by absolute GEX</div>
      </div>
      <div style="display:flex;align-items:center;gap:16px;">
        <div class="legend">
          <div class="legend-item"><div class="legend-dot" style="background:var(--green)"></div> Positive</div>
          <div class="legend-item"><div class="legend-dot" style="background:var(--red)"></div> Negative</div>
          <div class="legend-item"><div class="legend-dot" style="background:var(--purple)"></div> Dominant</div>
        </div>
        <div class="tab-strip">
          <button class="tab-btn active" onclick="switchTab(this,'SPX')">SPX</button>
          <button class="tab-btn" onclick="switchTab(this,'SPY')">SPY</button>
          <button class="tab-btn" onclick="switchTab(this,'QQQ')">QQQ</button>
        </div>
      </div>
    </div>

    <div class="table-wrap">
      <table id="gex-table">
        <thead>
          <tr>
            <th>Strike</th>
            <th>Volume</th>
            <th>Open Interest</th>
            <th>GEX ($k)</th>
            <th>Exposure Bar</th>
          </tr>
        </thead>
        <tbody id="gex-tbody"></tbody>
      </table>
    </div>

  </div>
</div>

<script>
  const DATA = {
    SPX: [
      { strike: 7280, vol: 11114, oi: 14963, gex: -101345 },
      { strike: 7285, vol: 5316,  oi: 6227,  gex: -44444  },
      { strike: 7290, vol: 10911, oi: 17756, gex: -198226 },
      { strike: 7295, vol: 6313,  oi: 10013, gex: -217335 },
      { strike: 7300, vol: 52920, oi: 101617,gex: 469052  },
      { strike: 7305, vol: 7024,  oi: 6896,  gex: -46914  },
      { strike: 7310, vol: 12733, oi: 18630, gex: 256120  },
      { strike: 7315, vol: 8740,  oi: 6744,  gex: -14594  },
      { strike: 7320, vol: 15598, oi: 16459, gex: 37424   },
      { strike: 7325, vol: 20425, oi: 37819, gex: 237477  },
    ],
    SPY: [
      { strike: 725, vol: 51506, oi: 36191, gex: 30814   },
      { strike: 726, vol: 6461,  oi: 14740, gex: -27609  },
      { strike: 727, vol: 638,   oi: 35261, gex: -31557  },
      { strike: 728, vol: 1111,  oi: 51702, gex: -182128 },
      { strike: 729, vol: 5557,  oi: 26420, gex: 10380   },
      { strike: 730, vol: 7196,  oi: 29734, gex: -50948  },
      { strike: 731, vol: 2306,  oi: 46308, gex: -8135   },
      { strike: 732, vol: 375,   oi: 21539, gex: 12320   },
      { strike: 733, vol: 850,   oi: 59951, gex: -107134 },
      { strike: 734, vol: 335,   oi: 17097, gex: -122896 },
    ],
    QQQ: [
      { strike: 699, vol: 1443,  oi: 9410,  gex: -9640   },
      { strike: 700, vol: 12550, oi: 10769, gex: -8550   },
      { strike: 701, vol: 8492,  oi: 20660, gex: -16399  },
      { strike: 702, vol: 6173,  oi: 16110, gex: -34880  },
      { strike: 703, vol: 9503,  oi: 21353, gex: -9447   },
      { strike: 704, vol: 8241,  oi: 15434, gex: -20724  },
      { strike: 705, vol: 4128,  oi: 23524, gex: 149621  },
      { strike: 706, vol: 5778,  oi: 14780, gex: -21787  },
      { strike: 707, vol: 20068, oi: 36145, gex: -112785 },
      { strike: 708, vol: 14199, oi: 24145, gex: -9640   },
    ]
  };

  let currentTicker = 'SPX';

  function renderTable(ticker) {
    const rows = DATA[ticker];
    const maxAbs = Math.max(...rows.map(r => Math.abs(r.gex)));
    const dominant = rows.reduce((a, b) => Math.abs(a.gex) > Math.abs(b.gex) ? a : b);
    const tbody = document.getElementById('gex-tbody');
    tbody.innerHTML = rows.map(r => {
      const isHot = r.strike === dominant.strike;
      const pct = Math.round(Math.abs(r.gex) / maxAbs * 100);
      const cls = isHot ? 'gex-hot' : r.gex > 0 ? 'gex-pos' : 'gex-neg';
      const barCls = isHot ? 'bar-hot' : r.gex > 0 ? 'bar-pos' : 'bar-neg';
      const sign = r.gex > 0 ? '+' : '';
      return `<tr class="${isHot ? 'highlight' : ''}">
        <td>${r.strike.toLocaleString()}</td>
        <td>${r.vol.toLocaleString()}</td>
        <td>${r.oi.toLocaleString()}</td>
        <td><span class="gex-cell ${cls}">${sign}${r.gex.toLocaleString()}</span></td>
        <td><div class="bar-bg"><div class="bar-fill ${barCls}" style="width:${pct}%"></div></div></td>
      </tr>`;
    }).join('');
  }

  function switchTab(btn, ticker) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentTicker = ticker;
    renderTable(ticker);
  }

  function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString('en-US', { hour12: false });
  }

  renderTable('SPX');
  updateClock();
  setInterval(updateClock, 1000);

  document.querySelector('.nav-tabs').addEventListener('click', e => {
    const t = e.target.closest('.nav-tab');
    if (!t) return;
    document.querySelectorAll('.nav-tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
  });
</script>
</body>
</html>
