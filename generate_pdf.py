from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.set_text_color(20, 40, 80)
        self.cell(0, 10, "AI Assignment 6: Dynamic Wumpus Logic Agent", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "I", 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Submitted by: Nehza Nazir (23F-0822) | NUCES Chiniot-Faisalabad", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 30, 200, 30)
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 14)
        self.set_fill_color(230, 240, 255)
        self.set_text_color(0, 50, 100)
        self.cell(0, 10, f"  {title}", border=0, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def chapter_body(self, text):
        self.set_font("helvetica", "", 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln()

    def bullet_point(self, text):
        self.set_font("helvetica", "", 11)
        self.set_text_color(0, 0, 0)
        self.cell(5, 6, chr(149)) # Bullet character
        self.multi_cell(0, 6, text)
        self.ln(2)

pdf = PDF()
pdf.add_page()

# --- 1. Links Section ---
pdf.chapter_title("1. Mandatory Links")
pdf.set_font("helvetica", "B", 11)
pdf.cell(40, 8, "GitHub Repo:")
pdf.set_font("helvetica", "U", 11)
pdf.set_text_color(0, 0, 255)
pdf.cell(0, 8, "https://github.com/Nehza-Nazir/Wumpus-Logic-Agent", link="https://github.com/Nehza-Nazir/Wumpus-Logic-Agent", new_x="LMARGIN", new_y="NEXT")

pdf.set_text_color(0, 0, 0)
pdf.set_font("helvetica", "B", 11)
pdf.cell(40, 8, "Vercel / Live URL:")
pdf.set_font("helvetica", "U", 11)
pdf.set_text_color(0, 0, 255)
pdf.cell(0, 8, "https://wumpus-logic-agent-weld.vercel.app/", link="https://wumpus-logic-agent-weld.vercel.app/", new_x="LMARGIN", new_y="NEXT")

pdf.set_text_color(0, 0, 0)
pdf.set_font("helvetica", "B", 11)
pdf.cell(40, 8, "LinkedIn Post:")
pdf.set_font("helvetica", "U", 11)
pdf.set_text_color(0, 0, 255)
pdf.cell(0, 8, "[Paste your LinkedIn Post URL here]", link="", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(8)

# --- 2. Introduction & Environment Specs ---
pdf.chapter_title("2. Project Objective & Specifications")
intro_text = (
    "The objective of this project is to develop a Web-based Dynamic Pathfinding Agent that acts as a strictly "
    "Knowledge-Based Agent. The agent navigates a Wumpus World grid by receiving dynamic percepts (Breeze, Stench, Glitter) "
    "and utilizes Propositional Logic coupled with Resolution Refutation to deductively prove whether adjacent unvisited cells "
    "are safe to explore.\n\n"
    "Key specifications implemented:\n"
    "- Dynamic Grid Configuration: Users can define Rows, Columns, and number of Pits at runtime.\n"
    "- Hidden Hazards: Pits and the Wumpus are placed randomly. The agent does NOT know their locations initially.\n"
    "- Strict Logic Execution: The agent only moves to cells that have been mathematically proven safe via the Resolution engine."
)
pdf.chapter_body(intro_text)

# --- 3. CNF Conversion Logic ---
pdf.chapter_title("3. Propositional Logic & CNF Conversion")
cnf_text1 = (
    "The core of the Knowledge Base (KB) relies on maintaining rules in Conjunctive Normal Form (CNF). "
    "When the agent receives a percept (e.g., a Breeze) at a cell (r,c), it signifies that at least one adjacent cell "
    "(a1, a2, etc.) contains a Pit. Conversely, if an adjacent cell contains a Pit, the current cell MUST have a Breeze. "
    "This is represented as a biconditional rule:\n\n"
    "        Breeze(r,c) <==> Pit(a1) v Pit(a2) v ... v Pit(an)\n\n"
    "To enable programmatic Resolution, this biconditional is automatically translated into the following CNF clauses:"
)
pdf.chapter_body(cnf_text1)

pdf.bullet_point("~Breeze(r,c) v Pit(a1) v Pit(a2) ... (If there is a breeze, there is a pit in an adjacent cell)")
pdf.bullet_point("~Pit(a1) v Breeze(r,c) (If there is a pit at a1, the current cell will have a breeze)")
pdf.bullet_point("~Pit(a2) v Breeze(r,c) (If there is a pit at a2, the current cell will have a breeze)")

cnf_text2 = (
    "\nFurthermore, the percept itself is added as a unit clause. If a breeze is felt, {Breeze(r,c)} is added. "
    "If no breeze is felt, {~Breeze(r,c)} is added.\n\n"
    "Optimization via Unit Propagation:\n"
    "If no breeze is felt, the algorithm efficiently resolves {~Breeze(r,c)} against {~Pit(ai) v Breeze(r,c)} to immediately "
    "yield {~Pit(ai)} for all adjacent cells, categorically proving them safe from pits in a single resolution step."
)
pdf.chapter_body(cnf_text2)

# --- 4. Resolution Refutation Algorithm ---
pdf.add_page()
pdf.chapter_title("4. Resolution Refutation Algorithm Implementation")
res_text1 = (
    "Before making a move to any adjacent, unvisited cell, the agent MUST query its KB: \"Is cell (r,c) safe?\". "
    "A cell is safe only if we can prove both ~Pit(r,c) AND ~Wumpus(r,c). The python backend implements an automated "
    "Resolution Refutation Engine to prove these goals.\n\n"
    "Proof by Contradiction Loop:\n"
    "1. Negate the Goal: To prove ~Pit(r,c), the system assumes the opposite: Pit(r,c) is True. It temporarily adds {Pit(r,c)} to the KB.\n"
    "2. Set-of-Support Strategy: Rather than performing an exhaustive O(N^2) comparison of all clauses in the KB (which causes severe "
    "performance bottlenecks), the engine employs a 'Set-of-Support' strategy. It strictly resolves the negated goal (and any newly "
    "derived resolvents from it) against the existing KB clauses.\n"
    "3. Resolution Rule: Two clauses containing complementary literals (e.g., L and ~L) are merged, dropping the complementary pair.\n"
    "4. Deriving the Empty Clause: If merging two clauses results in an empty set {}, a logical contradiction has been found. "
    "Because the KB facts are absolute, the contradiction proves that our assumption {Pit(r,c)} was inherently false. "
    "Therefore, ~Pit(r,c) is mathematically proven.\n\n"
    "If the algorithm reaches its maximum iteration limit without deriving the empty clause, the safety of the cell remains UNKNOWN. "
    "The agent is programmed to strictly avoid unknown cells to guarantee its survival."
)
pdf.chapter_body(res_text1)

# --- 5. Architecture & Visualization ---
pdf.chapter_title("5. System Architecture & UI Visualization")
arch_text = (
    "The project utilizes a modern decoupled architecture:\n\n"
    "Backend (Python/Flask):\n"
    "Contains the Knowledge Base class, the Resolution Engine, and the Agent loop. The logic is kept entirely stateless between API calls "
    "by rebuilding the KB from the agent's percept history during every step. This design makes it perfectly suited for Serverless deployment on Vercel.\n\n"
    "Frontend (Vanilla HTML/CSS/JS):\n"
    "A custom-built, premium 'Glassmorphism' dark-theme UI was developed to satisfy the visualization requirements without relying on bulky frameworks. "
    "It features:\n"
    "- A dynamic grid mapping Safe cells (Green), Unknown cells (Gray), and Danger/Pits (Red).\n"
    "- A Real-Time Metrics Dashboard tracking Agent Steps, Inference Steps, KB Clauses, and active percepts.\n"
    "- A live Resolution Log that prints the mathematical proof outcomes generated by the backend during every decision cycle."
)
pdf.chapter_body(arch_text)

pdf.image("p1.png", x=30, w=150)

pdf.output("AI_A6_Report_23F-0822.pdf")
print("Detailed PDF generated.")
