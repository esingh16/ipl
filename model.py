<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>IPL 2026 AI XI & Predictions</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header class="hero">
    <div class="hero-overlay"></div>
    <div class="hero-content">
      <h1>IPL 2026 AI XI & Predictions</h1>
      <p>
        AI/ML‑style engine picks the best 12 for each IPL 2026 team and predicts
        top run‑getters, wicket‑takers, top‑4 and the title favourite using multi‑year T20 data (IPL 2023‑25, T20I and leagues, encoded as ratings). [web:78][web:80][web:84][web:87]
      </p>
      <div class="chip-row">
        <span class="chip">Best XI + Impact</span>
        <span class="chip">Top Runs (Pred)</span>
        <span class="chip">Top Wickets (Pred)</span>
        <span class="chip">Top‑4 & Winner (Pred)</span>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="panel">
      <div class="panel-header">
        <h2>Pick a Team</h2>
        <p>View the AI‑picked playing XI and impact player for any IPL 2026 franchise.</p>
      </div>
      <div id="teamTabs" class="team-tabs"></div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2 id="teamTitle">Team XI & Impact Player</h2>
        <p class="subtitle">
          XI respects max four overseas players, ensures a wicketkeeper and strong bowling depth.
        </p>
      </div>
      <div class="best12-wrapper">
        <div>
          <h3>Playing XI</h3>
          <div id="xiGrid" class="player-grid"></div>
        </div>
        <div>
          <h3>Impact Player</h3>
          <div id="impactCard" class="impact-card empty">
            <p>Select a team to see the model pick.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>League‑wide Predictions</h2>
        <p>
          Uses encoded ratings from IPL 2023‑25, T20 internationals and major T20 leagues to project season‑long impact.
