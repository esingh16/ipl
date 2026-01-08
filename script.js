const TEAM_CODES = ["CSK", "DC", "GT", "KKR", "LSG", "MI", "PBKS", "RR", "RCB", "SRH"];

// main theme colour per team (used for cards/backgrounds)
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

// paths to the logos you attached
const teamLogos = {
  CSK: "csk.png",
  DC: "dc.png",
  GT: "gt.png",
  KKR: "kkr.png",
  LSG: "lsg.png",
  MI: "mi.png",
  PBKS: "pbks.png",
  RR: "rr.png",
  RCB: "rcb.png",
  SRH: "srh.png"
};


// captains
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
  TEAM_CODES.forEach((code) => {
    const btn = document.createElement("button");
    btn.className = "team-logo-btn";
    btn.dataset.code = code;
    btn.style.borderColor = `${teamColors[code]}aa`;
    btn.style.boxShadow = `0 10px 24px ${teamColors[code]}55`;

    const img = document.createElement("img");
    img.src = teamLogos[code];
    img.alt = `${code} logo`;

    btn.appendChild(img);

    btn.addEventListener("click", () => {
      currentTeam = code;
      updateTeam(code);
      document
        .querySelectorAll(".team-logo-btn")
        .forEach((el) => el.classList.remove("active"));
      btn.classList.add("active");
    });

    teamTabsEl.appendChild(btn);
  });

  const first = teamTabsEl.querySelector(".team-logo-btn");
  if (first) first.classList.add("active");
}

function updateTeam(code) {
  if (!modelData) return;
  const block = modelData.best12[code];
  if (!block) return;

  teamTitleEl.textContent = `${code} – XI & Impact Player`;

  // theme the background for XI and impact card using team colour
  const themeColor = teamColors[code] || "#ffffff";

  document.documentElement.style.setProperty(
    "--accent1",
    lighten(themeColor, 0.25)
  );
  document.documentElement.style.setProperty(
    "--accent2",
    lighten(themeColor, -0.1)
  );

  renderXI(code, block.xi, themeColor);
  renderImpact(block.impact, themeColor);
}

function renderXI(teamCode, xi, themeColor) {
  xiListEl.innerHTML = "";
  const captainName = CAPTAINS[teamCode];

  xi.forEach((player, index) => {
    const li = document.createElement("li");
    li.className = "xi-item";

    const hueBg = `${hexToRgba(themeColor, 0.28)}`;
    const border = `${hexToRgba(themeColor, 0.7)}`;
    li.style.background = `radial-gradient(circle at 0 0, ${hueBg}, #050816)`;
    li.style.borderColor = border;
    li.style.animationDelay = `${index * 0.04}s`;

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

function renderImpact(impact, themeColor) {
  if (!impact || !impact.name) {
    impactCardEl.classList.add("empty");
    impactCardEl.innerHTML = "No impact player available.";
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

  const bg = hexToRgba(themeColor, 0.3);
  const border = hexToRgba(themeColor, 0.9);
  impactCardEl.style.background = `radial-gradient(circle at 0 0, ${bg}, #151932)`;
  impactCardEl.style.borderColor = border;

  impactCardEl.appendChild(label);
  impactCardEl.appendChild(name);
  impactCardEl.appendChild(meta);
}

/* Cap tables */
function renderCaps() {
  runsTableBody.innerHTML = "";
  modelData.top_runs_pred.forEach((row, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${row.name}</td>
      <td>${row.team}</td>
      <td>${(row.score * 100).toFixed(0)}</td>
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
      <td>${(row.score * 100).toFixed(0)}</td>
    `;
    wicketsTableBody.appendChild(tr);
  });
}

/* Projections */
function renderProjections() {
  projectionsBody.innerHTML = "";
  modelData.projections.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.team}</td>
      <td>${row.strength.toFixed(3)}</td>
      <td>${(row.p_top4 * 100).toFixed(1)}%</td>
      <td>${(row.p_title * 100).toFixed(1)}%</td>
    `;
    projectionsBody.appendChild(tr);
  });
}

/* Winner modal */
function wireWinner() {
  if (!winnerButton) return;
  const winnerTeam = modelData.title_favourite;

  winnerButton.addEventListener("click", () => {
    winnerNameEl.textContent = winnerTeam || "N/A";
    winnerModal.classList.remove("hidden");
  });

  closeWinnerBtn.addEventListener("click", () => {
    winnerModal.classList.add("hidden");
  });

  winnerModal.addEventListener("click", (e) => {
    if (e.target === winnerModal || e.target.classList.contains("winner-backdrop")) {
      winnerModal.classList.add("hidden");
    }
  });
}

/* Helpers */
function hexToRgba(hex, alpha) {
  if (!hex) return `rgba(255,255,255,${alpha})`;
  let h = hex.replace("#", "");
  if (h.length === 3) {
    h = h
      .split("")
      .map((c) => c + c)
      .join("");
  }
  const num = parseInt(h, 16);
  const r = (num >> 16) & 255;
  const g = (num >> 8) & 255;
  const b = num & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function lighten(hex, amount) {
  let h = hex.replace("#", "");
  if (h.length === 3) {
    h = h
      .split("")
      .map((c) => c + c)
      .join("");
  }
  let num = parseInt(h, 16);
  let r = (num >> 16) & 255;
  let g = (num >> 8) & 255;
  let b = num & 255;

  const factor = amount;
  r = clamp(Math.round(r + 255 * factor), 0, 255);
  g = clamp(Math.round(g + 255 * factor), 0, 255);
  b = clamp(Math.round(b + 255 * factor), 0, 255);

  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

function clamp(v, min, max) {
  return Math.min(max, Math.max(min, v));
}

/* Kick off */
loadModel();
