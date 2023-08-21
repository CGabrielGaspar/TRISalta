import pandas as pd

table_b = pd.read_csv('./input/nota_oficial/extracted_data.csv')
table_a = pd.read_csv('./input/nota_calculado/combined_scores(Colantes-calc).csv')

merged_table = table_a.merge(table_b, left_on='ra_aluno', right_on='ID_ALUNO')


def format_percentage(value):
    return f"{value:.2f}%"


# Colunas correspondentes
columns_pairs = [
    ('PROFICIENCIA_MT_SAEB', 'notaSAES_MT'),
    ('PROFICIENCIA_LP_SAEB', 'notaSAES_LP')
]


# Função para calcular o erro absoluto percentual
def calculate_absolute_percentage_error(actual, predicted):
    return (abs(actual - predicted) / abs(actual)) * 100


# Calcular o erro absoluto percentual para cada par de colunas e adicionar ao DataFrame
for col_a, col_b in columns_pairs:
    error_column = f'ERROR_{col_a}_{col_b}'
    merged_table[error_column] = calculate_absolute_percentage_error(merged_table[col_a], merged_table[col_b])

# Calcular o MAPE absoluto
absolute_mape = {}
for col_a, col_b in columns_pairs:
    error_column = f'ERROR_{col_a}_{col_b}'
    absolute_mape[f'MAPE_{col_a}_{col_b}'] = merged_table[error_column].mean()

# Agrupar o DataFrame pela coluna 'identifier'
grouped_table = merged_table.groupby('identifier').mean()

# Selecionar apenas as colunas de erro percentual no DataFrame agrupado
grouped_mape = grouped_table[[f'ERROR_{col_a}_{col_b}' for col_a, col_b in columns_pairs]]

# Converter o dicionário de resultados do MAPE absoluto em um DataFrame
absolute_mape_df = pd.DataFrame([absolute_mape])

# Renomear o índice do DataFrame do MAPE absoluto
absolute_mape_df.index = ['absolute']

# Concatenar o DataFrame do MAPE absoluto com o DataFrame do MAPE agrupado
final_mape_results = pd.concat([absolute_mape_df, grouped_mape])
final_mape_results[[f'ERROR_{col_a}_{col_b}' for col_a, col_b in columns_pairs]] = final_mape_results[
    [f'ERROR_{col_a}_{col_b}' for col_a, col_b in columns_pairs]].applymap(format_percentage)

# Resetar o índice do DataFrame final
final_mape_results.reset_index(inplace=True)

# Renomear a coluna de índice para 'identifier'
final_mape_results.rename(columns={'index': 'identifier'}, inplace=True)

# Salvar o DataFrame como arquivo CSV
final_mape_results.to_csv('grouped_mape_results.csv', index=False)
