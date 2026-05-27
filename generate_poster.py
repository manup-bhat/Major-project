#!/usr/bin/env python3
"""
3D AR/VR Interactive Poster Generator v3
==========================================
Fixes:
  - Scene 1: NHI Graph restructured as hub-spoke (GitHub, Azure, KeyVault hubs)
    with clear group labels and meaningful connections - instantly understandable
  - Scene 3: Interactive pipeline with Next/Prev buttons, phase highlighting,
    info panel showing what each agent does on click
  - Particles: Softer colors, no white blowout, better visibility

Author: Manu Prakash Bhat · 1RV22IS035 · ISE · RVCE
"""

from pathlib import Path
import webbrowser

OUTPUT = Path(__file__).parent / "poster.html"

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>NHI Governance — 3D AR/VR Interactive Poster</title>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.164.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.164.0/examples/jsm/"
  }
}
</script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#050b18;--cd:#0a1525;--bd:#1a3a6b;--c1:#00d4ff;--c2:#7c3aed;--c3:#10b981;--c4:#f59e0b;--c5:#ef4444;--c6:#ec4899;--tx:#e2e8f0;--dm:#94a3b8}
body{background:var(--bg);color:var(--tx);font-family:'Inter',system-ui,sans-serif;line-height:1.5}
.poster{max-width:1200px;margin:0 auto;padding:0 20px 40px}

