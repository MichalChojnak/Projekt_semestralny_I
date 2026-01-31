import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QTabWidget, QMenuBar, QMenu,
    QFileDialog, QRadioButton, QGroupBox
)
from PyQt6.QtGui import QAction  # <- poprawny import w PyQt6
from PyQt6.QtCore import Qt

# --- standardowy kod genetyczny ---
CODON_TABLE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


class DNAAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNA Analyzer")
        self.setGeometry(100, 100, 1000, 600)

        # --- Menu ---
        self.menu_bar = self.menuBar()
        self.create_menus()

        # --- central widget ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # --- główny layout: panel boczny + zakładki ---
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        # --- panel boczny ---
        sidebar = QVBoxLayout()
        top_layout.addLayout(sidebar, 1)

        # Import DNA: radio + wczytaj / pobierz
        group_box = QGroupBox("Import DNA")
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)

        self.rb_text = QRadioButton("Wklej sekwencję DNA (A C G T)")
        self.rb_fasta = QRadioButton("Importuj FASTA")
        self.rb_text.setChecked(True)
        group_layout.addWidget(self.rb_text)
        group_layout.addWidget(self.rb_fasta)

        self.btn_load_file = QPushButton("Wczytaj FASTA")
        self.btn_download_ncbi = QPushButton("Pobierz z NCBI (placeholder)")
        group_layout.addWidget(self.btn_load_file)
        group_layout.addWidget(self.btn_download_ncbi)

        sidebar.addWidget(group_box)

        # Analiza
        self.btn_add_motif = QPushButton("Dodaj motyw")
        self.btn_run_analysis = QPushButton("Uruchom analizę")
        self.btn_export = QPushButton("Eksportuj CSV/PDF")
        sidebar.addWidget(self.btn_add_motif)
        sidebar.addWidget(self.btn_run_analysis)
        sidebar.addWidget(self.btn_export)
        sidebar.addStretch()

        # --- zakładki ---
        self.tabs = QTabWidget()
        top_layout.addWidget(self.tabs, 3)

        self.tab_preview = QTextEdit()
        self.tab_preview.setReadOnly(True)
        self.tabs.addTab(self.tab_preview, "1) Podgląd sekwencji")

        self.tab_motifs = QTextEdit()
        self.tab_motifs.setReadOnly(True)
        self.tabs.addTab(self.tab_motifs, "2) Wybór motywów")

        self.tab_results = QTextEdit()
        self.tab_results.setReadOnly(True)
        self.tabs.addTab(self.tab_results, "3) Wyniki analizy")

        self.tab_visual = QTextEdit()
        self.tab_visual.setReadOnly(True)
        self.tabs.addTab(self.tab_visual, "4) Wizualizacja")

        self.tab_export = QTextEdit()
        self.tab_export.setReadOnly(True)
        self.tabs.addTab(self.tab_export, "5) Eksport")

        # --- protein output ---
        main_layout.addWidget(QLabel("Sekwencja białka:"))
        self.protein_text = QTextEdit()
        self.protein_text.setReadOnly(True)
        self.protein_text.setMaximumHeight(120)
        main_layout.addWidget(self.protein_text)

        # --- logi ---
        main_layout.addWidget(QLabel("Logi / komunikaty:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        main_layout.addWidget(self.log_text)

        # --- sygnały ---
        self.rb_text.toggled.connect(self.update_mode)
        self.btn_load_file.clicked.connect(self.load_file)
        self.btn_add_motif.clicked.connect(self.add_motif)
        self.btn_run_analysis.clicked.connect(self.run_analysis)

        self.update_mode()

    def create_menus(self):
        # Plik
        menu_file = self.menu_bar.addMenu("Plik")
        action_open = QAction("Otwórz", self)
        action_exit = QAction("Wyjdź", self)
        action_exit.triggered.connect(self.close)
        menu_file.addAction(action_open)
        menu_file.addAction(action_exit)

        # Motywy
        menu_motifs = self.menu_bar.addMenu("Motywy")
        action_add = QAction("Dodaj motyw", self)
        menu_motifs.addAction(action_add)

        # NCBI
        menu_ncbi = self.menu_bar.addMenu("NCBI")
        action_download = QAction("Pobierz sekwencję", self)
        menu_ncbi.addAction(action_download)

        # Eksport
        menu_export = self.menu_bar.addMenu("Eksport")
        action_csv = QAction("Eksport CSV", self)
        action_pdf = QAction("Eksport PDF", self)
        menu_export.addAction(action_csv)
        menu_export.addAction(action_pdf)

        # Pomoc
        menu_help = self.menu_bar.addMenu("Pomoc")
        action_about = QAction("O programie", self)
        menu_help.addAction(action_about)

    # --- funkcje panel boczny ---
    def update_mode(self):
        self.btn_load_file.setDisabled(self.rb_text.isChecked())

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj plik", "", "FASTA (*.fa *.fasta *.txt)"
        )
        if file_name:
            self.log(f"Plik wczytany: {file_name}")
            seq = ""
            with open(file_name) as f:
                for line in f:
                    if not line.startswith(">"):
                        seq += line.strip()
            self.tab_preview.setText(seq.upper())
            self.translate_dna(seq)

    def add_motif(self):
        motif = "ATG"
        self.log(f"Motyw: {motif} dodany")
        self.tab_motifs.append(motif)

    def run_analysis(self):
        found = 42
        self.log(f"Znaleziono {found} wystąpień")

    def log(self, message):
        self.log_text.append(f"> {message}")

    # --- translacja DNA ---
    def translate_dna(self, seq: str):
        dna = seq.upper()
        protein = ""
        for i in range(0, len(dna) - 2, 3):
            codon = dna[i:i + 3]
            aa = CODON_TABLE.get(codon, "X")
            protein += "-" if aa == "*" else aa
        self.protein_text.setText(protein)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DNAAnalyzerGUI()
    window.show()
    sys.exit(app.exec())
