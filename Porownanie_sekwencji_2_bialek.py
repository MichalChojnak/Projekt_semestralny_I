from Bio import pairwise2
from Bio.pairwise2 import format_alignment

# Sekwencje
seq1 = "MKTFFVLLLAGTAVVAAAGGAGGAGGAASTTLLVAG"
seq2 = "MKTVFVLLLAGTAVVAAAGGAGGAGGAASTTLLVVG"

# Lokalne dopasowanie
alignments = pairwise2.align.localxx(seq1, seq2)
aligned_seq1, aligned_seq2, score, start, end = alignments[0]

# Grupy aminokwasów
hydrofobowe = "AVILMFYW"
polarne = "STNQ"
zasadowe = "KRH"
kwasowe = "DE"
specjalne = "CGP"

def grupa(aa):
    if aa in hydrofobowe: return "hydrofobowe"
    if aa in polarne: return "polarne"
    if aa in zasadowe: return "zasadowe"
    if aa in kwasowe: return "kwasowe"
    if aa in specjalne: return "specjalne"
    return "inne"

# Kolory ANSI
RED = "\033[91m"
YELLOW = "\033[93m"
END = "\033[0m"

# Wyświetlenie z kolorami
colored_alignment = ""
for a, b in zip(aligned_seq1, aligned_seq2):
    if a == b:
        colored_alignment += RED + a + END
    elif grupa(a) == grupa(b):
        colored_alignment += YELLOW + a + END
    else:
        colored_alignment += a

print("Lokalne dopasowanie z kolorami:")
print(colored_alignment)