/* HEADER */
.hdr{background:linear-gradient(135deg,#06091e,#0b1845,#06091e);border-bottom:3px solid var(--c1);padding:28px 40px 22px;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:24px;margin-bottom:16px}
.logo{width:64px;height:64px;background:linear-gradient(135deg,#7c3aed,#00d4ff);border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:'JetBrains Mono',monospace;font-size:17px;font-weight:700;color:#fff;box-shadow:0 0 20px rgba(0,212,255,.35)}
.logo small{font-size:7.5px;font-weight:400;letter-spacing:1.5px}
.hdr-mid .chips{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:6px}
.chip{border-radius:20px;padding:2px 10px;font-size:10px;border:1px solid}
.ch-c{border-color:var(--c1);color:var(--c1)}.ch-v{border-color:var(--c2);color:#c4b5fd}.ch-g{border-color:var(--c3);color:var(--c3)}
.hdr-mid h1{font-size:24px;font-weight:900;background:linear-gradient(90deg,#fff,var(--c1),var(--c2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.2}
.hdr-mid .sub{font-size:10.5px;color:var(--dm);margin-top:4px}
.hdr-right{text-align:right}
.hdr-right .org{font-size:20px;font-weight:900;color:var(--c4);letter-spacing:2px}
.hdr-right .org-sub{font-size:9.5px;color:var(--dm)}

/* SCENE SECTION */
.scene-section{margin-bottom:16px}
.scene-header{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.scene-num{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:13px;color:#fff;flex-shrink:0}
.scene-header h2{font-size:14px;font-weight:800;color:var(--tx)}
.scene-header .scene-tag{font-size:9px;padding:2px 8px;border-radius:12px;font-weight:600;margin-left:8px}

.scene-wrap{display:grid;grid-template-columns:1fr 280px;gap:12px}
.scene-wrap.wide{grid-template-columns:1fr 280px}
.canvas-box{background:#020810;border:1px solid var(--bd);border-radius:10px;position:relative;overflow:hidden;min-height:340px}
.canvas-box canvas{display:block;width:100%!important;height:100%!important}
.canvas-hint{position:absolute;top:8px;left:10px;font-size:9px;color:var(--dm);background:rgba(0,0,0,.6);padding:2px 7px;border-radius:4px;z-index:5}

/* LEGEND PANEL */
.legend{background:var(--cd);border:1px solid var(--bd);border-radius:10px;padding:14px 16px;font-size:10px;overflow-y:auto;max-height:400px}
.legend h3{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--c1);margin-bottom:8px}
.legend-item{display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid rgba(26,58,107,.3)}
.legend-item:last-child{border-bottom:none}
.lg-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.lg-sq{width:10px;height:10px;border-radius:2px;flex-shrink:0}
.legend-item .lt{color:var(--tx);font-weight:600}
.legend-item .ld{color:var(--dm);font-size:9px;margin-top:1px}
.legend-sep{height:1px;background:var(--bd);margin:8px 0}
.legend p{color:var(--dm);font-size:9.5px;line-height:1.4;margin-top:6px}
.legend .demo-tip{background:rgba(124,58,237,.08);border:1px solid rgba(124,58,237,.2);border-radius:6px;padding:6px 8px;margin-top:8px;font-size:9px;color:#c4b5fd}
.legend .demo-tip strong{color:var(--c2)}

/* PIPELINE CONTROLS */
.pipeline-controls{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:8px;z-index:20}
.pipe-btn{padding:6px 14px;border:1px solid var(--bd);border-radius:6px;background:rgba(10,21,37,.9);color:var(--tx);font:700 10px 'Inter',sans-serif;cursor:pointer;transition:all .2s}
.pipe-btn:hover{background:var(--c2);border-color:var(--c2);color:#fff}
.pipe-btn.active{background:var(--c2);border-color:var(--c2);color:#fff}
.pipe-btn:disabled{opacity:0.3;cursor:not-allowed}
.pipe-status{font:700 10px 'JetBrains Mono',monospace;color:var(--c1);background:rgba(0,0,0,.7);padding:4px 10px;border-radius:4px;min-width:120px;text-align:center}
.pipe-info{position:absolute;top:8px;right:10px;background:rgba(10,21,37,.92);border:1px solid var(--bd);border-radius:8px;padding:8px 12px;max-width:200px;z-index:20;font-size:9.5px}
.pipe-info .pi-name{font:700 11px 'JetBrains Mono',monospace;margin-bottom:3px}
.pipe-info .pi-desc{color:var(--dm);line-height:1.35}

/* BOTTOM GRID */
.bottom-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}
.card{background:var(--cd);border:1px solid var(--bd);border-radius:10px;padding:14px 16px;position:relative;overflow:hidden}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--c1),var(--c2))}
.card.gr::before{background:linear-gradient(90deg,var(--c3),#34d399)}
.card.am::before{background:linear-gradient(90deg,var(--c4),#fbbf24)}
.ct{font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px}
.card .ct{color:var(--c1)}.card.gr .ct{color:var(--c3)}.card.am .ct{color:var(--c4)}

/* STATS ROW */
.stats-row{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:12px}
.stat-box{background:rgba(0,0,0,.3);border:1px solid var(--bd);border-radius:7px;padding:8px;text-align:center}
.stat-box .sn{font-size:22px;font-weight:900;background:linear-gradient(135deg,var(--c1),var(--c2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.stat-box .sl{font-size:8px;color:var(--dm);margin-top:2px}

/* BADGES */
.bg{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}
.badge{padding:2px 8px;border-radius:14px;font-size:9px;font-weight:600;border:1px solid}
.b-c{border-color:var(--c1);color:var(--c1)}.b-v{border-color:var(--c2);color:#c4b5fd}
.b-g{border-color:var(--c3);color:var(--c3)}.b-a{border-color:var(--c4);color:var(--c4)}
.b-r{border-color:var(--c5);color:#fca5a5}.b-p{border-color:var(--c6);color:#f9a8d4}

/* TEAM */
.team-row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}
.tc{background:rgba(0,0,0,.25);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;display:flex;align-items:center;gap:9px}
.tc-av{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px;color:#fff;flex-shrink:0}
.tc .tn{font-size:11px;font-weight:700}.tc .tr{font-size:9px;color:var(--dm);margin-top:1px}
.tc .tid{font-size:9px;color:var(--c1);font-family:'JetBrains Mono',monospace;margin-top:1px}

/* FOOTER */
.ft{background:rgba(0,0,0,.4);border-top:1px solid var(--bd);padding:12px 40px;display:flex;justify-content:space-between;align-items:center;margin-top:16px}
.ft .fl{font-size:10px;color:var(--dm)}.ft .fr{font-size:9.5px;color:var(--c1);font-family:'JetBrains Mono',monospace}

/* SCORE BAR */
.sb-w{margin-top:4px}.sb-r{display:flex;justify-content:space-between;font-size:9.5px;margin-bottom:2px}
.sb{height:5px;background:rgba(255,255,255,.05);border-radius:8px;overflow:hidden}
.sf{height:100%;border-radius:8px}
</style>
</head>
<body>
<div class="poster">

<!-- HEADER -->
<header class="hdr">
  <div class="logo">NHI<br/><small>GOV&middot;AI</small></div>
  <div class="hdr-mid">
    <div class="chips">
      <span class="chip ch-c">Dept. of Information Science &amp; Engineering</span>
      <span class="chip ch-v">2025&ndash;2026</span>
      <span class="chip ch-g">B.E. Final Year Project</span>
    </div>
    <h1>Non-Human Identity Governance Agent for DevSecOps</h1>
    <div class="sub">9 Agents &middot; 11 NHI Types &middot; 3 ML Models &middot; 11 OPA/Rego Policies &middot; 13+ APIs</div>
  </div>
  <div class="hdr-right">
    <div class="org">HONEYWELL</div>
    <div class="org-sub">Connected Enterprise — IA Division</div>
  </div>
</header>

<!-- STATS -->
<div class="stats-row">
  <div class="stat-box"><div class="sn">9,680+</div><div class="sl">Lines of Code</div></div>
  <div class="stat-box"><div class="sn">9</div><div class="sl">Autonomous Agents</div></div>
  <div class="stat-box"><div class="sn">11</div><div class="sl">NHI Types Governed</div></div>
  <div class="stat-box"><div class="sn">3</div><div class="sl">ML Models (scikit-learn)</div></div>
  <div class="stat-box"><div class="sn">11</div><div class="sl">OPA/Rego Policies</div></div>
</div>

<!-- ═══════════════════════════════════════════════ -->
<!-- SCENE 1: NHI IDENTITY GRAPH (Hub-Spoke)        -->
<!-- ═══════════════════════════════════════════════ -->
<div class="scene-section">
  <div class="scene-header">
    <div class="scene-num" style="background:linear-gradient(135deg,var(--c1),var(--c2))">1</div>
    <h2>NHI Identity Relationship Graph — Platform View</h2>
    <span class="scene-tag" style="background:rgba(0,212,255,.1);color:var(--c1);border:1px solid rgba(0,212,255,.3)">Hub-Spoke · Labeled · Interactive</span>
  </div>
  <div class="scene-wrap">
    <div class="canvas-box" id="scene-graph">
      <span class="canvas-hint">🖱 Drag to orbit · Scroll to zoom · Hubs = Platforms, Satellites = NHI Types</span>
    </div>
    <div class="legend">
      <h3>Platform Hubs (Large Cubes)</h3>
      <div class="legend-item"><div class="lg-sq" style="background:#3b82f6"></div><div><div class="lt">GitHub</div><div class="ld">PATs, Deploy Keys, Actions Secrets</div></div></div>
      <div class="legend-item"><div class="lg-sq" style="background:#8b5cf6"></div><div><div class="lt">Azure AD</div><div class="ld">Service Principals, Client Secrets</div></div></div>
      <div class="legend-item"><div class="lg-sq" style="background:#06b6d4"></div><div><div class="lt">Key Vault</div><div class="ld">Secrets, Certificates, Keys</div></div></div>
      <div class="legend-item"><div class="lg-sq" style="background:#10b981"></div><div><div class="lt">SSL/TLS Endpoints</div><div class="ld">Certificates with expiry</div></div></div>
      <div class="legend-sep"></div>
      <h3>NHI Nodes (Spheres around hubs)</h3>
      <div class="legend-item"><div class="lg-dot" style="background:#f59e0b"></div><div><div class="lt">PAT</div><div class="ld">Score: 78-91 · HIGH/CRITICAL</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#f97316"></div><div><div class="lt">Deploy Key (Write)</div><div class="ld">Score: 55-88 · HIGH</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#ef4444"></div><div><div class="lt">Actions Secret</div><div class="ld">Score: 45-73 · MEDIUM/HIGH</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#00d4ff"></div><div><div class="lt">Service Principal</div><div class="ld">Score: 38-72</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#a78bfa"></div><div><div class="lt">KV Secret</div><div class="ld">Score: 40-75</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#10b981"></div><div><div class="lt">SSL Certificate</div><div class="ld">Score: 15-82</div></div></div>
      <div class="legend-sep"></div>
      <h3>Visual Encoding</h3>
      <p><strong>Sphere size</strong> = Risk score. <strong>Red glow</strong> = Critical (≥70).<br/>
      <strong>Lines</strong> = "belongs to" / "accesses" relationship.<br/>
      <strong>Ring</strong> around hub = platform boundary.</p>
      <div class="demo-tip"><strong>Demo tip:</strong> "4 platform hubs in the center (GitHub, Azure AD, Key Vault, SSL). Each NHI orbits its source platform. Size = risk. You can instantly see which platform has the riskiest identities."</div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════ -->
<!-- SCENE 2: RISK SCORE TERRAIN                    -->
<!-- ═══════════════════════════════════════════════ -->
<div class="scene-section">
  <div class="scene-header">
    <div class="scene-num" style="background:linear-gradient(135deg,var(--c5),var(--c4))">2</div>
    <h2>Risk Scoring Formula — 3D Terrain</h2>
    <span class="scene-tag" style="background:rgba(239,68,68,.1);color:var(--c5);border:1px solid rgba(239,68,68,.3)">Heightmap · Vertex Colors · 3D Terrain</span>
  </div>
  <div class="scene-wrap">
    <div class="canvas-box" id="scene-terrain" style="min-height:300px">
      <span class="canvas-hint">🖱 Orbit · Height = Risk Score · Color = Severity</span>
    </div>
    <div class="legend">
      <h3>Axes — Scoring Formula</h3>
      <div class="legend-item"><div class="lg-sq" style="background:var(--c1)"></div><div><div class="lt">X-Axis: Identity Age</div><div class="ld">0→365 days · Max 40 points</div></div></div>
      <div class="legend-item"><div class="lg-sq" style="background:var(--c2)"></div><div><div class="lt">Z-Axis: Privilege Scope</div><div class="ld">0→7 high-priv scopes · Max 20 pts</div></div></div>
      <div class="legend-item"><div class="lg-sq" style="background:var(--c4)"></div><div><div class="lt">Y-Height: Total Risk Score</div><div class="ld">Combined 0–100</div></div></div>
      <div class="legend-sep"></div>
      <h3>Color = Severity</h3>
      <div class="legend-item"><div class="lg-dot" style="background:#10b981"></div><div><div class="lt">Green (0–29) LOW</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#f59e0b"></div><div><div class="lt">Amber (30–49) MEDIUM</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#f97316"></div><div><div class="lt">Orange (50–69) HIGH</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#ef4444"></div><div><div class="lt">Red (70–100) CRITICAL</div></div></div>
      <div class="legend-sep"></div>
      <p><strong style="color:var(--c5)">Red plane (Y=70)</strong> = Auto-rotation<br/>
      <strong style="color:var(--c4)">Amber plane (Y=50)</strong> = LLM enrichment</p>
      <div class="demo-tip"><strong>Demo tip:</strong> "Older + more privileged = higher terrain. Red plateau at 70 triggers auto-rotation."</div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════ -->
<!-- SCENE 3: INTERACTIVE PIPELINE                  -->
<!-- ═══════════════════════════════════════════════ -->
<div class="scene-section">
  <div class="scene-header">
    <div class="scene-num" style="background:linear-gradient(135deg,var(--c2),var(--c6))">3</div>
    <h2>9-Agent Pipeline — Interactive Walkthrough</h2>
    <span class="scene-tag" style="background:rgba(124,58,237,.1);color:#c4b5fd;border:1px solid rgba(124,58,237,.3)">Click Next/Prev · Phase-by-Phase · Data Flow</span>
  </div>
  <div class="scene-wrap wide">
    <div class="canvas-box" id="scene-pipeline" style="min-height:320px">
      <span class="canvas-hint">🖱 Orbit · Use ◀ Next ▶ to step through pipeline phases</span>
      <!-- Interactive controls overlay -->
      <div class="pipeline-controls">
        <button class="pipe-btn" id="pipe-prev" disabled>◀ PREV</button>
        <div class="pipe-status" id="pipe-status">Phase 1 / 4</div>
        <button class="pipe-btn" id="pipe-next">NEXT ▶</button>
      </div>
      <!-- Info panel -->
      <div class="pipe-info" id="pipe-info">
        <div class="pi-name" id="pipe-info-name" style="color:var(--c1)">DISCOVERY</div>
        <div class="pi-desc" id="pipe-info-desc">5 agents scan GitHub, Azure AD, Key Vault, and SSL endpoints to discover all NHI types.</div>
      </div>
    </div>
    <div class="legend">
      <h3>Pipeline Phases (Navigate with buttons)</h3>
      <div class="legend-item"><div class="lg-dot" style="background:#00d4ff"></div><div><div class="lt">Phase 1: DISCOVERY</div><div class="ld">cert, github, azure_sp, keyvault, monitor</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#10b981"></div><div><div class="lt">Phase 2: SCORING</div><div class="ld">risk_scorer → 0-100 weighted score</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#f59e0b"></div><div><div class="lt">Phase 3: POLICY + ML</div><div class="ld">11 OPA rules + Isolation Forest</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#ec4899"></div><div><div class="lt">Phase 4: OUTPUT</div><div class="ld">report_gen → HTML, JSON, email</div></div></div>
      <div class="legend-sep"></div>
      <h3>Interaction</h3>
      <p><strong>Click NEXT/PREV</strong> to advance phases. Active phase glows and shows info. Particles flow only through the active section.<br/><br/>
      <strong>Double-click</strong> any agent node to jump directly to its phase.</p>
      <div class="demo-tip"><strong>Demo tip:</strong> "Let me walk you through each phase. [click Next] First, 5 agents discover identities. [click Next] Then scoring assigns 0-100. [click Next] Policy and ML analyze. [click Next] Finally, reports are generated."</div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════ -->
<!-- SCENE 4: ML ANOMALY 3D SCATTER                 -->
<!-- ═══════════════════════════════════════════════ -->
<div class="scene-section">
  <div class="scene-header">
    <div class="scene-num" style="background:linear-gradient(135deg,var(--c3),#34d399)">4</div>
    <h2>ML Isolation Forest — 3D Anomaly Space</h2>
    <span class="scene-tag" style="background:rgba(16,185,129,.1);color:var(--c3);border:1px solid rgba(16,185,129,.3)">Scatter Plot · Anomalies · 9-Dim Features</span>
  </div>
  <div class="scene-wrap">
    <div class="canvas-box" id="scene-scatter" style="min-height:320px">
      <span class="canvas-hint">🖱 Orbit · Red pulsing = Anomalies ML caught</span>
    </div>
    <div class="legend">
      <h3>Axes (3 of 9 features)</h3>
      <div class="legend-item"><div class="lg-sq" style="background:var(--c1)"></div><div><div class="lt">X: Risk Score (0–100)</div></div></div>
      <div class="legend-item"><div class="lg-sq" style="background:var(--c3)"></div><div><div class="lt">Y: Identity Age (days)</div></div></div>
      <div class="legend-item"><div class="lg-sq" style="background:var(--c2)"></div><div><div class="lt">Z: Privilege Scope (0–7)</div></div></div>
      <div class="legend-sep"></div>
      <h3>Point Types</h3>
      <div class="legend-item"><div class="lg-dot" style="background:#10b981"></div><div><div class="lt">Normal</div><div class="ld">Within distribution</div></div></div>
      <div class="legend-item"><div class="lg-dot" style="background:#ef4444;box-shadow:0 0 6px #ef4444"></div><div><div class="lt">Anomaly (ML-detected)</div><div class="ld">Outlier score ≥ 0.6</div></div></div>
      <div class="legend-sep"></div>
      <p>Isolation Forest: 200 trees, contamination=0.1, 9 features.</p>
      <div class="sb-w"><div class="sb-r"><span>Accuracy</span><span style="color:var(--c3)">~94%</span></div><div class="sb"><div class="sf" style="width:94%;background:linear-gradient(90deg,#10b981,#34d399)"></div></div></div>
      <div class="sb-w"><div class="sb-r"><span>R² forecast</span><span style="color:var(--c1)">0.89+</span></div><div class="sb"><div class="sf" style="width:89%;background:linear-gradient(90deg,#00d4ff,#38bdf8)"></div></div></div>
      <div class="demo-tip"><strong>Demo tip:</strong> "Red = anomalies (dormant PATs, over-privileged keys). ML catches what rules miss."</div>
    </div>
  </div>
</div>

<!-- BOTTOM SECTION -->
<div class="bottom-grid">
  <div class="card">
    <div class="ct" style="color:var(--c1)">Technology Stack</div>
    <div class="bg"><span class="badge b-c">Python 3.11</span><span class="badge b-v">LangChain</span><span class="badge b-a">Flask</span><span class="badge b-g">scikit-learn</span><span class="badge b-p">OPA/Rego</span></div>
    <div style="font-size:9px;font-weight:700;color:var(--dm);margin-top:8px;text-transform:uppercase;letter-spacing:.5px">Frontend</div>
    <div class="bg"><span class="badge b-c">React 18</span><span class="badge b-v">TypeScript</span><span class="badge b-a">Vite</span><span class="badge b-g">Recharts</span><span class="badge b-p">TailwindCSS</span></div>
  </div>
  <div class="card gr">
    <div class="ct" style="color:var(--c3)">Key Results</div>
    <div style="font-size:10.5px">
      <div style="padding:3px 0;border-bottom:1px solid rgba(26,58,107,.3)">✓ <strong>360°</strong> NHI visibility across 4 platforms</div>
      <div style="padding:3px 0;border-bottom:1px solid rgba(26,58,107,.3)">✓ <strong>&lt;2 min</strong> full scan-to-report</div>
      <div style="padding:3px 0;border-bottom:1px solid rgba(26,58,107,.3)">✓ <strong>3 dormant PATs</strong> caught by ML</div>
      <div style="padding:3px 0;border-bottom:1px solid rgba(26,58,107,.3)">✓ <strong>R²>0.89</strong> 30-day forecast</div>
      <div style="padding:3px 0">✓ <strong>React</strong> real-time dashboard</div>
    </div>
  </div>
  <div class="card am">
    <div class="ct" style="color:var(--c4)">Future Scope</div>
    <div style="font-size:10px">
      <div style="padding:3px 0;border-bottom:1px solid rgba(26,58,107,.3)"><strong style="color:var(--c6)">GNN-based Risk Propagation</strong></div>
      <div style="padding:3px 0;border-bottom:1px solid rgba(26,58,107,.3)"><strong style="color:var(--c1)">Multi-Cloud Federation</strong></div>
      <div style="padding:3px 0;border-bottom:1px solid rgba(26,58,107,.3)"><strong style="color:var(--c3)">Zero-Trust Policy Engine</strong></div>
      <div style="padding:3px 0"><strong style="color:var(--c4)">Automated Remediation</strong></div>
    </div>
  </div>
</div>

<!-- TEAM -->
<div class="team-row">
  <div class="tc" style="border-color:rgba(245,158,11,.3)">
    <div class="tc-av" style="background:linear-gradient(135deg,#f59e0b,#fbbf24)">MM</div>
    <div><div class="tn">Prof. Merin Meleet</div><div class="tr">Internal Guide · Asst. Professor, ISE</div><div class="tid">RV College of Engineering</div></div>
  </div>
  <div class="tc">
    <div class="tc-av" style="background:linear-gradient(135deg,#7c3aed,#00d4ff)">MB</div>
    <div><div class="tn">Manu Prakash Bhat</div><div class="tr">Developer — Full Stack · ML · DevSecOps</div><div class="tid">1RV22IS035 · Dept. of ISE</div></div>
  </div>
  <div class="tc" style="border-color:rgba(0,212,255,.3)">
    <div class="tc-av" style="background:linear-gradient(135deg,#0ea5e9,#00d4ff)">TR</div>
    <div><div class="tn">Tejeshwar Rao</div><div class="tr">External Guide · Manager — DevSecOps</div><div class="tid">Honeywell · IA Division</div></div>
  </div>
</div>

<footer class="ft">
  <div class="fl"><strong style="color:var(--tx)">Dept. of ISE</strong> · RV College of Engineering, Bengaluru · 2025–2026</div>
  <div class="fr">NHI-GOVERNANCE v3.0 · MAY 2026</div>
</footer>
</div>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--              THREE.JS 3D SCENES                               -->
<!-- ═══════════════════════════════════════════════════════════════ -->
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';


// ─── Utilities ─────────────────────────────
function makeRenderer(container) {
  const r = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  r.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  r.setSize(container.clientWidth, container.clientHeight);
  r.toneMapping = THREE.ACESFilmicToneMapping;
  r.toneMappingExposure = 1.0;
  container.appendChild(r.domElement);
  return r;
}
function makeCSS2D(container) {
  const r = new CSS2DRenderer();
  r.setSize(container.clientWidth, container.clientHeight);
  r.domElement.style.position = 'absolute';
  r.domElement.style.top = '0';
  r.domElement.style.left = '0';
  r.domElement.style.pointerEvents = 'none';
  container.appendChild(r.domElement);
  return r;
}
function makeLabel(text, color='#e2e8f0', fontSize='9px', bold=true) {
  const div = document.createElement('div');
  div.style.cssText = `color:${color};font:${bold?'700':'400'} ${fontSize} 'JetBrains Mono',monospace;text-shadow:0 0 6px rgba(0,0,0,1),0 1px 3px rgba(0,0,0,.9);white-space:nowrap;pointer-events:none;padding:1px 4px;border-radius:3px;background:rgba(5,11,24,.6)`;
  div.textContent = text;
  return new CSS2DObject(div);
}


// ═══════════════════════════════════════════════════════════════
// SCENE 1: NHI IDENTITY GRAPH (Hub-Spoke Layout)
// Hubs = Platforms (GitHub, Azure AD, Key Vault, SSL)
// Spokes = NHI types orbiting their source platform
// ═══════════════════════════════════════════════════════════════
(function() {
  const container = document.getElementById('scene-graph');
  if (!container) return;
  const renderer = makeRenderer(container);
  const css2d = makeCSS2D(container);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020810);

  const camera = new THREE.PerspectiveCamera(55, container.clientWidth/container.clientHeight, 0.1, 200);
  camera.position.set(0, 18, 30);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.25;

  // Lights
  scene.add(new THREE.AmbientLight(0x445566, 0.8));
  const dl = new THREE.DirectionalLight(0xffffff, 0.7); dl.position.set(10,20,10); scene.add(dl);

  // ─── PLATFORM HUBS (4 large cubes at cardinal directions) ───
  const PLATFORMS = [
    { name: 'GitHub', color: 0x3b82f6, pos: [-10, 0, 0],
      nhis: [
        { name: 'PAT (repo,workflow)', risk: 85, color: 0xf59e0b },
        { name: 'PAT (admin:org)', risk: 91, color: 0xf59e0b },
        { name: 'Deploy Key [Write]', risk: 78, color: 0xf97316 },
        { name: 'Deploy Key [Read]', risk: 22, color: 0x22d3ee },
        { name: 'Actions Secret', risk: 62, color: 0xef4444 },
        { name: 'Actions Secret', risk: 73, color: 0xef4444 },
      ]},
    { name: 'Azure AD', color: 0x8b5cf6, pos: [10, 0, 0],
      nhis: [
        { name: 'Service Principal', risk: 72, color: 0x00d4ff },
        { name: 'Service Principal', risk: 55, color: 0x00d4ff },
        { name: 'Client Secret', risk: 78, color: 0xfb923c },
        { name: 'Client Secret', risk: 60, color: 0xfb923c },
        { name: 'Managed Identity', risk: 12, color: 0x6ee7b7 },
      ]},
    { name: 'Key Vault', color: 0x06b6d4, pos: [0, 0, -10],
      nhis: [
        { name: 'KV Secret', risk: 75, color: 0xa78bfa },
        { name: 'KV Secret', risk: 55, color: 0xa78bfa },
        { name: 'KV Certificate', risk: 35, color: 0xc084fc },
        { name: 'KV Key', risk: 42, color: 0x818cf8 },
      ]},
    { name: 'SSL/TLS', color: 0x10b981, pos: [0, 0, 10],
      nhis: [
        { name: 'SSL Cert (CRITICAL)', risk: 82, color: 0xef4444 },
        { name: 'SSL Cert (WARNING)', risk: 65, color: 0xf59e0b },
        { name: 'SSL Cert (OK)', risk: 15, color: 0x10b981 },
      ]},
  ];

  const hubMeshes = [];
  PLATFORMS.forEach(plat => {
    // Hub - larger rounded box
    const hubGeo = new THREE.BoxGeometry(2.5, 2.5, 2.5);
    const hubMat = new THREE.MeshPhongMaterial({
      color: plat.color, emissive: plat.color, emissiveIntensity: 0.25,
      transparent: true, opacity: 0.85
    });
    const hub = new THREE.Mesh(hubGeo, hubMat);
    hub.position.set(...plat.pos);
    scene.add(hub);
    hubMeshes.push(hub);

    // Hub label (large, clear)
    const hlabel = makeLabel(plat.name, '#ffffff', '11px');
    hlabel.position.set(0, 2.2, 0);
    hub.add(hlabel);

    // Platform ring
    const ringGeo = new THREE.RingGeometry(5.5, 5.8, 32);
    const ringMat = new THREE.MeshBasicMaterial({ color: plat.color, transparent: true, opacity: 0.15, side: THREE.DoubleSide });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI/2;
    ring.position.set(...plat.pos);
    ring.position.y = -0.5;
    scene.add(ring);

    // NHI nodes orbiting this hub
    plat.nhis.forEach((nhi, i) => {
      const angle = (i / plat.nhis.length) * Math.PI * 2;
      const radius = 4.5;
      const scale = 0.35 + (nhi.risk / 100) * 0.55;

      const nodeGeo = new THREE.SphereGeometry(1, 14, 10);
      const nodeMat = new THREE.MeshPhongMaterial({
        color: nhi.color,
        emissive: nhi.risk >= 70 ? nhi.color : 0x000000,
        emissiveIntensity: nhi.risk >= 70 ? 0.5 : 0,
        shininess: 50
      });
      const node = new THREE.Mesh(nodeGeo, nodeMat);
      node.position.set(
        plat.pos[0] + Math.cos(angle) * radius,
        plat.pos[1] + (Math.random()-0.5) * 2,
        plat.pos[2] + Math.sin(angle) * radius
      );
      node.scale.setScalar(scale);
      scene.add(node);

      // Node label with name + score
      const severity = nhi.risk >= 70 ? 'CRIT' : nhi.risk >= 50 ? 'HIGH' : nhi.risk >= 30 ? 'MED' : 'LOW';
      const labelColor = nhi.risk >= 70 ? '#ef4444' : nhi.risk >= 50 ? '#f97316' : '#e2e8f0';
      const nlabel = makeLabel(`${nhi.name} [${nhi.risk}]`, labelColor, '7.5px');
      nlabel.position.set(0, scale + 0.4, 0);
      node.add(nlabel);

      // Edge from node to hub
      const edgeGeo = new THREE.BufferGeometry().setFromPoints([
        node.position.clone(),
        new THREE.Vector3(...plat.pos)
      ]);
      const edgeMat = new THREE.LineBasicMaterial({ color: plat.color, transparent: true, opacity: 0.25 });
      scene.add(new THREE.Line(edgeGeo, edgeMat));
    });
  });

  // Cross-platform connections (SP → Key Vault, PAT → Repo implied)
  const crossEdgeMat = new THREE.LineDashedMaterial({ color: 0xf59e0b, dashSize: 0.5, gapSize: 0.3, transparent: true, opacity: 0.2 });
  const crossPairs = [[0,2],[1,2],[1,0]]; // GitHub-KV, AzureAD-KV, AzureAD-GitHub
  crossPairs.forEach(([a,b]) => {
    const geo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(...PLATFORMS[a].pos),
      new THREE.Vector3(...PLATFORMS[b].pos)
    ]);
    const line = new THREE.Line(geo, crossEdgeMat);
    line.computeLineDistances();
    scene.add(line);
  });

  // Bloom (mild)
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(container.clientWidth, container.clientHeight), 0.4, 0.3, 0.9));
  composer.addPass(new OutputPass());

  renderer.setAnimationLoop(() => {
    // Rotate hubs gently
    hubMeshes.forEach(h => { h.rotation.y += 0.003; });
    controls.update();
    composer.render();
    css2d.render(scene, camera);
  });

  window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth/container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    css2d.setSize(container.clientWidth, container.clientHeight);
    composer.setSize(container.clientWidth, container.clientHeight);
  });
})();


// ═══════════════════════════════════════════════════════════════
// SCENE 2: RISK SCORE TERRAIN
// ═══════════════════════════════════════════════════════════════
(function() {
  const container = document.getElementById('scene-terrain');
  if (!container) return;
  const renderer = makeRenderer(container);
  const css2d = makeCSS2D(container);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x030a14);

  const camera = new THREE.PerspectiveCamera(50, container.clientWidth/container.clientHeight, 0.1, 200);
  camera.position.set(14, 12, 16);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.25;
  controls.target.set(0, 2, 0);

  scene.add(new THREE.AmbientLight(0x223344, 0.5));
  const sun = new THREE.DirectionalLight(0xffffff, 0.8); sun.position.set(8,15,5); scene.add(sun);

  const GRID = 60;
  const geo = new THREE.PlaneGeometry(20, 20, GRID-1, GRID-1);
  geo.rotateX(-Math.PI / 2);

  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);

  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const z = pos.getZ(i);
    const ageNorm = (x + 10) / 20;
    const privNorm = (z + 10) / 20;
    // More dramatic height with exponential curve + noise for realism
    const base = ageNorm * 40 + privNorm * 20 + (ageNorm * privNorm) * 25;
    const noise = Math.sin(x * 1.5) * Math.cos(z * 1.2) * 6 + Math.sin(x * 3 + z * 2) * 3;
    const totalRisk = Math.max(0, Math.min(100, base + noise));
    // Exaggerate height so peaks are very distinct from valleys
    const height = Math.pow(totalRisk / 100, 1.6) * 8;
    pos.setY(i, height);

    // Sharp distinct color bands
    const c = new THREE.Color();
    if (totalRisk < 25) c.set(0x065f46);         // dark green - safe
    else if (totalRisk < 40) c.set(0x10b981);    // green - low
    else if (totalRisk < 55) c.set(0xfbbf24);    // yellow - medium
    else if (totalRisk < 70) c.set(0xf97316);    // orange - high
    else if (totalRisk < 85) c.set(0xdc2626);    // red - critical
    else c.set(0x7f1d1d);                        // dark red - extreme
    colors[i*3]=c.r; colors[i*3+1]=c.g; colors[i*3+2]=c.b;
  }
  pos.needsUpdate = true;
  geo.computeVertexNormals();
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const terrainMat = new THREE.MeshPhongMaterial({ vertexColors: true, flatShading: true, side: THREE.DoubleSide, shininess: 30 });
  scene.add(new THREE.Mesh(geo, terrainMat));

  // Wireframe overlay for depth perception
  const wireGeo = geo.clone();
  const wireMat = new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true, transparent: true, opacity: 0.04 });
  scene.add(new THREE.Mesh(wireGeo, wireMat));

  // Threshold planes - more visible with dashed edges
  const planeGeo = new THREE.PlaneGeometry(20, 20);
  const p70 = new THREE.Mesh(planeGeo, new THREE.MeshBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0.15, side: THREE.DoubleSide }));
  p70.rotation.x = -Math.PI/2; p70.position.y = Math.pow(70/100, 1.6)*8; scene.add(p70);
  const l70 = makeLabel('▲ AUTO-ROTATE THRESHOLD (score ≥ 70)', '#ef4444', '9px');
  l70.position.set(0, Math.pow(70/100, 1.6)*8 + 0.4, -10); scene.add(l70);

  const p50 = new THREE.Mesh(planeGeo.clone(), new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.1, side: THREE.DoubleSide }));
  p50.rotation.x = -Math.PI/2; p50.position.y = Math.pow(50/100, 1.6)*8; scene.add(p50);
  const l50 = makeLabel('▲ LLM ENRICHMENT (score ≥ 50)', '#f59e0b', '9px');
  l50.position.set(0, Math.pow(50/100, 1.6)*8 + 0.4, -10); scene.add(l50);

  // Axis labels
  const la = makeLabel('← Identity Age (0-365 days) →', '#00d4ff', '9px');
  la.position.set(0, 0.1, 11); scene.add(la);
  const lp = makeLabel('← Privilege Scope (0-7) →', '#7c3aed', '9px');
  lp.position.set(11, 0.1, 0); scene.add(lp);
  const lh = makeLabel('↑ Risk Score', '#ef4444', '9px');
  lh.position.set(-10.5, 4, -10.5); scene.add(lh);

  scene.add(new THREE.GridHelper(20, 20, 0x1a3a6b, 0x0d1b30));

  renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); css2d.render(scene, camera); });
  window.addEventListener('resize', () => { camera.aspect=container.clientWidth/container.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(container.clientWidth,container.clientHeight); css2d.setSize(container.clientWidth,container.clientHeight); });
})();


