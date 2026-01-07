// ---- Mocked data ----
// In real use, you would fetch squads & stats and compute this dynamically
// from Cricbuzz/ESPN style data for IPL 2026. [web:4][web:30][web:44]

// Minimal squads for demo: adjust names to real IPL 2026 squads later.
const TEAMS = [
  "CSK",
  "DC",
  "GT",
  "KKR",
  "LSG",
  "MI",
  "PBKS",
  "RR",
  "RCB",
  "SRH"
];

const teamColors = {
  CSK: "#f9de2a",
  DC: "#004c93",
  GT: "#0a243b",
  KKR: "#3b125f",
  LSG: "#00a9e0",
  MI: "#004ba0",
  PBKS: "#c41e3a",
  RR: "#ea1a8c",
  RCB: "#ff0000",
  SRH: "#ff822a"
};

// Example squads with simple stats. Replace later with real 2026 squads. [web:30]
const SQUADS = {
  CSK: [
    { name: "Ruturaj Gaikwad", role: "Opener", type: "batter", country: "India", form: 0.9, impact: 0.8 },
    { name: "Devon Conway", role: "Opener", type: "batter", country: "NZ", form: 0.8, impact: 0.7 },
    { name: "Moeen Ali", role: "All‑rounder", type: "allrounder", country: "ENG", form: 0.75, impact: 0.9 },
    { name: "Shivam Dube", role: "Middle‑order", type: "allrounder", country: "India", form: 0.82, impact: 0.78 },
    { name: "MS Dhoni", role: "Keeper‑finisher", type: "keeper", country: "India", form: 0.7, impact: 0.95 },
    { name: "Ravindra Jadeja", role: "All‑rounder", type: "allrounder", country: "India", form: 0.88, impact: 0.93 },
    { name: "Deepak Chahar", role: "Powerplay bowler", type: "bowler", country: "India", form: 0.7, impact: 0.8 },
    { name: "Matheesha Pathirana", role: "Death bowler", type: "bowler", country: "SL", form: 0.83, impact: 0.9 },
    { name: "Tushar Deshpande", role: "Seam bowler", type: "bowler", country: "India", form: 0.68, impact: 0.7 },
    { name: "Ajinkya Rahane", role: "Top‑order", type: "batter", country: "India", form: 0.65, impact: 0.55 },
    { name: "Rajvardhan Hangargekar", role: "All‑round seam", type: "allrounder", country: "India", form: 0.6, impact: 0.65 },
    { name: "Maheesh Theekshana", role: "Spinner", type: "bowler", country: "SL", form: 0.72, impact: 0.78 }
  ],
  RCB: [
    { name: "Virat Kohli", role: "Top‑order", type: "batter", country: "India", form: 0.92, impact: 0.92 },
    { name: "Faf du Plessis", role: "Opener", type: "batter", country: "SA", form: 0.82, impact: 0.75 },
    { name: "Glenn Maxwell", role: "All‑rounder", type: "allrounder", country: "AUS", form: 0.78, impact: 0.9 },
    { name: "Rajat Patidar", role: "Middle‑order", type: "batter", country: "India", form: 0.75, impact: 0.7 },
    { name: "Dinesh Karthik", role: "Finisher‑keeper", type: "keeper", country: "India", form: 0.7, impact: 0.8 },
    { name: "Cameron Green", role: "All‑rounder", type: "allrounder", country: "AUS", form: 0.8, impact: 0.82 },
    { name: "Mohammed Siraj", role: "Seam bowler", type: "bowler", country: "India", form: 0.78, impact: 0.82 },
    { name: "Reece Topley", role: "Left‑arm seam", type: "bowler", country: "ENG", form: 0.68, impact: 0.7 },
    { name: "Karn Sharma", role: "Spinner", type: "bowler", country: "India", form: 0.62, impact: 0.6 },
    { name: "Anuj Rawat", role: "Top‑order/keeper", type: "keeper", country: "India", form: 0.6, impact: 0.55 },
    { name: "Akash Deep", role: "Seam bowler", type: "bowler", country: "India", form: 0.58, impact: 0.6 },
    { name: "Mahipal Lomror", role: "All‑rounder", type: "allrounder", country: "India", form: 0.63, impact: 0.64 }
  ]
};

// Fallback simple squads for other teams (short, just to show UI)
function makeDummySquad(code) {
  return Array.from({ length: 12 }).map((_, idx) => {
    const isOverseas = idx % 4 === 1;
    return {
      name: `${code} Player ${idx + 1}`,
      role: idx < 2 ? "Opener" : idx < 5 ? "Middle‑order" : idx < 8 ? "Bowler" : "All‑rounder",
      type: idx < 2 ? "batter" : idx < 5 ? "batter" : idx < 8 ? "bowler" : "allrounder",
      country: isOverseas ? "AUS" : "India",
      form: 0.5 + Math.random() * 0.4,
      impact: 0.5 + Math.random() * 0.4
    };
  });
}

