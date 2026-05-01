/**
 * Wumpus World Logic Agent – Frontend Application
 * 23F-0822 Nehza Nazir | NUCES Chiniot-Faisalabad
 */

const API_BASE = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000"
    : "";

// ── State ──
let gameState = null;
let autoRunning = false;
let autoTimer = null;

// ── DOM References ──
const $ = (id) => document.getElementById(id);
const btnInit = $("btn-init");
const btnStep = $("btn-step");
const btnAuto = $("btn-auto");
const btnReset = $("btn-reset");
const inputRows = $("input-rows");
const inputCols = $("input-cols");
const inputPits = $("input-pits");
const gridContainer = $("grid-container");
const statusBanner = $("status-banner");
const statusText = $("status-text");
const logContainer = $("log-container");

// ── Metric Elements ──
const valSteps = $("val-steps");
const valInferences = $("val-inferences");
const valKb = $("val-kb");
const valSafe = $("val-safe");

// ── Percept Elements ──
const perceptBreeze = $("percept-breeze");
const perceptStench = $("percept-stench");
const perceptGlitter = $("percept-glitter");

// ══════════════════════════════════════
//  API Calls
// ══════════════════════════════════════

async function apiInit(rows, cols, numPits) {
    const res = await fetch(`${API_BASE}/api/init`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rows, cols, num_pits: numPits }),
    });
    if (!res.ok) throw new Error(`Init failed: ${res.status}`);
    return res.json();
}

async function apiStep(state) {
    const res = await fetch(`${API_BASE}/api/step`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state }),
    });
    if (!res.ok) throw new Error(`Step failed: ${res.status}`);
    return res.json();
}

// ══════════════════════════════════════
//  Grid Rendering
// ══════════════════════════════════════

function renderGrid() {
    if (!gameState) return;
    const { rows, cols } = gameState.env;
    const agentPos = gameState.agent_pos;
    const visited = new Set(gameState.visited.map(v => `${v[0]}_${v[1]}`));
    const safeCells = new Set((gameState.safe_cells || []).map(s => `${s[0]}_${s[1]}`));
    const perceptHistory = gameState.percept_history || {};
    const alive = gameState.alive;
    const won = gameState.won;

    // Hidden info (for reveal on game end)
    const pits = new Set(gameState.env.pits.map(p => `${p[0]}_${p[1]}`));
    const wumpus = gameState.env.wumpus ? `${gameState.env.wumpus[0]}_${gameState.env.wumpus[1]}` : null;
    const gold = gameState.env.gold ? `${gameState.env.gold[0]}_${gameState.env.gold[1]}` : null;
    const gameOver = !alive || won;

    // Create or update grid
    let grid = document.getElementById("world-grid");
    if (!grid) {
        gridContainer.innerHTML = "";
        grid = document.createElement("div");
        grid.id = "world-grid";
        grid.style.gridTemplateColumns = `repeat(${cols}, 65px)`;
        gridContainer.appendChild(grid);
    }
    grid.style.gridTemplateColumns = `repeat(${cols}, 65px)`;
    grid.innerHTML = "";

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const key = `${r}_${c}`;
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.dataset.row = r;
            cell.dataset.col = c;

            const isAgent = agentPos[0] === r && agentPos[1] === c;
            const isVisited = visited.has(key);
            const isSafe = safeCells.has(key);
            const isPit = pits.has(key);
            const isWumpus = key === wumpus;
            const isGold = key === gold;
            const percData = perceptHistory[key];

            // Determine cell class
            if (isAgent && !alive) {
                cell.classList.add("cell-dead");
            } else if (isAgent) {
                cell.classList.add("cell-agent");
            } else if (gameOver && isPit) {
                cell.classList.add("cell-danger");
            } else if (gameOver && isWumpus) {
                cell.classList.add("cell-danger");
            } else if (isGold && (gameOver || (isVisited && won))) {
                cell.classList.add("cell-gold");
            } else if (isVisited) {
                cell.classList.add("cell-visited");
            } else if (isSafe) {
                cell.classList.add("cell-safe");
            } else {
                cell.classList.add("cell-unknown");
            }

            // Icon
            const iconDiv = document.createElement("div");
            iconDiv.classList.add("cell-icon");
            if (isAgent && !alive) {
                iconDiv.innerHTML = '<i class="fas fa-skull"></i>';
            } else if (isAgent) {
                iconDiv.innerHTML = '<i class="fas fa-robot"></i>';
            } else if (gameOver && isPit) {
                iconDiv.innerHTML = '<i class="fas fa-circle-exclamation"></i>';
            } else if (gameOver && isWumpus) {
                iconDiv.innerHTML = '<i class="fas fa-dragon"></i>';
            } else if (isGold && gameOver) {
                iconDiv.innerHTML = '<i class="fas fa-gem"></i>';
            } else if (isVisited) {
                iconDiv.innerHTML = '<i class="fas fa-check-circle"></i>';
            } else if (isSafe) {
                iconDiv.innerHTML = '<i class="fas fa-shield-halved"></i>';
            } else {
                iconDiv.innerHTML = '<i class="fas fa-question"></i>';
            }
            cell.appendChild(iconDiv);

            // Coordinate label
            const label = document.createElement("div");
            label.classList.add("cell-label");
            label.textContent = `${r},${c}`;
            cell.appendChild(label);

            // Percept icons for visited cells
            if (percData && isVisited) {
                const percDiv = document.createElement("div");
                percDiv.classList.add("cell-percepts");
                if (percData.breeze) percDiv.innerHTML += '<i class="fas fa-wind breeze-icon" title="Breeze"></i>';
                if (percData.stench) percDiv.innerHTML += '<i class="fas fa-skull-crossbones stench-icon" title="Stench"></i>';
                if (percDiv.innerHTML) cell.appendChild(percDiv);
            }

            grid.appendChild(cell);
        }
    }
}