// ═══════════════════════════════════════════════════════════════
// SCENE 3: INTERACTIVE PIPELINE (Next/Prev, phase-by-phase)
// ═══════════════════════════════════════════════════════════════
(function() {
  const container = document.getElementById('scene-pipeline');
  if (!container) return;
  const renderer = makeRenderer(container);
  const css2d = makeCSS2D(container);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x030810);

  const camera = new THREE.PerspectiveCamera(50, container.clientWidth/container.clientHeight, 0.1, 200);
  camera.position.set(0, 6, 24);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(0, 0, 0);

  scene.add(new THREE.AmbientLight(0x223344, 0.6));
  const pl1 = new THREE.PointLight(0x00d4ff, 0.5, 40); pl1.position.set(-12,5,5); scene.add(pl1);
  const pl2 = new THREE.PointLight(0xa78bfa, 0.5, 40); pl2.position.set(12,5,5); scene.add(pl2);

  // ─── AGENTS grouped by phase ───
  const PHASES = [
    { name: 'DISCOVERY', color: '#00d4ff', colorHex: 0x00d4ff,
      desc: '5 agents scan GitHub, Azure AD, Key Vault, and SSL endpoints to discover all 11 NHI types.',
      agents: [
        { name: 'cert_agent', x: -14, desc: 'SSL/TLS cert expiry check' },
        { name: 'github_nhi', x: -11, desc: 'GitHub PATs, keys, secrets' },
        { name: 'azure_sp', x: -8, desc: 'Azure Service Principals' },
        { name: 'keyvault', x: -5, desc: 'Key Vault scan' },
        { name: 'monitor', x: -2, desc: 'Dormancy detection' },
      ]},
    { name: 'SCORING', color: '#10b981', colorHex: 0x10b981,
      desc: 'risk_scorer applies weighted formula: age(40) + type(30) + privilege(20) + ssl(10) = 0-100 score.',
      agents: [
        { name: 'risk_scorer', x: 2, desc: '0-100 weighted scoring' },
      ]},
    { name: 'POLICY + ML', color: '#f59e0b', colorHex: 0xf59e0b,
      desc: '11 OPA/Rego policy rules evaluate violations. ML engine runs Isolation Forest anomaly detection + Linear Regression forecast.',
      agents: [
        { name: 'policy_engine', x: 6, desc: '11 OPA/Rego rules' },
        { name: 'ml_engine', x: 10, desc: 'Isolation Forest + LR' },
      ]},
    { name: 'OUTPUT', color: '#ec4899', colorHex: 0xec4899,
      desc: 'report_gen produces HTML dashboard, JSON inventory, CSV export. email_notifier sends alerts for critical findings.',
      agents: [
        { name: 'report_gen', x: 14, desc: 'HTML + JSON + email' },
      ]},
  ];

  // Create agent meshes
  const agentMeshes = [];
  const allAgents = [];
  const agentGeo = new THREE.OctahedronGeometry(0.7, 1);

  PHASES.forEach((phase, pi) => {
    phase.agents.forEach(agent => {
      const mat = new THREE.MeshPhongMaterial({
        color: phase.colorHex,
        emissive: phase.colorHex,
        emissiveIntensity: 0.15,
        shininess: 60
      });
      const mesh = new THREE.Mesh(agentGeo, mat);
      mesh.position.set(agent.x, 0, 0);
      mesh.userData = { phase: pi, agent: agent.name, originalEmissive: 0.15 };
      scene.add(mesh);
      agentMeshes.push(mesh);

      // Label
      const label = makeLabel(agent.name, phase.color, '8.5px');
      label.position.set(0, -1.4, 0);
      mesh.add(label);

      allAgents.push({ mesh, phase: pi, ...agent });
    });
  });

  // Phase bracket labels (above)
  PHASES.forEach((phase, pi) => {
    const agents = phase.agents;
    const cx = agents.reduce((s, a) => s + a.x, 0) / agents.length;
    const label = makeLabel(`── ${phase.name} ──`, phase.color, '9px');
    label.position.set(cx, 3, 0);
    scene.add(label);
  });

  // Pipeline connector tube
  const curvePoints = allAgents.map(a => new THREE.Vector3(a.x, 0, 0));
  const curve = new THREE.CatmullRomCurve3(curvePoints);
  const tubeGeo = new THREE.TubeGeometry(curve, 80, 0.06, 8, false);
  const tubeMat = new THREE.MeshBasicMaterial({ color: 0x1a3a6b, transparent: true, opacity: 0.5 });
  scene.add(new THREE.Mesh(tubeGeo, tubeMat));

  // ─── PARTICLES (soft colored, NO white blowout) ───
  const PARTICLE_COUNT = 400;
  const pProgress = new Float32Array(PARTICLE_COUNT);
  const pSpeeds = new Float32Array(PARTICLE_COUNT);
  const pPositions = new Float32Array(PARTICLE_COUNT * 3);
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    pProgress[i] = Math.random();
    pSpeeds[i] = 0.2 + Math.random() * 0.5;
  }
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPositions, 3));

  // Soft colored particles — NO additive blending (prevents white blowout)
  const pMat = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uActiveMin: { value: 0.0 },
      uActiveMax: { value: 1.0 },
    },
    vertexShader: `
      uniform float uActiveMin;
      uniform float uActiveMax;
      attribute vec3 position;
      varying float vActive;
      varying float vProgress;
      void main() {
        vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
        // Compute approximate progress (x from -14 to 14 mapped to 0-1)
        float prog = (position.x + 14.0) / 28.0;
        vProgress = prog;
        vActive = step(uActiveMin, prog) * step(prog, uActiveMax);
        gl_PointSize = mix(2.0, 4.5, vActive) * (120.0 / -mvPos.z);
        gl_Position = projectionMatrix * mvPos;
      }
    `,
    fragmentShader: `
      varying float vActive;
      varying float vProgress;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        float soft = smoothstep(0.5, 0.1, d);
        // Color gradient: cyan -> green -> amber -> pink
        vec3 c;
        if (vProgress < 0.33) c = mix(vec3(0.0,0.7,0.9), vec3(0.06,0.72,0.51), vProgress*3.0);
        else if (vProgress < 0.66) c = mix(vec3(0.06,0.72,0.51), vec3(0.96,0.62,0.04), (vProgress-0.33)*3.0);
        else c = mix(vec3(0.96,0.62,0.04), vec3(0.93,0.27,0.6), (vProgress-0.66)*3.0);
        float alpha = mix(0.15, 0.7, vActive) * soft;
        gl_FragColor = vec4(c, alpha);
      }
    `,
    transparent: true, depthWrite: false
  });
  const particles = new THREE.Points(pGeo, pMat);
  scene.add(particles);

  // ─── INTERACTIVE STATE ───
  let currentPhase = 0;
  const totalPhases = PHASES.length;

  function getPhaseRange(pi) {
    // Map phase index to curve progress [0,1]
    const firstAgent = PHASES.slice(0, pi).reduce((s, p) => s + p.agents.length, 0);
    const lastAgent = firstAgent + PHASES[pi].agents.length - 1;
    const total = allAgents.length - 1;
    return [firstAgent / total, lastAgent / total];
  }

  function updatePhase(pi) {
    currentPhase = pi;
    const [min, max] = getPhaseRange(pi);
    // Expand range slightly for particles
    pMat.uniforms.uActiveMin.value = Math.max(0, min - 0.05);
    pMat.uniforms.uActiveMax.value = Math.min(1, max + 0.05);

    // Highlight active agents, dim others
    agentMeshes.forEach(m => {
      if (m.userData.phase === pi) {
        m.material.emissiveIntensity = 0.6;
        m.scale.setScalar(1.3);
      } else {
        m.material.emissiveIntensity = 0.05;
        m.scale.setScalar(0.8);
      }
    });

    // Update UI
    document.getElementById('pipe-status').textContent = `Phase ${pi+1} / ${totalPhases}`;
    document.getElementById('pipe-info-name').textContent = PHASES[pi].name;
    document.getElementById('pipe-info-name').style.color = PHASES[pi].color;
    document.getElementById('pipe-info-desc').textContent = PHASES[pi].desc;
    document.getElementById('pipe-prev').disabled = (pi === 0);
    document.getElementById('pipe-next').disabled = (pi === totalPhases - 1);

    // Animate camera to focus on active phase
    const agents = PHASES[pi].agents;
    const cx = agents.reduce((s, a) => s + a.x, 0) / agents.length;
    // Smooth camera target shift
    controls.target.set(cx, 0, 0);
  }

  // Button handlers
  document.getElementById('pipe-next').addEventListener('click', () => {
    if (currentPhase < totalPhases - 1) updatePhase(currentPhase + 1);
  });
  document.getElementById('pipe-prev').addEventListener('click', () => {
    if (currentPhase > 0) updatePhase(currentPhase - 1);
  });

  // Double-click to jump to phase
  renderer.domElement.addEventListener('dblclick', (event) => {
    const rect = container.getBoundingClientRect();
    const mouse = new THREE.Vector2(
      ((event.clientX - rect.left) / rect.width) * 2 - 1,
      -((event.clientY - rect.top) / rect.height) * 2 + 1
    );
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(agentMeshes);
    if (hits.length > 0) {
      const phase = hits[0].object.userData.phase;
      updatePhase(phase);
    }
  });

  // Initialize to phase 0
  updatePhase(0);

  // Animation
  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const t = clock.getElapsedTime();
    pMat.uniforms.uTime.value = t;

    // Move particles
    const posArr = pGeo.attributes.position.array;
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      pProgress[i] += pSpeeds[i] * 0.002;
      if (pProgress[i] > 1) pProgress[i] -= 1;
      const pt = curve.getPointAt(Math.min(0.999, pProgress[i]));
      posArr[i*3]   = pt.x + (Math.random()-0.5)*0.5;
      posArr[i*3+1] = pt.y + Math.sin(t + i*0.2)*0.3 + (Math.random()-0.5)*0.3;
      posArr[i*3+2] = pt.z + (Math.random()-0.5)*0.5;
    }
    pGeo.attributes.position.needsUpdate = true;

    // Bob active agents
    agentMeshes.forEach((m, idx) => {
      if (m.userData.phase === currentPhase) {
        m.position.y = Math.sin(t * 2 + idx) * 0.25;
        m.rotation.y += 0.01;
      } else {
        m.position.y = 0;
      }
    });

    controls.update();
    renderer.render(scene, camera);
    css2d.render(scene, camera);
  });

  window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth/container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    css2d.setSize(container.clientWidth, container.clientHeight);
  });
})();


