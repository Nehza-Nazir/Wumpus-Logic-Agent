"""
Dynamic Wumpus Logic Agent - Backend API
=========================================
Knowledge-Based Agent using Propositional Logic & Resolution Refutation
Student: 23F-0822 Nehza Nazir | NUCES Chiniot-Faisalabad
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from collections import deque

app = Flask(__name__)
CORS(app)

# ------------------------------------
#  Propositional Logic Utilities
# ------------------------------------

def lit(name, neg=False):
    return (name, neg)

def neg_lit(l):
    return (l[0], not l[1])

def lit_str(l):
    return ("~" + l[0]) if l[1] else l[0]

def clause_str(c):
    if not c:
        return "{} (empty clause)"
    return "{ " + " v ".join(lit_str(l) for l in sorted(c, key=lambda x: x[0])) + " }"

def resolve_pair(c1, c2):
    """Resolve two frozenset clauses. Returns list of resolvent frozensets."""
    resolvents = []
    for l1 in c1:
        comp = neg_lit(l1)
        if comp in c2:
            new_lits = (c1 - {l1}) | (c2 - {comp})
            # Tautology check
            if not any(neg_lit(x) in new_lits for x in new_lits):
                resolvents.append(frozenset(new_lits))
    return resolvents

# ------------------------------------
#  Knowledge Base with Resolution
# ------------------------------------

class KnowledgeBase:
    def __init__(self):
        self.clauses = set()
        self.inference_count = 0
        # Cache: directly proven safe propositions
        self._proven_safe = set()

    def tell(self, clause):
        self.clauses.add(clause)

    def tell_percept(self, row, col, percept_type, has_percept, adjacents):
        """
        Encode: Percept_r_c <=> Hazard_a1 v Hazard_a2 v ...
        CNF form:
          {~Percept, H_a1, H_a2, ...}
          {~H_ai, Percept} for each ai
        Plus fact: {Percept} or {~Percept}
        """
        prefix = "B" if percept_type == "breeze" else "S"
        haz = "P" if percept_type == "breeze" else "W"
        perc = lit(f"{prefix}_{row}_{col}")
        h_lits = [lit(f"{haz}_{r}_{c}") for r, c in adjacents]

        # Biconditional in CNF
        self.tell(frozenset([neg_lit(perc)] + h_lits))
        for hl in h_lits:
            self.tell(frozenset([neg_lit(hl), perc]))

        # Fact
        if has_percept:
            self.tell(frozenset([perc]))
        else:
            self.tell(frozenset([neg_lit(perc)]))
            # Optimization: if no percept, we can immediately derive ~H for each adj
            # because {~Percept} + {~H_ai, Percept} resolves to {~H_ai}
            for hl in h_lits:
                self.tell(frozenset([neg_lit(hl)]))
                self._proven_safe.add(hl[0])  # e.g. "P_1_0"

    def tell_no_hazard(self, row, col):
        self.tell(frozenset([lit(f"P_{row}_{col}", True)]))
        self.tell(frozenset([lit(f"W_{row}_{col}", True)]))
        self._proven_safe.add(f"P_{row}_{col}")
        self._proven_safe.add(f"W_{row}_{col}")

    def ask_safe(self, row, col):
        """Check if ~P_r_c AND ~W_r_c can be proven."""
        p_name = f"P_{row}_{col}"
        w_name = f"W_{row}_{col}"

        # Fast path: check cache
        if p_name in self._proven_safe and w_name in self._proven_safe:
            log = [
                f"Goal: Prove ~{p_name} ^ ~{w_name}",
                f"[FAST] ~{p_name} already proven (unit clause in KB)",
                f"[FAST] ~{w_name} already proven (unit clause in KB)",
                f">> Cell ({row},{col}) is SAFE (0 resolution steps)"
            ]
            return True, 0, log

        total_steps = 0
        all_log = []

        # Check pit safety
        if p_name in self._proven_safe:
            pit_safe = True
            all_log.append(f"[FAST] ~{p_name} already proven")
        else:
            pit_safe, pit_steps, pit_log = self._resolution_refutation(p_name)
            total_steps += pit_steps
            all_log.extend(pit_log)
            if pit_safe:
                self._proven_safe.add(p_name)

        # Check wumpus safety
        if w_name in self._proven_safe:
            wump_safe = True
            all_log.append(f"[FAST] ~{w_name} already proven")
        else:
            wump_safe, wump_steps, wump_log = self._resolution_refutation(w_name)
            total_steps += wump_steps
            all_log.extend(wump_log)
            if wump_safe:
                self._proven_safe.add(w_name)

        self.inference_count += total_steps
        is_safe = pit_safe and wump_safe
        verdict = "SAFE" if is_safe else "UNKNOWN"
        all_log.append(f">> Cell ({row},{col}) is {verdict} ({total_steps} resolution steps)")
        return is_safe, total_steps, all_log

    def _resolution_refutation(self, prop_name):
        """
        Prove ~prop via resolution refutation.
        Add {prop} to KB, try to derive empty clause {}.
        Uses set-of-support strategy for efficiency.
        """
        log = []
        log.append(f"Goal: Prove ~{prop_name}")
        log.append(f"Assume {prop_name} (negate the goal)")

        assumption = frozenset([lit(prop_name)])

        # Check immediate: is {~prop} already in KB?
        neg_clause = frozenset([lit(prop_name, True)])
        if neg_clause in self.clauses:
            log.append(f"Resolved {clause_str(assumption)} x {clause_str(neg_clause)} -> empty")
            log.append(f">> ~{prop_name} PROVEN in 1 step")
            return True, 1, log

        # Set-of-support resolution: only resolve new clauses with KB
        support = {assumption}
        all_kb = set(self.clauses)
        new_this_round = set()
        steps = 0
        MAX_STEPS = 3000

        log.append(f"KB has {len(all_kb)} clauses, starting resolution...")

        while steps < MAX_STEPS:
            new_this_round.clear()
            found = False

            for s_clause in list(support):
                for kb_clause in list(all_kb | support):
                    if s_clause == kb_clause:
                        continue
                    resolvents = resolve_pair(s_clause, kb_clause)
                    steps += 1

                    for r in resolvents:
                        if len(r) == 0:
                            log.append(f"Resolved {clause_str(s_clause)} x {clause_str(kb_clause)} -> empty")
                            log.append(f">> ~{prop_name} PROVEN in {steps} steps")
                            return True, steps, log
                        if r not in all_kb and r not in support:
                            new_this_round.add(r)

                    if steps >= MAX_STEPS:
                        found = True
                        break
                if found:
                    break

            if not new_this_round:
                log.append(f"No new clauses derived. Cannot prove ~{prop_name} ({steps} steps)")
                return False, steps, log

            support |= new_this_round

        log.append(f"Step limit reached for ~{prop_name} ({steps} steps)")
        return False, steps, log


# ------------------------------------
#  Wumpus World Environment
# ------------------------------------

class WumpusWorld:
    def __init__(self, rows, cols, num_pits):
        self.rows = rows
        self.cols = cols
        self.pits = []
        self.wumpus = None
        self.gold = None
        self._generate(num_pits)

    def _generate(self, num_pits):
        all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        all_cells.remove((0, 0))
        random.shuffle(all_cells)
        self.wumpus = all_cells.pop()
        actual_pits = min(num_pits, len(all_cells))
        self.pits = [all_cells.pop() for _ in range(actual_pits)]
        if all_cells:
            self.gold = all_cells.pop()
        else:
            self.gold = (self.rows - 1, self.cols - 1)

    def get_adjacent(self, r, c):
        adj = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                adj.append((nr, nc))
        return adj

    def get_percepts(self, r, c):
        adj = self.get_adjacent(r, c)
        breeze = any((ar, ac) in self.pits for ar, ac in adj)
        stench = any((ar, ac) == self.wumpus for ar, ac in adj)
        glitter = (r, c) == self.gold
        return {"breeze": breeze, "stench": stench, "glitter": glitter}

    def is_pit(self, r, c):
        return (r, c) in self.pits

    def is_wumpus(self, r, c):
        return (r, c) == self.wumpus

    def serialize(self):
        return {
            "rows": self.rows, "cols": self.cols,
            "pits": self.pits,
            "wumpus": list(self.wumpus) if self.wumpus else None,
            "gold": list(self.gold) if self.gold else None,
        }

    @staticmethod
    def from_data(data):
        env = WumpusWorld.__new__(WumpusWorld)
        env.rows = data["rows"]
        env.cols = data["cols"]
        env.pits = [tuple(p) for p in data["pits"]]
        env.wumpus = tuple(data["wumpus"]) if data["wumpus"] else None
        env.gold = tuple(data["gold"]) if data["gold"] else None
        return env


# ------------------------------------
#  Logic Agent
# ------------------------------------

class LogicAgent:
    def __init__(self, env):
        self.env = env
        self.kb = KnowledgeBase()
        self.pos = (0, 0)
        self.visited = set()
        self.safe_cells = {(0, 0)}
        self.frontier = []
        self.alive = True
        self.won = False
        self.move_history = [(0, 0)]
        self.kb.tell_no_hazard(0, 0)

    def rebuild_from_state(self, state):
        """Restore agent state from serialized data."""
        self.pos = tuple(state["agent_pos"])
        self.alive = state["alive"]
        self.won = state["won"]
        self.visited = set(tuple(v) for v in state["visited"])
        self.safe_cells = set(tuple(s) for s in state["safe_cells"])
        self.move_history = [tuple(m) for m in state["move_history"]]
        # Rebuild KB from percept history
        for key, percs in state["percept_history"].items():
            r, c = map(int, key.split("_"))
            adj = self.env.get_adjacent(r, c)
            self.kb.tell_percept(r, c, "breeze", percs["breeze"], adj)
            self.kb.tell_percept(r, c, "stench", percs["stench"], adj)
            self.kb.tell_no_hazard(r, c)

    def step(self):
        """One agent step: perceive -> reason -> decide -> move."""
        if not self.alive or self.won:
            return self._result("Agent is no longer active.", [])

        r, c = self.pos
        self.visited.add((r, c))

        # Death check
        if self.env.is_pit(r, c):
            self.alive = False
            return self._result(f"Agent fell into a PIT at ({r},{c})! Game Over.", [])
        if self.env.is_wumpus(r, c):
            self.alive = False
            return self._result(f"Agent eaten by WUMPUS at ({r},{c})! Game Over.", [])

        # Perceive
        percepts = self.env.get_percepts(r, c)

        # Tell KB about current cell
        adj = self.env.get_adjacent(r, c)
        self.kb.tell_percept(r, c, "breeze", percepts["breeze"], adj)
        self.kb.tell_percept(r, c, "stench", percepts["stench"], adj)
        self.kb.tell_no_hazard(r, c)

        # Gold check
        if percepts["glitter"]:
            self.won = True
            return self._result(f"GOLD found at ({r},{c})! Agent wins!", [], percepts)

        # Reason about adjacent unvisited cells
        all_log = []
        for ar, ac in adj:
            if (ar, ac) not in self.visited and (ar, ac) not in self.safe_cells:
                is_safe, steps, log = self.kb.ask_safe(ar, ac)
                all_log.extend(log)
                if is_safe:
                    self.safe_cells.add((ar, ac))
                    if (ar, ac) not in self.frontier:
                        self.frontier.append((ar, ac))

        # Remove visited from frontier
        self.frontier = [f for f in self.frontier if f not in self.visited]

        # Move decision
        if self.frontier:
            target = self.frontier.pop(0)
            path = self._bfs_path(target)
            if path and len(path) > 1:
                self.pos = path[1]
            else:
                self.pos = target
            self.move_history.append(self.pos)
            msg = f"Agent moves to ({self.pos[0]},{self.pos[1]})"
        else:
            msg = "No safe unvisited cells reachable. Agent is stuck."

        return self._result(msg, all_log, percepts)

    def _bfs_path(self, target):
        q = deque([(self.pos, [self.pos])])
        seen = {self.pos}
        while q:
            (r, c), path = q.popleft()
            if (r, c) == target:
                return path
            for nr, nc in self.env.get_adjacent(r, c):
                if (nr, nc) not in seen and ((nr, nc) in self.safe_cells or (nr, nc) in self.visited):
                    seen.add((nr, nc))
                    q.append(((nr, nc), path + [(nr, nc)]))
        return None

    def _result(self, message, log, percepts=None):
        return {
            "message": message,
            "agent_pos": list(self.pos),
            "alive": self.alive,
            "won": self.won,
            "visited": [list(v) for v in self.visited],
            "safe_cells": [list(s) for s in self.safe_cells],
            "frontier": [list(f) for f in self.frontier],
            "percepts": percepts,
            "resolution_log": log,
            "inference_steps": self.kb.inference_count,
            "kb_size": len(self.kb.clauses),
            "move_history": [list(m) for m in self.move_history],
        }


# ------------------------------------
#  API Routes
# ------------------------------------

@app.route("/api/init", methods=["POST"])
def init_game():
    data = request.get_json()
    rows = int(data.get("rows", 4))
    cols = int(data.get("cols", 4))
    num_pits = int(data.get("num_pits", 2))

    env = WumpusWorld(rows, cols, num_pits)
    p = env.get_percepts(0, 0)

    state = {
        "env": env.serialize(),
        "agent_pos": [0, 0],
        "alive": True,
        "won": False,
        "visited": [[0, 0]],
        "safe_cells": [[0, 0]],
        "percept_history": {"0_0": {"breeze": p["breeze"], "stench": p["stench"]}},
        "inference_steps_total": 0,
        "step_count": 0,
        "move_history": [[0, 0]],
        "current_percepts": p,
    }
    return jsonify({"state": state, "message": "Game initialized. Agent at (0,0)."})


@app.route("/api/step", methods=["POST"])
def step_game():
    data = request.get_json()
    state = data["state"]

    env = WumpusWorld.from_data(state["env"])
    agent = LogicAgent(env)
    agent.rebuild_from_state(state)

    result = agent.step()

    # Record percepts for new position
    new_pos = tuple(result["agent_pos"])
    pos_key = f"{new_pos[0]}_{new_pos[1]}"
    if pos_key not in state["percept_history"] and result["alive"]:
        p = env.get_percepts(new_pos[0], new_pos[1])
        state["percept_history"][pos_key] = {"breeze": p["breeze"], "stench": p["stench"]}

    # Update state
    state["agent_pos"] = result["agent_pos"]
    state["alive"] = result["alive"]
    state["won"] = result["won"]
    state["visited"] = result["visited"]
    state["safe_cells"] = result["safe_cells"]
    state["inference_steps_total"] = state.get("inference_steps_total", 0) + result["inference_steps"]
    state["step_count"] = state.get("step_count", 0) + 1
    state["move_history"] = result["move_history"]
    state["current_percepts"] = result.get("percepts")

    return jsonify({
        "state": state,
        "message": result["message"],
        "resolution_log": result["resolution_log"],
        "inference_steps": result["inference_steps"],
        "kb_size": result["kb_size"],
        "percepts": result.get("percepts"),
        "frontier": result["frontier"],
    })


@app.route("/api/check", methods=["POST"])
def check_cell():
    data = request.get_json()
    state = data["state"]
    target_r = int(data["row"])
    target_c = int(data["col"])

    env = WumpusWorld.from_data(state["env"])
    agent = LogicAgent(env)
    agent.rebuild_from_state(state)

    is_safe, steps, log = agent.kb.ask_safe(target_r, target_c)
    return jsonify({"is_safe": is_safe, "steps": steps, "log": log})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "engine": "Wumpus Logic Agent v1.0"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
