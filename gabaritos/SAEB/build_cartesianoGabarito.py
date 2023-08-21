import pandas as pd
from itertools import permutations

data = pd.read_csv("grouped_ajustado.csv", delimiter=';')

result = pd.DataFrame(columns=['ID_PROVA_BRASIL', 'DISCIPLINA', 'ID_SERIE', 'BLOCO', 'GABARITO'])

unique_combinations = data[['DISCIPLINA', 'ID_SERIE']].drop_duplicates().values.tolist()

for comb in unique_combinations:
    discipline, series = comb

    filtered_data = data[(data['DISCIPLINA'] == discipline) & (data['ID_SERIE'] == series)]

    row_permutations = list(permutations(filtered_data.iterrows(), 2))

    for row_perm in row_permutations:
        idx1, row1 = row_perm[0]
        idx2, row2 = row_perm[1]
        gabarito_merged = f"KEY      {row1['GABARITO']}{row2['GABARITO']}"
        bloco_str = f"{row1['BLOCO']},{row2['BLOCO']}"

        result = result.append({
            'ID_PROVA_BRASIL': row1['ID_PROVA_BRASIL'],
            'DISCIPLINA': discipline,
            'ID_SERIE': series,
            'BLOCO': bloco_str,
            'GABARITO': gabarito_merged
        }, ignore_index=True)

for _, row in result.iterrows():
    id_prova_brasil, disciplina, id_serie, bloco, gabarito = row

    file_name = f"SAEB_{id_serie}EF_{disciplina}_{bloco}.key"

    with open(f"./gabaritos/{file_name}", 'w') as file:
        file.write(gabarito)

# Print the result
print(result)