// ══════════════════════════════════════
//  UI Updates
// ══════════════════════════════════════

function updateMetrics(stepData) {
    if (!gameState) return;
    valSteps.textContent = gameState.step_count || 0;
    valInferences.textContent = gameState.inference_steps_total || 0;
    valKb.textContent = stepData?.kb_size || 0;
    valSafe.textContent = (gameState.safe_cells || []).length;
}

function updatePercepts(percepts) {
    perceptBreeze.classList.toggle("active-breeze", !!percepts?.breeze);
    perceptStench.classList.toggle("active-stench", !!percepts?.stench);
    perceptGlitter.classList.toggle("active-glitter", !!percepts?.glitter);
}

function setStatus(msg, type) {
    statusText.textContent = msg;
    statusBanner.className = "glass-card";
    statusBanner.classList.add(`status-${type}`);
    const icon = statusBanner.querySelector("i");
    const icons = { idle: "fa-circle-info", active: "fa-robot", win: "fa-trophy", dead: "fa-skull-crossbones" };
    icon.className = `fas ${icons[type] || "fa-circle-info"}`;
}

function addLog(msg, type = "info") {
    const entry = document.createElement("div");
    entry.classList.add("log-entry", `log-${type}`);
    entry.textContent = msg;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function clearLog() {
    logContainer.innerHTML = "";
}

function setButtons(init, step, auto, reset) {
    btnInit.disabled = !init;
    btnStep.disabled = !step;
    btnAuto.disabled = !auto;
    btnReset.disabled = !reset;
}

// ══════════════════════════════════════
//  Event Handlers
// ══════════════════════════════════════

btnInit.addEventListener("click", async () => {
    const rows = parseInt(inputRows.value) || 4;
    const cols = parseInt(inputCols.value) || 4;
    const pits = parseInt(inputPits.value) || 2;

    setStatus("Initializing game...", "active");
    setButtons(false, false, false, false);
    clearLog();
    addLog(`Creating ${rows}×${cols} grid with ${pits} pits...`, "info");

    try {
        const data = await apiInit(rows, cols, pits);
        gameState = data.state;
        renderGrid();
        updateMetrics({});
        updatePercepts(gameState.current_percepts);
        setStatus("Game started! Agent at (0,0). Click Step to explore.", "active");
        addLog(data.message, "success");
        if (gameState.current_percepts?.breeze) addLog("[WARNING] Breeze detected at (0,0)!", "warning");
        if (gameState.current_percepts?.stench) addLog("[WARNING] Stench detected at (0,0)!", "warning");
        if (!gameState.current_percepts?.breeze && !gameState.current_percepts?.stench) {
            addLog("No percepts at (0,0). Adjacent cells likely safe.", "info");
        }
        setButtons(true, true, true, true);
    } catch (e) {
        setStatus("Failed to connect to backend!", "dead");
        addLog(`Error: ${e.message}`, "danger");
        setButtons(true, false, false, false);
    }
});

btnStep.addEventListener("click", async () => {
    if (!gameState || !gameState.alive || gameState.won) return;
    await performStep();
});

async function performStep() {
    setButtons(false, false, false, false);
    try {
        const data = await apiStep(gameState);
        gameState = data.state;
        renderGrid();
        updateMetrics(data);
        updatePercepts(data.percepts);

        // Log resolution info
        if (data.resolution_log && data.resolution_log.length > 0) {
            addLog(`── Step ${gameState.step_count} Resolution ──`, "step");
            data.resolution_log.forEach(l => {
                if (l.includes("PROVEN")) addLog(l, "success");
                else if (l.includes("Cannot prove")) addLog(l, "warning");
                else addLog(l, "info");
            });
        }

        addLog(data.message, data.state.alive ? (data.state.won ? "success" : "step") : "danger");

        if (!gameState.alive) {
            setStatus("Agent died! Game Over.", "dead");
            setButtons(true, false, false, true);
            stopAuto();
            renderGrid(); // re-render to reveal grid
        } else if (gameState.won) {
            setStatus("Gold found! Agent wins!", "win");
            setButtons(true, false, false, true);
            stopAuto();
            renderGrid();
        } else {
            setStatus(`Agent at (${gameState.agent_pos[0]},${gameState.agent_pos[1]}). Step ${gameState.step_count}.`, "active");
            setButtons(true, true, true, true);
        }

        // Check if stuck
        if (data.message.includes("stuck")) {
            addLog("Agent cannot find any provably safe cells to explore.", "warning");
            setButtons(true, false, false, true);
            stopAuto();
        }
    } catch (e) {
        addLog(`Error: ${e.message}`, "danger");
        setButtons(true, true, true, true);
        stopAuto();
    }
}

btnAuto.addEventListener("click", () => {
    if (autoRunning) {
        stopAuto();
    } else {
        startAuto();
    }
});

function startAuto() {
    autoRunning = true;
    btnAuto.innerHTML = '<i class="fas fa-pause"></i> Pause';
    addLog("Auto-run started...", "info");
    autoStep();
}

function stopAuto() {
    autoRunning = false;
    if (autoTimer) clearTimeout(autoTimer);
    autoTimer = null;
    btnAuto.innerHTML = '<i class="fas fa-forward"></i> Auto-Run';
}

async function autoStep() {
    if (!autoRunning || !gameState || !gameState.alive || gameState.won) {
        stopAuto();
        return;
    }
    await performStep();
    if (autoRunning && gameState?.alive && !gameState?.won) {
        autoTimer = setTimeout(autoStep, 800);
    }
}

btnReset.addEventListener("click", () => {
    stopAuto();
    gameState = null;
    gridContainer.innerHTML = `
        <div id="grid-placeholder">
            <i class="fas fa-gamepad"></i>
            <p>Configure the grid and click <strong>New Game</strong> to start</p>
        </div>`;
    valSteps.textContent = "0";
    valInferences.textContent = "0";
    valKb.textContent = "0";
    valSafe.textContent = "0";
    updatePercepts(null);
    setStatus("Awaiting initialization...", "idle");
    clearLog();
    addLog("System ready. Configure grid and start a new game.", "info");
    setButtons(true, false, false, false);
});

// ── Animate metric values ──
function animateValue(el, end) {
    const start = parseInt(el.textContent) || 0;
    if (start === end) return;
    const diff = end - start;
    const steps = Math.min(Math.abs(diff), 20);
    const inc = diff / steps;
    let current = start;
    let i = 0;
    const timer = setInterval(() => {
        i++;
        current += inc;
        el.textContent = Math.round(current);
        if (i >= steps) {
            el.textContent = end;
            clearInterval(timer);
        }
    }, 30);
}

// Override updateMetrics to animate
const _origUpdateMetrics = updateMetrics;
updateMetrics = function(stepData) {
    if (!gameState) return;
    animateValue(valSteps, gameState.step_count || 0);
    animateValue(valInferences, gameState.inference_steps_total || 0);
    animateValue(valKb, stepData?.kb_size || parseInt(valKb.textContent) || 0);
    animateValue(valSafe, (gameState.safe_cells || []).length);
};

// ── Init ──
addLog("System ready. Configure grid and start a new game.", "info");