for (const t of TEAMS) {
  if (!SQUADS[t]) SQUADS[t] = makeDummySquad(t);
}

// Mock stats for runs & wickets (replace later with real IPL 2026 stats). [web:4][web:12]
const mockTopRuns = [
  { player: "Sai Sudharsan", team: "GT", runs: 759, sr: 156.2 },
  { player: "Suryakumar Yadav", team: "MI", runs: 717, sr: 167.9 },
  { player: "Virat Kohli", team: "RCB", runs: 657, sr: 144.7 },
  { player: "Shubman Gill", team: "GT", runs: 650, sr: 155.9 },
  { player: "Mitchell Marsh", team: "DC", runs: 627, sr: 163.7 }
];

const mockTopWickets = [
  { player: "Yuzvendra Chahal", team: "RR", wkts: 24, econ: 7.8 },
  { player: "Mohammed Siraj", team: "RCB", wkts: 22, econ: 7.9 },
  { player: "Jasprit Bumrah", team: "MI", wkts: 21, econ: 7.2 },
  { player: "Rashid Khan", team: "GT", wkts: 20, econ: 7.1 },
  { player: "Pat Cummins", team: "SRH", wkts: 19, econ: 8.1 }
];

// Mock playoff projections (pts & probabilities). [web:44]
const mockProjections = [
  { team: "CSK", pts: 18, nrr: "+0.912", pTop4: 0.86, pTitle: 0.24 },
  { team: "MI", pts: 16, nrr: "+0.742", pTop4: 0.79, pTitle: 0.2 },
  { team: "RCB", pts: 14, nrr: "+0.102", pTop4: 0.54, pTitle: 0.13 },
  { team: "SRH", pts: 14, nrr: "+0.188", pTop4: 0.58, pTitle: 0.16 },
  { team: "RR", pts: 12, nrr: "-0.010", pTop4: 0.35, pTitle: 0.08 },
  { team: "KKR", pts: 10, nrr: "-0.211", pTop4: 0.22, pTitle: 0.05 },
  { team: "GT", pts: 10, nrr: "-0.189", pTop4: 0.24, pTitle: 0.05 },
  { team: "LSG", pts: 8, nrr: "-0.341", pTop4: 0.14, pTitle: 0.03 },
  { team: "PBKS", pts: 6, nrr: "-0.512", pTop4: 0.08, pTitle: 0.02 },
  { team: "DC", pts: 6, nrr: "-0.678", pTop4: 0.06, pTitle: 0.02 }
];

// ---- AI‑style selection logic ----

// Simple scoring: combine form and impact, plus role bonus (all‑rounders get a small bump).
function computeScore(player) {
  const base = 0.6 * player.form + 0.4 * player.impact;
  const roleBonus = player.type === "allrounder" ? 0.06 : 0;
  return +(base + roleBonus).toFixed(3);
}

function isOverseas(player) {
  return player.country !== "India";
}

function pickBest12ForTeam(code) {
  const squad = SQUADS[code].map(p => ({
    ...p,
    score: computeScore(p)
  }));

  // Sort by score descending.
  squad.sort((a, b) => b.score - a.score);

  // Build XI with constraints: max 4 overseas, at least 5 bowlers/all‑rounders combined.
  const xi = [];
  let overseasCount = 0;

  for (const p of squad) {
    if (xi.length === 11) break;

    const willBeOverseas = isOverseas(p);
    if (willBeOverseas && overseasCount >= 4) continue;

    xi.push(p);
    if (willBeOverseas) overseasCount++;
  }

  // Ensure at least 5 bowling options (bowler/allrounder).
  const countBowling = xi.filter(
    p => p.type === "bowler" || p.type === "allrounder"
  ).length;

  if (countBowling < 5) {
    const need = 5 - countBowling;
    let added = 0;
    for (const p of squad) {
      if (added >= need) break;
      if (
        (p.type === "bowler" || p.type === "allrounder") &&
        !xi.includes(p)
      ) {
        const willBeOverseas = isOverseas(p);
        if (willBeOverseas && overseasCount >= 4) continue;
        xi[xi.length - 1 - added] = p; // swap lower ones
        if (willBeOverseas) overseasCount++;
        added++;
      }
    }
  }

  // Impact player: best remaining non‑selected.
  const remaining = squad.filter(p => !xi.includes(p));
  remaining.sort((a, b) => b.score - a.score);
  const impact = remaining[0] || null;

  return { xi, impact };
}

// ---- DOM rendering ----

const teamTabsEl = document.getElementById("teamTabs");
const xiGridEl = document.getElementById("xiGrid");
const impactCardEl = document.getElementById("impactCard");
const teamTitleEl = document.getElementById("teamTitle");
const runsTableBody = document.querySelector("#runsTable tbody");
const wicketsTableBody = document.querySelector("#wicketsTable tbody");
const projectionsBody = document.querySelector("#projectionsTable tbody");

let currentTeam = TEAMS[0];

