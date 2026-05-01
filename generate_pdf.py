from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "AI Assignment 6: Dynamic Wumpus Logic Agent", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "I", 10)
        self.cell(0, 10, "Nehza Nazir (23F-0822) | NUCES Chiniot-Faisalabad", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, border=0, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def chapter_body(self, text):
        self.set_font("helvetica", "", 11)
        self.multi_cell(0, 6, text)
        self.ln()

pdf = PDF()
pdf.add_page()

# Links section (Mandatory on the first page)
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
pdf.cell(0, 8, "[Paste your Vercel URL here]", link="", new_x="LMARGIN", new_y="NEXT")

pdf.set_text_color(0, 0, 0)
pdf.set_font("helvetica", "B", 11)
pdf.cell(40, 8, "LinkedIn Post:")
pdf.set_font("helvetica", "U", 11)
pdf.set_text_color(0, 0, 255)
pdf.cell(0, 8, "[Paste your LinkedIn Post URL here]", link="", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(10)

# Explanation Section
pdf.chapter_title("2. CNF Conversion & Knowledge Base Logic")
body1 = (
    "The Knowledge Base (KB) maintains Propositional Logic rules about the Wumpus World. "
    "When the agent receives a percept (like a Breeze or Stench) at cell (r,c), a biconditional "
    "rule is established between that percept and the possible hazards in adjacent cells (a1, a2, etc.):\n\n"
    "    B(r,c) <==> P(a1) v P(a2) v P(a3) v P(a4)\n\n"
    "To use the Resolution Refutation algorithm, these biconditional statements must be converted into "
    "Conjunctive Normal Form (CNF). The CNF conversion process yields the following clauses:\n\n"
    "1. ~B(r,c) v P(a1) v P(a2) v P(a3) v P(a4)  (If there is a breeze, at least one adjacent cell has a pit)\n"
    "2. ~P(a1) v B(r,c)                          (If there is a pit at a1, there must be a breeze)\n"
    "3. ~P(a2) v B(r,c)                          (If there is a pit at a2, there must be a breeze)\n"
    "4. ...and so on for all adjacent cells.\n\n"
    "These clauses are stored as frozen sets of literals in the KB. When a percept is definitively True or False, "
    "a unit clause (e.g., {B(r,c)} or {~B(r,c)}) is also added to the KB to represent the factual reality of that cell."
)
pdf.chapter_body(body1)

pdf.chapter_title("3. Resolution Refutation Loop")
body2 = (
    "Before the agent moves to an unvisited cell, it must PROVE that the cell is safe. A cell is considered safe "
    "if there is no Pit (~P) AND no Wumpus (~W).\n\n"
    "The Resolution Refutation algorithm operates via proof by contradiction:\n"
    "1. Negate the Goal: To prove ~P(r,c), we assume P(r,c) is True and add the clause {P(r,c)} to the KB.\n"
    "2. Set-of-Support Resolution: Instead of resolving all clauses against each other (which is computationally "
    "expensive), the algorithm strictly resolves the negated goal (and its subsequent resolvents) against the existing KB.\n"
    "3. Clause Resolution: Two clauses are resolved if they contain complementary literals (e.g., P and ~P). "
    "The resolvent is the union of the two clauses, minus the complementary literals.\n"
    "4. Contradiction Check: If the resolution process produces an empty clause {}, a contradiction has been found. "
    "This means our assumption (P) was false, thereby proving our original goal (~P) is True.\n\n"
    "If the algorithm explores all possible resolvents without deriving the empty clause, the safety of the cell "
    "remains UNKNOWN, and the agent will not step there. This engine runs automatically before every move to build a frontier of provably safe cells."
)
pdf.chapter_body(body2)

pdf.output("AI_A6_Report_23F-0822.pdf")
print("PDF generated.")
