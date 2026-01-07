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

// captains you specified
const CAPTAINS = {
  CSK: "Ruturaj Gaikwad",
  MI: "Hardik Pandya",
  GT: "Shubman Gill",
  RCB: "Rajat Patidar",
  PBKS: "Shreyas Iyer",
  KKR: "Ajinkya Rahane",
  RR: "Riyan Parag",
  LSG: "Rishabh Pant",
  SRH: "Pat Cummins",
  DC: "Axar Patel"
};

// winner modal wiring
const teamTabsEl = document.getElementById("teamTabs");
const xiListEl = document.getElementById("xiList");
const impactCardEl = document.getElementById("impactCard");
const teamTitleEl = document.getElementById("teamTitle");
const runsTableBody = document.querySelector("#runsTable tbody");
const wicketsTableBody = document.querySelector("#wicketsTable tbody");
const projectionsBody = document.querySelector("#projectionsTable tbody");
const winnerButton = document.getElementById("winnerButton");
const winnerModal = document.getElementById("winnerModal");
const winnerNameEl = document.getElementById("winnerName");
const closeWinnerBtn = document.getElementById("closeWinner");

let modelData = null;
let currentTeam = "CSK";

async function loadModel() {
  const res = await fetch("model_output.json");
  modelData = await res.json();
  initUI();
}

function initUI() {
  renderTeamTabs();
  updateTeam(currentTeam);
  renderCaps();
  renderProjections();
  wireWinner();
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
  const block = modelData.best12[code];
  if (!block) return;
  teamTitleEl.textContent = `${code} – XI & Impact Player`;
  renderXI(code, block.xi);
  renderImpact(block.impact);
}

function renderXI(teamCode, xi) {
  xiListEl.innerHTML = "";
  const captainName = CAPTAINS[teamCode];

  xi.forEach(player => {
    const li = document.createElement("li");
    li.className = "xi-item";

    const main = document.createElement("div");
    main.className = "xi-main";

    const nameRole = document.createElement("div");
    const nameEl = document.createElement("div");
    nameEl.className = "xi-name";
    nameEl.textContent = player.name;
    const roleEl = document.createElement("div");
    roleEl.className = "xi-role";
    roleEl.textContent = player.description || player.role;

    nameRole.appendChild(nameEl);
    nameRole.appendChild(roleEl);

    const tags = document.createElement("div");
    tags.className = "xi-tags";

    if (player.name === captainName) {
      const c = document.createElement("span");
      c.className = "badge badge-captain";
      c.textContent = "C";
      tags.appendChild(c);
    }
    if (player.role === "keeper" || /wk/i.test(player.description || "")) {
      const wk = document.createElement("span");
      wk.className = "badge badge-wk";
      wk.textContent = "WK";
      tags.appendChild(wk);
    }
    if (player.overseas) {
      const o = document.createElement("span");
      o.className = "badge badge-overseas";
      o.textContent = "Overseas";
      tags.appendChild(o);
    }

    const scoreEl = document.createElement("div");
    scoreEl.className = "player-score";
    scoreEl.textContent = player.score ? Math.round(player.score * 100) : "";

    main.appendChild(nameRole);
    main.appendChild(scoreEl);

    li.appendChild(main);
    if (tags.childNodes.length) li.appendChild(tags);

    xiListEl.appendChild(li);
  });
}

function renderImpact(impact) {
  if (!impact || !impact.name) {
    impactCardEl.classList.add("empty");
    impactCardEl.innerHTML = "<p>No impact player available.</p>";
    return;
  }
  impactCardEl.classList.remove("empty");
  impactCardEl.innerHTML = "";

  const label = document.createElement("div");
  label.className = "impact-label";
  label.textContent = "Impact player";

  const name = document.createElement("div");
  name.className = "impact-name";
  name.textContent = impact.name;

  const meta = document.createElement("div");
  meta.className = "impact-meta";
  meta.textContent = `${impact.description || impact.role} · ${
    impact.overseas ? "Overseas" : "Indian"
  }`;

  impactCardEl.appendChild(label);
  impactCardEl.appendChild(name);
  impactCardEl.appendChild(meta);
}

function renderCaps() {
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
}

function renderProjections() {
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
}

function wireWinner() {
  const winnerTeam = modelData.title_favourite;
  winnerNameEl.textContent = winnerTeam || "N/A";

  winnerButton.addEventListener("click", () => {
    winnerModal.classList.remove("hidden");
  });

  closeWinnerBtn.addEventListener("click", () => {
    winnerModal.classList.add("hidden");
  });

  winnerModal.addEventListener("click", e => {
    if (e.target === winnerModal) {
      winnerModal.classList.add("hidden");
    }
  });
}

loadModel();