function renderTeamTabs() {
  teamTabsEl.innerHTML = "";
  TEAMS.forEach(code => {
    const btn = document.createElement("button");
    btn.className = "team-tab";
    btn.textContent = code;
    btn.style.borderColor = `${teamColors[code]}55`;
    btn.addEventListener("click", () => {
      currentTeam = code;
      updateTeam();
      document
        .querySelectorAll(".team-tab")
        .forEach(el => el.classList.remove("active"));
      btn.classList.add("active");
    });
    teamTabsEl.appendChild(btn);
  });

  // Mark first active.
  const first = teamTabsEl.querySelector(".team-tab");
  if (first) first.classList.add("active");
}

function updateTeam() {
  const { xi, impact } = pickBest12ForTeam(currentTeam);
  teamTitleEl.textContent = `${currentTeam} – XI & Impact Player`;
  renderXI(xi);
  renderImpact(impact);
}

function renderXI(xi) {
  xiGridEl.innerHTML = "";
  xi.forEach(p => {
    const card = document.createElement("div");
    card.className = "player-card";

    const main = document.createElement("div");
    main.className = "player-main";

    const info = document.createElement("div");
    info.className = "player-info";

    const nameEl = document.createElement("div");
    nameEl.className = "player-name";
    nameEl.textContent = p.name;

    const roleEl = document.createElement("div");
    roleEl.className = "player-role";
    roleEl.textContent = p.role;

    const tags = document.createElement("div");
    tags.className = "player-tags";

    const locTag = document.createElement("span");
    locTag.className = "tag " + (isOverseas(p) ? "overseas" : "indian");
    locTag.textContent = isOverseas(p) ? "Overseas" : "Indian";
    tags.appendChild(locTag);

    if (p.type === "bowler" || p.type === "allrounder") {
      const bowlTag = document.createElement("span");
      bowlTag.className = "tag bowler";
      bowlTag.textContent = p.type === "bowler" ? "Bowler" : "All‑rounder";
      tags.appendChild(bowlTag);
    } else if (p.type === "keeper") {
      const keepTag = document.createElement("span");
      keepTag.className = "tag";
      keepTag.textContent = "Keeper";
      tags.appendChild(keepTag);
    } else {
      const batTag = document.createElement("span");
      batTag.className = "tag";
      batTag.textContent = "Batter";
      tags.appendChild(batTag);
    }

    info.appendChild(nameEl);
    info.appendChild(roleEl);
    info.appendChild(tags);

    const scoreEl = document.createElement("div");
    scoreEl.className = "player-score";
    scoreEl.textContent = (p.score * 100).toFixed(0);

    main.appendChild(info);
    main.appendChild(scoreEl);

    const meta = document.createElement("div");
    meta.className = "player-meta";
    meta.textContent = `Form ${(p.form * 100).toFixed(0)} · Impact ${(p.impact *
      100).toFixed(0)}`;

    card.appendChild(main);
    card.appendChild(meta);

    xiGridEl.appendChild(card);
  });
}

function renderImpact(p) {
  if (!p) {
    impactCardEl.classList.add("empty");
    impactCardEl.innerHTML = "<p>No impact player available.</p>";
    return;
  }
  impactCardEl.classList.remove("empty");
  impactCardEl.innerHTML = "";

  const label = document.createElement("div");
  label.className = "impact-label";
  label.textContent = "Impact Player";

  const name = document.createElement("div");
  name.className = "player-name";
  name.style.marginTop = "4px";
  name.textContent = p.name;

  const role = document.createElement("div");
  role.className = "player-role";
  role.textContent = p.role;

  const meta = document.createElement("div");
  meta.className = "player-meta";
  meta.textContent = `Score ${(p.score * 100).toFixed(
    0
  )} · Form ${(p.form * 100).toFixed(0)} · Impact ${(p.impact * 100).toFixed(
    0
  )}`;

  impactCardEl.appendChild(label);
  impactCardEl.appendChild(name);
  impactCardEl.appendChild(role);
  impactCardEl.appendChild(meta);
}

// Stats rendering
function renderStats() {
  runsTableBody.innerHTML = "";
  mockTopRuns.forEach((row, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${row.player}</td>
      <td>${row.team}</td>
      <td>${row.runs}</td>
      <td>${row.sr}</td>
    `;
    runsTableBody.appendChild(tr);
  });

  wicketsTableBody.innerHTML = "";
  mockTopWickets.forEach((row, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${row.player}</td>
      <td>${row.team}</td>
      <td>${row.wkts}</td>
      <td>${row.econ}</td>
    `;
    wicketsTableBody.appendChild(tr);
  });
}

// Projections
function renderProjections() {
  projectionsBody.innerHTML = "";
  mockProjections.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.team}</td>
      <td>${row.pts}</td>
      <td>${row.nrr}</td>
      <td>${(row.pTop4 * 100).toFixed(0)}%</td>
      <td>${(row.pTitle * 100).toFixed(0)}%</td>
    `;
    projectionsBody.appendChild(tr);
  });
}

// Init
renderTeamTabs();
updateTeam();
renderStats();
renderProjections();
