# Dynamic Wumpus Logic Agent 🧠

**AI Assignment 6 | 23F-0822 Nehza Nazir | NUCES Chiniot-Faisalabad**

A web-based Knowledge-Based Agent that navigates a Wumpus World grid using **Propositional Logic** and **Resolution Refutation** to deduce safe cells in real-time.

---

## 🌐 Live Demo

- **Vercel**: [Live URL will be added after deployment]
- **GitHub**: [Repository URL]
- **LinkedIn**: [Post URL]

---

## 🎯 Features

- **Dynamic Grid Sizing**: Configurable Rows × Columns (3×3 to 10×10)
- **Knowledge-Based Agent**: Maintains a Propositional Logic KB updated with percepts
- **Resolution Refutation Engine**: Automated CNF conversion and clause resolution to prove cell safety
- **Real-Time Visualization**: Color-coded grid showing Safe (Green), Unknown (Gray), Danger (Red), and Agent (Cyan)
- **Metrics Dashboard**: Live inference step count, KB clause count, and active percepts
- **Resolution Log**: Step-by-step proof trace of the resolution algorithm

---

## 🏗️ Architecture

### Backend (Python / Flask)

| Module | Description |
|--------|-------------|
| `KnowledgeBase` | Propositional Logic KB with CNF clause storage |
| `tell_percept()` | Encodes biconditional rules: `B(r,c) ⇔ P(a1) ∨ P(a2) ∨ ...` |
| `resolution_refutation()` | Set-of-support resolution strategy to prove `¬P(r,c)` |
| `LogicAgent` | BFS-based exploration using KB safety proofs |
| `WumpusWorld` | Environment with dynamic hazard placement and percept generation |

### Frontend (Vanilla HTML/CSS/JS)

- Premium dark-themed UI with glassmorphism design
- Animated grid with cell-state transitions
- Real-time metrics with animated counters
- Resolution log with color-coded proof steps

---

## 🔬 How the Resolution Engine Works

### 1. Knowledge Base (Tell)

When the agent visits cell `(r,c)` and perceives a **Breeze**:

```
B(r,c) ⇔ P(a1) ∨ P(a2) ∨ P(a3) ∨ P(a4)
```

This biconditional is converted to CNF:
```
{¬B(r,c), P(a1), P(a2), P(a3), P(a4)}     # If breeze, some adjacent has pit
{¬P(a1), B(r,c)}                            # If pit at a1, then breeze
{¬P(a2), B(r,c)}                            # If pit at a2, then breeze
...
{B(r,c)}                                    # Fact: breeze is true
```

When **no Breeze** is perceived:
```
{¬B(r,c)}     →  resolves with {¬P(ai), B(r,c)}  →  {¬P(ai)}
```
This immediately proves all adjacent cells are pit-free.

### 2. Resolution Refutation (Ask)

To prove cell `(i,j)` is safe from pits:

1. **Negate the goal**: Add `{P(i,j)}` to KB
2. **Resolve clauses**: Use set-of-support strategy
3. **Find contradiction**: If empty clause `{}` is derived → `¬P(i,j)` is proven
4. **Repeat for Wumpus**: Also prove `¬W(i,j)`

### 3. Agent Decision Loop

```
PERCEIVE → TELL KB → ASK (Resolution) → DECIDE → MOVE
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python run_dev.py

# Open browser at http://127.0.0.1:5000
```

### Deployment (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

---

## 📁 Project Structure

```
AI-AS-06/
├── api/
│   └── index.py          # Flask API + KB + Resolution Engine + Agent
├── public/
│   ├── index.html         # Main web page
│   ├── style.css          # Premium dark theme styling
│   └── app.js             # Frontend logic & grid renderer
├── run_dev.py             # Local development server
├── vercel.json            # Vercel deployment config
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 📊 Metrics Tracked

| Metric | Description |
|--------|-------------|
| Agent Steps | Number of moves the agent has made |
| Inference Steps | Total resolution operations performed |
| KB Clauses | Number of CNF clauses in the knowledge base |
| Safe Cells | Number of cells proven safe via resolution |

---

## 🎮 How to Use

1. Set grid dimensions (Rows × Columns) and number of Pits
2. Click **New Game** to initialize
3. Click **Step** to advance the agent one move at a time
4. Click **Auto-Run** for automatic exploration
5. Watch the Resolution Log for proof details
6. Monitor the Metrics Dashboard for real-time statistics

---

## 👤 Author

**Nehza Nazir** | 23F-0822  
BSc Artificial Intelligence  
NUCES Chiniot-Faisalabad Campus

---

## 📝 License

This project was developed as an academic assignment for AI coursework.
