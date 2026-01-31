import sys
import re
import random
from functools import partial
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QTabWidget, QFileDialog, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from matplotlib.colors import to_rgb

# --- motywy i kolory ---
MOTIFS = {"ATG": True, "TATA": True, "CGCG": True, "GCGT": True}
MOTIF_COLORS = {"ATG":"#90ee90","TATA":"#ffff99","CGCG":"#add8e6","GCGT":"#ffa500"}  # HEX

NUM_SEQUENCES = 2  # Tylko 2 sekwencje

def generate_random_sequence(length=100):
    return ''.join(random.choice("ACGT") for _ in range(length))

class DNAAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNA Analyzer")
        self.setGeometry(100, 100, 1000, 700)

        self.sequences = [""] * NUM_SEQUENCES
        self.text_inputs = []
        self.preview_tabs = []
        self.motif_counts = [{} for _ in range(NUM_SEQUENCES)]

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        self.init_sidebar(main_layout)
        self.init_tabs(main_layout)
        self.init_log(main_layout)

    def init_sidebar(self, parent_layout):
        sidebar = QVBoxLayout()
        parent_layout.addLayout(sidebar, 1)

        # Panel DNA
        dna_group = QGroupBox("Sekwencje DNA")
        dna_layout = QVBoxLayout()
        dna_group.setLayout(dna_layout)
        sidebar.addWidget(dna_group)

        for i in range(NUM_SEQUENCES):
            text_edit = QTextEdit()
            text_edit.setPlaceholderText(f"Sekwencja {i+1} DNA...")
            text_edit.setFixedHeight(80)
            self.text_inputs.append(text_edit)
            dna_layout.addWidget(text_edit)

            btn_load = QPushButton(f"Wczytaj FASTA - Sekwencja {i+1}")
            btn_load.clicked.connect(lambda _, idx=i: self.load_file(idx))
            dna_layout.addWidget(btn_load)

            btn_random = QPushButton(f"Generuj losową sekwencję {i+1}")
            btn_random.clicked.connect(lambda _, idx=i: self.fill_random_sequence(idx))
            dna_layout.addWidget(btn_random)

        # Panel motywów
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
        self.btn_compare_plot = QPushButton("Generuj heatmapę motywów")
        sidebar.addWidget(self.btn_run_analysis)
        sidebar.addWidget(self.btn_compare_plot)
        sidebar.addStretch()

    def init_tabs(self, parent_layout):
        self.tabs = QTabWidget()
        parent_layout.addWidget(self.tabs, 3)
        for i in range(NUM_SEQUENCES):
            tab = QTextEdit()
            tab.setReadOnly(True)
            self.tabs.addTab(tab, f"Sekwencja {i+1}")
            self.preview_tabs.append(tab)

        self.tab_results = QTextEdit()
        self.tab_results.setReadOnly(True)
        self.tabs.addTab(self.tab_results, "Wyniki analizy")

    def init_log(self, parent_layout):
        layout = QVBoxLayout()
        parent_layout.addLayout(layout, 1)
        layout.addWidget(QLabel("Logi / komunikaty:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

    def connect_signals(self):
        self.btn_run_analysis.clicked.connect(self.run_analysis)
        self.btn_compare_plot.clicked.connect(self.show_comparison_heatmap)

    def load_file(self, idx):
        file_name, _ = QFileDialog.getOpenFileName(self, f"Wczytaj FASTA - Sekwencja {idx+1}", "", "FASTA (*.fa *.fasta *.txt)")
        if file_name:
            self.log(f"Plik wczytany dla Sekwencji {idx+1}: {file_name}")
            seq = ""
            with open(file_name) as f:
                for line in f:
                    if not line.startswith(">"):
                        seq += line.strip()
            seq = seq.upper()
            self.sequences[idx] = seq
            self.preview_tabs[idx].setText(seq)

    def fill_random_sequence(self, idx):
        seq = generate_random_sequence(100)
        self.sequences[idx] = seq
        self.text_inputs[idx].setText(seq)
        self.preview_tabs[idx].setText(seq)
        self.log(f"Wygenerowano losową sekwencję dla Sekwencji {idx+1}")

    def toggle_motif(self, motif, state):
        MOTIFS[motif] = state != 0
        self.log(f"Motyw {motif} {'włączony' if MOTIFS[motif] else 'wyłączony'}")

    def run_analysis(self):
        for idx in range(NUM_SEQUENCES):
            seq = self.text_inputs[idx].toPlainText().upper().replace("\n","")
            self.sequences[idx] = seq

        self.tab_results.clear()
        self.motif_counts = [{} for _ in range(NUM_SEQUENCES)]

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
            self.highlight_motifs(seq, self.preview_tabs[idx])

        self.log("Analiza motywów zakończona.")

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
                        colored_chars[start+i] = f'<span style="background-color:{color}">{seq[start+i]}</span>'
        result = ''.join([colored_chars[i] if colored_chars[i] else seq[i] for i in range(len(seq))])
        text_widget.setHtml(result)

    def show_comparison_heatmap(self):
        if not any(self.motif_counts):
            self.log("Brak danych do heatmapy.")
            return

        class HeatmapWindow(QWidget):
            def __init__(self, motif_counts):
                super().__init__()
                self.setWindowTitle("Heatmapa motywów DNA")
                self.setGeometry(150, 150, 600, 400)
                layout = QVBoxLayout()
                self.setLayout(layout)
                fig = Figure(figsize=(6,4))
                canvas = FigureCanvas(fig)
                layout.addWidget(canvas)
                ax = fig.add_subplot(111)

                motifs = list(MOTIFS.keys())
                sequences = [f"Sekwencja {i+1}" for i in range(len(motif_counts))]

                max_counts = {motif: max(count.get(motif,0) for count in motif_counts) or 1 for motif in motifs}
                data_rgb = np.ones((len(motifs), len(sequences),3))  # white

                for i, motif in enumerate(motifs):
                    base_color = np.array(to_rgb(MOTIF_COLORS[motif]))
                    for j in range(len(sequences)):
                        count = motif_counts[j].get(motif,0)
                        if count>0:
                            factor = count / max_counts[motif]
                            data_rgb[i,j,:] = 1 - factor*(1-base_color)

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
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DNAAnalyzerGUI()
    window.show()
    sys.exit(app.exec())
