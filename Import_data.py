import requests

def fetch_uniprot_sequence(uniprot_id: str) -> str:
    """
    Pobiera sekwencję aminokwasową z UniProt na podstawie ID.

    :param uniprot_id: np. "P69905"
    :return: sekwencja aminokwasowa jako string
    :raises: Exception jeśli nie uda się pobrać danych
    """

    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Błąd pobierania danych z UniProt dla ID {uniprot_id}")

    fasta_data = response.text

    # Usuwamy linię nagłówkową FASTA (zaczyna się od ">")
    lines = fasta_data.split("\n")
    sequence = "".join(line.strip() for line in lines if not line.startswith(">"))

    return sequence


