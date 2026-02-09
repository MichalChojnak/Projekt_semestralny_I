# Skala Kyte-Doolittle
KD = {
    'I': 4.5, 'V': 4.2, 'L': 3.8, 'F': 2.8, 'C': 2.5,
    'M': 1.9, 'A': 1.8, 'G': -0.4, 'T': -0.7, 'S': -0.8,
    'W': -0.9, 'Y': -1.3, 'P': -1.6, 'H': -3.2, 'E': -3.5,
    'Q': -3.5, 'D': -3.5, 'N': -3.5, 'K': -3.9, 'R': -4.5
}

def hydrofobowe_regiony(sekwencja, okno=10, prog=18):
    regiony = []
    dl = len(sekwencja)
    for i in range(dl - okno + 1):
        fragment = sekwencja[i:i+okno]
        suma_hydro = sum(KD.get(aa, 0) for aa in fragment)  # aa nieznany -> 0
        if suma_hydro >= prog:
            regiony.append((i, i+okno, suma_hydro))
    return regiony

