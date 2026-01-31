import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QMessageBox,
    QRadioButton, QFileDialog
)

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

class DNAProteinGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DNA → Protein (PyQt6)")
        self.setMinimumSize(650, 560)

        layout = QVBoxLayout()

        # --- tryb wejścia ---
        self.rb_text = QRadioButton("Wklej sekwencję DNA (A C G T)")
        self.rb_fasta = QRadioButton("Importuj plik FASTA")
        self.rb_text.setChecked(True)

        layout.addWidget(self.rb_text)
        layout.addWidget(self.rb_fasta)

        self.info = QLabel("Dozwolone znaki: A C G T")
        layout.addWidget(self.info)

        # --- DNA ---
        self.dna_text = QTextEdit()
        self.dna_text.setPlaceholderText("Sekwencja DNA")
        layout.addWidget(self.dna_text)

        # --- przyciski ---
        btn_layout = QHBoxLayout()
        self.btn_load = QPushButton("Wczytaj FASTA")
        self.btn_check = QPushButton("Sprawdź DNA")
        self.btn_translate = QPushButton("Tłumacz na białko")

        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_check)
        btn_layout.addWidget(self.btn_translate)
        layout.addLayout(btn_layout)

        # --- protein ---
        layout.addWidget(QLabel("Sekwencja białka:"))
        self.protein_text = QTextEdit()
        self.protein_text.setReadOnly(True)
        layout.addWidget(self.protein_text)

        self.setLayout(layout)

        # --- sygnały ---
        self.rb_text.toggled.connect(self.update_mode)
        self.btn_load.clicked.connect(self.load_fasta)
        self.btn_check.clicked.connect(self.validate_dna)
        self.btn_translate.clicked.connect(self.translate_dna)

        self.update_mode()

    def update_mode(self):
        self.btn_load.setDisabled(self.rb_text.isChecked())

    def load_fasta(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik FASTA",
            "",
            "FASTA (*.fa *.fasta *.txt)"
        )
        if not file:
            return

        try:
            seq = ""
            with open(file) as f:
                for line in f:
                    if not line.startswith(">"):
                        seq += line.strip()

            self.dna_text.setText(seq.upper())

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    def validate_dna(self):
        dna = self.get_dna()
        if dna:
            QMessageBox.information(
                self,
                "OK",
                f"Sekwencja poprawna\nDługość: {len(dna)}"
            )

    def get_dna(self):
        dna = self.dna_text.toPlainText().upper().replace("\n", "").strip()

        if not dna:
            QMessageBox.warning(self, "Błąd", "Sekwencja jest pusta")
            return None

        if not re.fullmatch(r"[ACGT]+", dna):
            QMessageBox.critical(
                self,
                "Błąd sekwencji",
                "Sekwencja może zawierać tylko:\nA C G T"
            )
            return None

        return dna

    def translate_dna(self):
        dna = self.get_dna()
        if not dna:
            return

        if len(dna) % 3 != 0:
            QMessageBox.warning(
                self,
                "Uwaga",
                "Długość sekwencji nie jest podzielna przez 3"
            )

        protein = ""
        for i in range(0, len(dna) - 2, 3):
            codon = dna[i:i+3]
            aa = CODON_TABLE.get(codon, "X")

            # OPCJA A: STOP → '-'
            if aa == "*":
                protein += "-"
            else:
                protein += aa

        self.protein_text.setText(protein)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DNAProteinGUI()
    window.show()
    sys.exit(app.exec())
