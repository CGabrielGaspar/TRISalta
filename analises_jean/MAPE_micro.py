import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error

# Lendo os dados dos CSVs
Expected = pd.read_csv('./input/nota_oficial/extracted_data.csv')
Actual_250 = pd.read_csv('./input/nota_calculado/combined_scores(250-50).csv')
Actual_Calc = pd.read_csv('./input/nota_calculado/combined_scores(calc).csv')

# Renomeando as colunas para realizar o merge
Actual_250.rename(columns={'ra_aluno': 'ID_ALUNO'}, inplace=True)
Actual_Calc.rename(columns={'ra_aluno': 'ID_ALUNO'}, inplace=True)

# Removendo linhas na tabela B que possuem ID de aluno, mas não possuem notas
columns_to_check = ['PROFICIENCIA_MT_SAEB', 'PROFICIENCIA_LP_SAEB']
Expected.dropna(subset=columns_to_check, inplace=True)

# Definindo os pares de colunas para os quais o MAPE será calculado
columns_pairs = [
    ('PROFICIENCIA_MT_SAEB', 'notaSAES_MT'),
    ('PROFICIENCIA_LP_SAEB', 'notaSAES_LP'),
]

# Inicializando um dicionário para armazenar os resultados
mape_results = {}

# Para cada identifier único nas tabelas Actual
for identifier in Actual_250['identifier'].unique():
    # Filtre as tabelas para incluir apenas as linhas com esse identifier
    Actual_250_filtered = Actual_250[Actual_250['identifier'] == identifier]
    Actual_Calc_filtered = Actual_Calc[Actual_Calc['identifier'] == identifier]

    # Realizando o merge com base na coluna de ID de aluno
    merged_table_ab = pd.merge(Actual_250_filtered, Expected, on='ID_ALUNO')
    merged_table_bc = pd.merge(Actual_Calc_filtered, Expected, on='ID_ALUNO')

    # Calculando o MAPE para cada par de colunas na tabela A e B
    for col_pair in columns_pairs:
        col_a, col_b = col_pair
        mape = mean_absolute_percentage_error(merged_table_ab[col_a], merged_table_ab[col_b])
        mape_results[(col_pair, 'A-B', identifier)] = mape

    # Calculando o MAPE para cada par de colunas na tabela B e C
    for col_pair in columns_pairs:
        col_a, col_b = col_pair
        mape = mean_absolute_percentage_error(merged_table_bc[col_a], merged_table_bc[col_b])
        mape_results[(col_pair, 'B-C', identifier)] = mape


for key, mape in mape_results.items():
    col_pair, comparison, identifier = key
    print(f'MAPE for {col_pair[0]} and {col_pair[1]} for {comparison} and identifier {identifier}: {mape}')

results_list = [(key[0][0], key[0][1], key[1], key[2], value) for key, value in mape_results.items()]
results_df = pd.DataFrame(results_list, columns=['Column1', 'Column2', 'Comparison', 'Identifier', 'MAPE'])

# Exportando os resultados para um CSV
results_df.to_csv('mape_results.csv', index=False)