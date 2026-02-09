from Bio import pairwise2
from Bio.pairwise2 import format_alignment

# Przykładowe sekwencje
seq1 = "MKTFFVLLLAGTAVVAAAGGAGGAGGAASTTLLVAG"
seq2 = "VVLLLAGTAVVAAAGGAGG"

# Lokalne dopasowanie (Smith-Waterman)
alignments = pairwise2.align.localxx(seq1, seq2)

# Wybieramy najlepsze dopasowanie
best_alignment = alignments[0]
aligned_seq1, aligned_seq2, score, start, end = best_alignment

print("Najlepsze lokalne dopasowanie:")
print(format_alignment(*best_alignment))

# Obliczamy procent podobieństwa w dopasowanym fragmencie
matches = sum(a == b for a, b in zip(aligned_seq1, aligned_seq2))
identity = matches / len(aligned_seq1) * 100
print(f"Procent identycznych pozycji w dopasowaniu lokalnym: {identity:.2f}%")
