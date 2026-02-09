# DNA to Protein Translator with Validation and Codon Length Check

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

def validate_dna(dna_seq):
    """Check for invalid letters in DNA sequence"""
    valid_nucleotides = {'A', 'G', 'C', 'T'}
    errors = []
    for i, nucleotide in enumerate(dna_seq.upper()):
        if nucleotide not in valid_nucleotides:
            errors.append((i, nucleotide))
    return errors

# =====================
# INTERACTIVE MENU
# =====================
print("=== DNA to Protein Translator ===")
print("Enter a DNA sequence to translate it into protein sequence.")
print("Only A, G, C, T are allowed.")
print("The sequence length must be a multiple of 3.")
print("Type 'exit' to quit the program.\n")

while True:
    dna_input = input("Enter DNA sequence: ").strip()
    if dna_input.lower() == 'exit':
        print("Exiting the program. Goodbye!")
        break

    # Validate DNA letters
    errors = validate_dna(dna_input)
    if errors:
        print("Error: Invalid characters found in DNA sequence!")
        for pos, char in errors:
            print(f" - Position {pos+1}: '{char}' is not valid")
        highlight = ''.join([char if char.upper() in {'A','G','C','T'} else '^' for char in dna_input])
        print("Sequence:  ", dna_input)
        print("Highlight: ", highlight)
        print("-" * 50)
        continue

    # Validate length (must be multiple of 3)
    if len(dna_input) % 3 != 0:
        print(f"Error: Sequence length is {len(dna_input)}. DNA sequence must be a multiple of 3 (codons).")
        print("-" * 50)
        continue

    # Translate sequence
    protein_output = translate_dna(dna_input)
    print("Protein sequence:", protein_output)
    print("-" * 50)
