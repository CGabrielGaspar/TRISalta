import csv
from collections import defaultdict
import chardet

gabaritos = ["./GabaritoD1.csv", "./GabaritoD2.csv"]

for gabarito in gabaritos:
    with open(gabarito, 'rb') as csvfile:
        result = chardet.detect(csvfile.read())
    file_encoding = result['encoding']

    with open(gabarito, encoding=file_encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)

        avaliacoes = defaultdict(lambda: defaultdict(dict))

        # Extract the relevant fields
        for row in reader:
            avaliacao = row[3]
            componente = row[10]
            questao = row[13]
            resposta = row[14].strip()  # Remove

            # Determine the file name based on the 'Nome do Componente' column
            if "Linguagens" in componente:
                category_suffix = "_LP"
            elif "Humanas" in componente:
                category_suffix = "_CH"
            elif "Matemática" in componente:
                category_suffix = "_MT"
            elif "Natureza" in componente:
                category_suffix = "_CN"
            else:
                continue

            if questao not in avaliacoes[category_suffix]:
                avaliacoes[category_suffix][questao] = resposta

    # Write the extracted data to .txt files
    for category_suffix, questoes_respostas in avaliacoes.items():
        filename = f"./inp_enem{category_suffix}.key"
        with open(filename, 'w', encoding='utf-8') as txtfile:
            content = f"KEY      {''.join(questoes_respostas.values())}"
            txtfile.write(content)

'''
Esse código cria as Keys, necessárias os proximos passos do TRI
'''