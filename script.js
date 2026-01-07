const TEAM_CODES = ["CSK", "DC", "GT", "KKR", "LSG", "MI", "PBKS", "RR", "RCB", "SRH"];

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

let modelData = null;
let currentTeam = "CSK";

const teamTabsEl = document.getElementById("teamTabs");
const xiGridEl = document.getElementById("xiGrid");
const impactCardEl = document.getElementById("impactCard");
const teamTitleEl = document.getElementById("teamTitle");
const runsTableBody = document.querySelector("#runsTable tbody");
const wicketsTableBody = document.querySelector("#wicketsTable tbody");
const projectionsBody = document.querySelector("#projectionsTable tbody");
const summaryEl = document.getElementById("summary");

async function loadModelOutput() {
  const res = await fetch("model_output.json");
  modelData = await res.json();
  initUI();
}

function initUI() {
  renderTeamTabs();
  updateTeam(currentTeam);
  renderLeaguePredictions();
}

function renderTeamTabs() {
  teamTabsEl.innerHTML = "";
  TEAM_CODES.forEach(code => {
    const btn = document.createElement("button");
    btn.className = "team-tab";
    btn.textContent = code;
    btn.style.borderColor = `${teamColors[code]}55`;
    btn.addEventListener("click", () => {
      currentTeam = code;
      updateTeam(code);
      document
        .querySelectorAll(".team-tab")
        .forEach(el => el.classList.remove("active"));
      btn.classList.add("active");
    });
    teamTabsEl.appendChild(btn);
  });
  const first = teamTabsEl.querySelector(".team-tab");
  if (first) first.classList.add("active");
}

function updateTeam(code) {
  if (!modelData) return;
  const teamBlock = modelData.best12[code];
  if (!teamBlock) return;
  teamTitleEl.textContent = `${code} – XI & Impact Player`;

  renderXI(teamBlock.xi);
  renderImpact(teamBlock.impact);
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
    roleEl.textContent = p.description;

    const tags = document.createElement("div");
    tags.className = "player-tags";

    const locTag = document.createElement("span");
    locTag.className = "tag " + (p.overseas ? "overseas" : "indian");
    locTag.textContent = p.overseas ? "Overseas" : "Indian";
    tags.appendChild(locTag);

    const typeTag = document.createElement("span");
    typeTag.className = "tag" + (p.role === "bowler" || p.role === "allrounder" ? " bowler" : "");
    typeTag.textContent =
      p.role === "bowler"
        ? "Bowler"
        : p.role === "allrounder"
        ? "All‑rounder"
        : p.role === "keeper"
        ? "Keeper"
        : "Batter";
    tags.appendChild(typeTag);

    info.appendChild(nameEl);
    info.appendChild(roleEl);
    info.appendChild(tags);

    const scoreEl = document.createElement("div");
    scoreEl.className = "player-score";
    scoreEl.textContent = Math.round(p.score * 100);

    main.appendChild(info);
    main.appendChild(scoreEl);

    const meta = document.createElement("div");
    meta.className = "player-meta";
    meta.textContent = `Selection score: ${(p.score * 100).toFixed(1)}`;

    card.appendChild(main);
    card.appendChild(meta);
    xiGridEl.appendChild(card);
  });
}

function renderImpact(p) {
  if (!p || !p.name) {
    impactCardEl.classList.add("empty");
    impactCardEl.innerHTML = "<p>No impact player available.</p>";
    return;
  }
  impactCardEl.classList.remove("empty");
  impactCardEl.innerHTML = "";

  const label = document.createElement("div");
  label.className = "impact-label";
  label.textContent = "Impact Player (AI Pick)";

  const name = document.createElement("div");
  name.className = "player-name";
  name.style.marginTop = "4px";
  name.textContent = p.name;

  const role = document.createElement("div");
  role.className = "player-role";
  role.textContent = p.description;

  const meta = document.createElement("div");
  meta.className = "player-meta";
  meta.textContent = `Selection score: ${(p.score * 100).toFixed(1)} · ${
    p.overseas ? "Overseas" : "Indian"
  } ${p.role}`;

  impactCardEl.appendChild(label);
  impactCardEl.appendChild(name);
  impactCardEl.appendChild(role);
  impactCardEl.appendChild(meta);
}

function renderLeaguePredictions() {
  // Top runs
  runsTableBody.innerHTML = "";
  modelData.top_runs_pred.forEach((row, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${row.name}</td>
      <td>${row.team}</td>
      <td>${(row.score * 100).toFixed(1)}</td>
    `;
    runsTableBody.appendChild(tr);
  });

  // Top wickets
  wicketsTableBody.innerHTML = "";
  modelData.top_wkts_pred.forEach((row, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${row.name}</td>
      <td>${row.team}</td>
      <td>${(row.score * 100).toFixed(1)}</td>
    `;
    wicketsTableBody.appendChild(tr);
  });

  // Projections
  projectionsBody.innerHTML = "";
  modelData.projections.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.team}</td>
      <td>${row.strength.toFixed(3)}</td>
      <td>${(row.p_top4 * 100).toFixed(0)}%</td>
      <td>${(row.p_title * 100).toFixed(0)}%</td>
    `;
    projectionsBody.appendChild(tr);
  });

  const top4 = modelData.top4_predicted.join(", ");
  const fav = modelData.title_favourite;
  summaryEl.textContent = `Projected top‑4: ${top4}. Title favourite: ${fav}.`;
}

loadModelOutput();
