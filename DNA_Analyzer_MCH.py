import sys
import re
from functools import partial
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QTabWidget, QFileDialog, QRadioButton, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from matplotlib.colors import to_rgb

# --- kod genetyczny ---
CODON_TABLE = {
    "TTT":"F","TTC":"F","TTA":"L","TTG":"L",
    "CTT":"L","CTC":"L","CTA":"L","CTG":"L",
    "ATT":"I","ATC":"I","ATA":"I","ATG":"M",
    "GTT":"V","GTC":"V","GTA":"V","GTG":"V",
    "TCT":"S","TCC":"S","TCA":"S","TCG":"S",
    "CCT":"P","CCC":"P","CCA":"P","CCG":"P",
    "ACT":"T","ACC":"T","ACA":"T","ACG":"T",
    "GCT":"A","GCC":"A","GCA":"A","GCG":"A",
    "TAT":"Y","TAC":"Y","TAA":"*","TAG":"*",
    "CAT":"H","CAC":"H","CAA":"Q","CAG":"Q",
    "AAT":"N","AAC":"N","AAA":"K","AAG":"K",
    "GAT":"D","GAC":"D","GAA":"E","GAG":"E",
    "TGT":"C","TGC":"C","TGA":"*","TGG":"W",
    "CGT":"R","CGC":"R","CGA":"R","CGG":"R",
    "AGT":"S","AGC":"S","AGA":"R","AGG":"R",
    "GGT":"G","GGC":"G","GGA":"G","GGG":"G",
}

# --- motywy i kolory ---
MOTIFS = {"ATG": True, "TATA": True, "CGCG": True, "GCGT": True}
MOTIF_COLORS = {"ATG":"#90ee90","TATA":"#ffff99","CGCG":"#add8e6","GCGT":"#ffa500"}  # HEX

MAX_SEQUENCES = 6