// ═══════════════════════════════════════════════════════════════
// SCENE 4: ML ANOMALY 3D SCATTER
// ═══════════════════════════════════════════════════════════════
(function() {
  const container = document.getElementById('scene-scatter');
  if (!container) return;
  const renderer = makeRenderer(container);
  const css2d = makeCSS2D(container);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020a10);

  const camera = new THREE.PerspectiveCamera(55, container.clientWidth/container.clientHeight, 0.1, 200);
  camera.position.set(12, 10, 14);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.3;
  controls.target.set(5, 5, 3);

  scene.add(new THREE.AmbientLight(0x223344, 0.5));
  scene.add(new THREE.DirectionalLight(0xffffff, 0.7)).position.set(10,15,8);

  const axisScale = { x: 0.12, y: 0.03, z: 1.5 };
  const axisLen = { x: 12, y: 11, z: 10.5 };

  // Axes
  const axisMat = new THREE.LineBasicMaterial({ color: 0x445577 });
  [[0,0,0,axisLen.x,0,0],[0,0,0,0,axisLen.y,0],[0,0,0,0,0,axisLen.z]].forEach(pts => {
    const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(pts[0],pts[1],pts[2]), new THREE.Vector3(pts[3],pts[4],pts[5])]);
    scene.add(new THREE.Line(g, axisMat));
  });

  const lx = makeLabel('Risk Score →', '#00d4ff', '8px'); lx.position.set(axisLen.x/2, -0.8, 0); scene.add(lx);
  const ly = makeLabel('Age (days) ↑', '#10b981', '8px'); ly.position.set(-1.2, axisLen.y/2, 0); scene.add(ly);
  const lz = makeLabel('Scope →', '#7c3aed', '8px'); lz.position.set(0, -0.8, axisLen.z/2); scene.add(lz);

  // Data points
  const normalGeo = new THREE.SphereGeometry(0.18, 10, 7);
  const anomalyGeo = new THREE.SphereGeometry(0.3, 12, 8);
  const normalMat = new THREE.MeshPhongMaterial({ color: 0x10b981, emissive: 0x10b981, emissiveIntensity: 0.15 });
  const anomalyMat = new THREE.MeshPhongMaterial({ color: 0xef4444, emissive: 0xef4444, emissiveIntensity: 0.5 });

  // Normal findings
  for (let i = 0; i < 55; i++) {
    const mesh = new THREE.Mesh(normalGeo, normalMat);
    mesh.position.set(
      (15 + Math.random()*45) * axisScale.x,
      (10 + Math.random()*180) * axisScale.y,
      Math.floor(Math.random()*4) * axisScale.z
    );
    scene.add(mesh);
  }

  // Anomalies (high risk, old, high scope)
  const anomalyData = [
    { score: 88, age: 280, scope: 6, label: 'Dormant PAT [88]' },
    { score: 91, age: 320, scope: 5, label: 'PAT admin:org [91]' },
    { score: 82, age: 210, scope: 5, label: 'Expired SSL [82]' },
    { score: 75, age: 240, scope: 4, label: 'KV Secret old [75]' },
    { score: 85, age: 350, scope: 6, label: 'Dormant PAT [85]' },
    { score: 78, age: 190, scope: 5, label: 'Client Secret [78]' },
    { score: 70, age: 260, scope: 4, label: 'Deploy Key [70]' },
  ];
  anomalyData.forEach(a => {
    const mesh = new THREE.Mesh(anomalyGeo, anomalyMat);
    mesh.position.set(a.score * axisScale.x, a.age * axisScale.y, a.scope * axisScale.z);
    scene.add(mesh);
    const label = makeLabel(a.label, '#ef4444', '7px');
    label.position.set(0, 0.5, 0);
    mesh.add(label);
  });

  // Decision boundary (wireframe sphere)
  const bGeo = new THREE.SphereGeometry(5, 20, 14);
  const bMat = new THREE.MeshBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.04, wireframe: true });
  const boundary = new THREE.Mesh(bGeo, bMat);
  boundary.position.set(4, 3.5, 2.5);
  scene.add(boundary);

  scene.add(new THREE.GridHelper(14, 14, 0x1a3a6b, 0x0d1b30)).position.set(6, -0.05, 5);

  // Bloom
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(container.clientWidth, container.clientHeight), 0.5, 0.3, 0.85));
  composer.addPass(new OutputPass());

  renderer.setAnimationLoop(() => {
    anomalyMat.emissiveIntensity = 0.35 + Math.sin(Date.now()*0.004) * 0.25;
    controls.update();
    composer.render();
    css2d.render(scene, camera);
  });

  window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth/container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    css2d.setSize(container.clientWidth, container.clientHeight);
    composer.setSize(container.clientWidth, container.clientHeight);
  });
})();

</script>
</body>
</html>
"""

OUTPUT.write_text(HTML, encoding="utf-8")
print(f"[OK] 3D AR/VR Poster v3 written → {OUTPUT}")
print(f"     Size: {OUTPUT.stat().st_size / 1024:.1f} KB")
webbrowser.open(OUTPUT.as_uri())
print("[OK] Opened in browser")
print()
print("FIXES APPLIED:")
print("  1. GRAPH: Hub-spoke layout — 4 platform hubs (GitHub, Azure AD,")
print("     Key Vault, SSL) with NHI types orbiting their source.")
print("     Each node has full name + risk score. Instantly clear what's what.")
print()
print("  2. PIPELINE: Interactive Next/Prev buttons — step through 4 phases:")
print("     DISCOVERY → SCORING → POLICY+ML → OUTPUT")
print("     Active phase glows, info panel shows description.")
print("     Double-click any agent to jump to its phase.")
print()
print("  3. PARTICLES: Removed additive blending (no white blowout).")
print("     Soft colored particles with phase-matched gradient.")
print("     Inactive particles are dim; active ones are vibrant.")
