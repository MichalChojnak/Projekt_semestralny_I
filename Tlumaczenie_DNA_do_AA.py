# DNA to Protein Translation Program

# Standard codon table
codon_table = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
}

def translate_dna(dna_seq):
    """Translate DNA sequence to protein sequence"""
    dna_seq = dna_seq.upper().replace(" ", "")
    protein_seq = ""
    for i in range(0, len(dna_seq) - 2, 3):
        codon = dna_seq[i:i + 3]
        amino_acid = codon_table.get(codon, 'X')  # 'X' if codon is unknown
        protein_seq += amino_acid
    return protein_seq

# =====================
# INTERACTIVE MENU
# =====================
print("=== DNA to Protein Translator ===")
print("Enter a DNA sequence to translate it into protein sequence.")
print("Type 'exit' to quit the program.\n")

while True:
    dna_input = input("Enter DNA sequence: ").strip()
    if dna_input.lower() == 'exit':
        print("Exiting the program. Goodbye!")
        break
    if len(dna_input) < 3:
        print("Sequence too short to translate. Please enter at least 3 nucleotides.\n")
        continue
    protein_output = translate_dna(dna_input)
    print("Protein sequence:", protein_output)
    print("-" * 50)