# ==============================
# --- główne GUI
# ==============================
class DNAAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNA Analyzer")
        self.setGeometry(100, 100, 1400, 800)

        self.sequences = [""] * MAX_SEQUENCES
        self.text_inputs = []
        self.preview_tabs = []
        self.protein_texts = []

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        self.init_sidebar(top_layout)
        self.init_tabs(top_layout)
        self.init_protein_and_log(main_layout)

    def init_sidebar(self, parent_layout):
        sidebar = QVBoxLayout()
        parent_layout.addLayout(sidebar, 1)

        group_box = QGroupBox("Import DNA")
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)

        self.rb_text = QRadioButton("Wklej sekwencje DNA")
        self.rb_fasta = QRadioButton("Importuj FASTA")
        self.rb_text.setChecked(True)
        group_layout.addWidget(self.rb_text)
        group_layout.addWidget(self.rb_fasta)

        for i in range(MAX_SEQUENCES):
            self.text_inputs.append(QTextEdit())
            self.text_inputs[i].setPlaceholderText(f"Sekwencja {i+1} DNA...")
            self.text_inputs[i].setFixedHeight(80)
            group_layout.addWidget(self.text_inputs[i])

            btn = QPushButton(f"Wczytaj FASTA - Sekwencja {i+1}")
            btn.clicked.connect(lambda _, idx=i: self.load_file(seq_num=idx))
            group_layout.addWidget(btn)

        sidebar.addWidget(group_box)

        motif_group = QGroupBox("Motywy do wyszukania")
        motif_layout = QVBoxLayout()
        motif_group.setLayout(motif_layout)

        self.motif_checkboxes = {}
        for motif in MOTIFS:
            cb = QCheckBox(motif)
            cb.setChecked(MOTIFS[motif])
            cb.stateChanged.connect(partial(self.toggle_motif, motif))
            motif_layout.addWidget(cb)
            self.motif_checkboxes[motif] = cb

        sidebar.addWidget(motif_group)

        self.btn_run_analysis = QPushButton("Uruchom analizę")
        self.btn_compare_plot = QPushButton("Pokaż heatmapę motywów")
        sidebar.addWidget(self.btn_run_analysis)
        sidebar.addWidget(self.btn_compare_plot)
        sidebar.addStretch()

    def init_tabs(self, parent_layout):
        self.tabs = QTabWidget()
        parent_layout.addWidget(self.tabs, 3)

        for i in range(MAX_SEQUENCES):
            tab = QTextEdit()
            tab.setReadOnly(True)
            self.tabs.addTab(tab, f"Sekwencja {i+1}")
            self.preview_tabs.append(tab)

        self.tab_results = QTextEdit()
        self.tab_results.setReadOnly(True)
        self.tabs.addTab(self.tab_results, "Wyniki analizy")

    def init_protein_and_log(self, layout):
        layout.addWidget(QLabel("Sekwencje białka:"))
        for i in range(MAX_SEQUENCES):
            protein_text = QTextEdit()
            protein_text.setReadOnly(True)
            protein_text.setMaximumHeight(100)
            layout.addWidget(protein_text)
            self.protein_texts.append(protein_text)

        layout.addWidget(QLabel("Logi / komunikaty:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

    def connect_signals(self):
        self.rb_text.toggled.connect(self.update_mode)
        self.btn_run_analysis.clicked.connect(self.run_analysis)
        self.btn_compare_plot.clicked.connect(self.show_comparison_heatmap)
        self.update_mode()

    def update_mode(self):
        for i in range(MAX_SEQUENCES):
            self.text_inputs[i].setDisabled(not self.rb_text.isChecked())

    def load_file(self, seq_num=0):
        file_name, _ = QFileDialog.getOpenFileName(
            self, f"Wczytaj plik FASTA - Sekwencja {seq_num+1}", "", "FASTA (*.fa *.fasta *.txt)"
        )
        if file_name:
            self.log(f"Plik wczytany dla Sekwencji {seq_num+1}: {file_name}")
            seq = ""
            with open(file_name) as f:
                for line in f:
                    if not line.startswith(">"):
                        seq += line.strip()
            seq = seq.upper()
            self.sequences[seq_num] = seq
            self.preview_tabs[seq_num].setText(seq)
            self.run_analysis()

    def toggle_motif(self, motif, state):
        MOTIFS[motif] = state != 0
        self.log(f"Motyw {motif} {'włączony' if MOTIFS[motif] else 'wyłączony'}")
        self.run_analysis()

    def run_analysis(self):
        if self.rb_text.isChecked():
            for i in range(MAX_SEQUENCES):
                self.sequences[i] = self.text_inputs[i].toPlainText().upper().replace("\n","")

        self.tab_results.clear()
        self.motif_counts = [{} for _ in range(MAX_SEQUENCES)]

        for idx, seq in enumerate(self.sequences):
            if not seq:
                continue
            counts = {}
            for motif, active in MOTIFS.items():
                if not active:
                    counts[motif] = 0
                    continue
                positions = [m.start()+1 for m in re.finditer(f"(?={motif})", seq)]
                counts[motif] = len(positions)
            self.motif_counts[idx] = counts
            line = f"Sekwencja {idx+1}: " + ", ".join(f"{motif}={count}" for motif, count in counts.items())
            self.tab_results.append(line)
            self.translate_dna(seq, self.protein_texts[idx])
            self.highlight_motifs(seq, self.preview_tabs[idx])

        self.log("Analiza motywów zakończona.")

    def translate_dna(self, seq, text_widget):
        protein = ""
        for i in range(0, len(seq)-2, 3):
            codon = seq[i:i+3]
            aa = CODON_TABLE.get(codon,"X")
            protein += "-" if aa=="*" else aa
        text_widget.setText(protein)

    def highlight_motifs(self, seq, text_widget):
        if not seq:
            text_widget.clear()
            return
        colored_chars = [''] * len(seq)
        for motif, color in MOTIF_COLORS.items():
            if MOTIFS[motif]:
                for m in re.finditer(f"(?={motif})", seq):
                    start = m.start()
                    for i in range(len(motif)):
                        colored_chars[start+i] = f'<span style="background-color:{color};">{seq[start+i]}</span>'
        result = ''.join([colored_chars[i] if colored_chars[i] else seq[i] for i in range(len(seq))])
        text_widget.setHtml(result)

    # ------------------------------
    # Heatmapa z gradientem kolorów motywów
    # ------------------------------
    def show_comparison_heatmap(self):
        if not hasattr(self, 'motif_counts'):
            self.log("Brak danych do porównania.")
            return

        class HeatmapWindow(QWidget):
            def __init__(self, motif_counts):
                super().__init__()
                self.setWindowTitle("Heatmapa motywów DNA")
                layout = QVBoxLayout()
                self.setLayout(layout)
                fig = Figure(figsize=(10,6))
                canvas = FigureCanvas(fig)
                layout.addWidget(canvas)
                ax = fig.add_subplot(111)

                motifs = list(MOTIFS.keys())
                sequences = [f"Sekwencja {i+1}" for i in range(len(motif_counts))]

                # Maksymalna liczba dla normalizacji gradientu
                max_counts = {motif: max(count.get(motif,0) for count in motif_counts) or 1 for motif in motifs}

                data_rgb = np.ones((len(motifs), len(sequences), 3))  # start white

                for i, motif in enumerate(motifs):
                    base_color = np.array(to_rgb(MOTIF_COLORS[motif]))
                    for j in range(len(sequences)):
                        count = motif_counts[j].get(motif,0)
                        if count > 0:
                            factor = count / max_counts[motif]
                            data_rgb[i,j,:] = 1 - factor*(1-base_color)  # blend with white

                ax.imshow(data_rgb, aspect='auto')

                for i in range(len(motifs)):
                    for j in range(len(sequences)):
                        ax.text(j, i, str(motif_counts[j].get(motifs[i],0)),
                                ha='center', va='center', color='black')

                ax.set_xticks(range(len(sequences)))
                ax.set_xticklabels(sequences)
                ax.set_yticks(range(len(motifs)))
                ax.set_yticklabels(motifs)

                canvas.draw()

        self.plot_window = HeatmapWindow(self.motif_counts)
        self.plot_window.show()

    def log(self, message):
        self.log_text.append(f"> {message}")

# ==============================
# uruchomienie aplikacji
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DNAAnalyzerGUI()
    window.show()
    sys.exit(app.exec())
