import json

import pandas as pd


def process_dataframes(df1, df2, avaliados_params):
    """
    Function to process the dataframes as per the given logic.
    :param df1: First dataframe
    :param df2: Second dataframe
    :param avaliados_params: A dictionary with required counts for each NomeSerie value
    """
    # Replace all blank cells in the "Resposta" column with 'W'
    df1['Resposta'] = df1['Resposta'].fillna('W')

    # Initialize an empty list to collect new rows and data for checks
    new_rows = []
    check_data = []
    invalid_series_data = []
    invalid_nomeprova_data = []

    # Check if "SAES" is in the "NomeProva" column and separate invalid entries
    invalid_nomeprova_data = df1[~df1['NomeProva'].str.contains('saes', case=False, regex=True)]
    df1 = df1[df1['NomeProva'].str.contains('saes', case=False, regex=True)]

    # Group df1 by RA and NomeSerie, and for each group
    # check the number of rows. If it's less than the required
    # count, add the missing rows with Resposta = 'W'
    for (RA, NomeSerie), group in df1.groupby(["RA", "NomeSerie"]):
        # Determine the required count for this group
        for prefix, params in avaliados_params.items():
            if NomeSerie.startswith(prefix):
                required_count = params["num_questions"] * 2
                break
        else:
            # Add this group's RA, NomeSerie, NomeTurma, NomePessoa to invalid_series_data
            invalid_series_data.append({
                "RA": RA,
                "NomeSerie": NomeSerie,
                "NomeTurma": group['NomeTurma'].iloc[0],
                "NomePessoa": group['NomePessoa'].iloc[0],
                "Count": len(group)
            })
            continue  # If no matching prefix was found, skip this group

        existing_values = group['Questao'].unique()

        for i in range(1, required_count + 1):
            if i not in existing_values:
                # Create a new row, copying all column values from the first row of the group
                new_row = group.iloc[0].copy()
                new_row['Questao'] = i  # Set the 'Questao' value to the missing value
                new_row['Resposta'] = 'W'  # Set 'Resposta' to 'W'
                new_rows.append(new_row)

                # Add data for the check
                check_data.append({"RA": RA, "Questao": i})

    # Continue with the rest of your code...

    # Append all new rows to df1
    df1 = df1.append(new_rows, ignore_index=True)

    # Write the check data to a CSV file
    check_df = pd.DataFrame(check_data)
    check_df.to_csv('./02. output/check_added_rows.csv', index=False, encoding='utf-8-sig')

    # Write the invalid series data to a CSV file
    invalid_series_df = pd.DataFrame(invalid_series_data)
    invalid_series_df.to_csv('./02. output/check_invalid_series.csv', index=False, encoding='utf-8-sig')

    # Write the invalid NomeProva data to a CSV file
    invalid_nomeprova_data.to_csv('./02. output/check_invalid_nomeprova.csv', index=False, encoding='utf-8-sig')

    # Filter out rows where NomeSerie does not start with "1ª" or "6º"
    df1 = df1[df1['NomeSerie'].str.startswith(("1ª", "6º"))]

    # Initialize an empty DataFrame for the merged data
    merged_df = pd.DataFrame()

    # For each unique value in the 'NomeSerie' column, extract the corresponding part of df1
    for serie in df1['NomeSerie'].unique():
        temp_df1 = df1[df1['NomeSerie'] == serie]
        column = '6Ano' if '6º' in serie else '1Serie'
        temp_df2 = df2[['Questao', column]].copy()

        # Rename the second column of temp_df2 to 'gabarito' for the merge
        temp_df2 = temp_df2.rename(columns={column: 'gabarito'})

        merged = pd.merge(temp_df1, temp_df2, on='Questao', how='left')
        merged_df = pd.concat([merged_df, merged])

    # Convert the 'Questao' column to int, dropping any remaining missing values
    merged_df = merged_df.dropna(subset=['Questao'])
    merged_df['Questao'] = merged_df['Questao'].astype(int)

    # Create the "Questão e Gab" column
    merged_df['Questão e Gab'] = merged_df['Questao'].astype(str) + " - " + merged_df['gabarito']

    # Drop the 'gabarito' column
    merged_df = merged_df.drop(columns='gabarito')

    # Add a new column "Tag", which is determined by the "NomeSerie"
    merged_df['Tag'] = merged_df['NomeSerie'].apply(lambda x: '6Ano' if '6º' in x else '1Serie')

    # Rename the columns as per your request
    merged_df = merged_df.rename(columns={
        'NomeEscola': 'Escola',
        'NomeSerie': 'Série',
        'NomeTurma': 'Turma',
        'NomePessoa': 'Aluno',
        'Resposta': 'Marcação'
    })

    merged_df = merged_df.sort_values(
        by=['RA', 'Marca', 'Escola', 'Série', 'Turma', 'NomeProva', 'Questao'])

    # No resultado abaixo, eu estou procurando e removendo duplicata em RA', 'Marca', 'Escola', 'Série', 'Turma',
    # 'NomeProva', 'Questao'. Se todas essas forem iguais, eu estou removendo. A ideia é manter uma linha pra cada aluno
    # pra cada questão.
    duplicated_df = merged_df[
        merged_df.duplicated(subset=['RA', 'Marca', 'Escola', 'Série', 'Turma', 'NomeProva', 'Questao'], keep=False)]
    duplicated_df.to_csv('./02. output/check_duplicates.csv', index=False, encoding='utf-8-sig')

    merged_df = merged_df.drop_duplicates(subset=['RA', 'Marca', 'Escola', 'Série', 'Turma', 'NomeProva', 'Questao'])

    # Save the dataframe back into 'Result1.csv'
    merged_df.to_csv('./02. output/data.csv', index=False, encoding='utf-8-sig')


def set_gabarito(df, num_questions):
    '''
    Função para extrair o gabarito de um dataframe.

    :param df: DataFrame com as informações das questões e gabaritos.
    :return list: Lista de dicionários com informações do gabarito (id_questao e gabarito).
    '''

    # Função interna para extrair informações de questão e gabarito de uma linha do dataframe
    def extract_questao_gabarito(row):
        questao_gab = row['Questão e Gab']
        prova = row['Prova']

        # Verifica se questao_gab é uma string e extrai o id da questão e o gabarito
        if isinstance(questao_gab, str):
            id_questao, gabarito = questao_gab.split(' - ')
            id_questao = int(id_questao) + num_questions if "M1" in prova else int(id_questao)
            return {'id_questao': id_questao, 'gabarito': gabarito}

    # Cria uma lista com as informações extraídas e remove duplicatas e valores None
    result_list = [extract_questao_gabarito(row) for _, row in df.iterrows() if isinstance(row['Questão e Gab'], str)]
    return list({json.dumps(item): item for item in result_list if item is not None}.values())


def group_marcacoes(df):
    '''
    Função para agrupar as marcações de cada aluno.

    :param df: DataFrame com as informações dos alunos e suas marcações.
    :return df: DataFrame com as marcações agrupadas por aluno.
    '''
    return df.groupby(['Marca', 'Escola', 'Série', 'Turma', 'Aluno', 'RA', 'Questão e Gab']).agg(
        {'Marcação': ''.join}).reset_index()


def process_data(df):
    '''
    Função para processar os dados do DataFrame e criar a estrutura final de simulados.

    :param df: DataFrame com as informações das questões, gabaritos e marcações dos alunos.
    :return dict: Dicionário com a estrutura final de simulados e gabaritos.
    '''
    simulados = {'simulados': [], 'gabarito': set_gabarito(df, avaliados_params[avaliados]["num_questions"])}
    data_dict = {}

    # Itera sobre as linhas agrupadas do dataframe
    for _, row in group_marcacoes(df).iterrows():
        cod = "".join(str(e.index(item)) for e, item in
                      zip([redes, escolas, turmas, series], row[['Marca', 'Escola', 'Turma', 'Série']])) + tipo_prova

        # Verifica se o código não está no dicionário e cria a estrutura necessária
        if cod not in data_dict:
            data_dict[cod] = {'id_rede': row['Marca'], 'id_escola': row['Escola'],
                              'tipo_prova': tipo_prova,
                              'id_turma': row['Turma'], 'id_serie': row['Série'],
                              'provas': []}

        # Cria a lista de marcações. Isso precisa ser alterado dependendo do número de questões
        marcacoes = [
            {'id_questao': int(qg.split(' - ')[0]), 'marcacao': m,
             'disciplina': 'LP' if int(qg.split(' - ')[0]) <= avaliados_params[avaliados]["num_questions"] else 'MT'}
            for idx, (qg, m) in enumerate(zip(row['Questão e Gab'].split(','), row['Marcação']))]
        data_dict[cod]['provas'].append({'ra_aluno': str(row['RA']), '01. input': marcacoes})
    simulados['simulados'] = list(data_dict.values())
    return simulados


path_in = "01. input"
file_in = "data.xlsx"
workbook = pd.read_excel(f"{path_in}/{file_in}")

# Cria listas únicas para redes, escolas, turmas e séries
redes = list(set(workbook.Marca))
escolas = list(set(workbook.Escola))
turmas = list(set(workbook.Turma))
series = list(set(workbook.Série))

avaliados_params = {
    "6Ano": {"num_questions": 22},  # Número de questões por disciplina (22)
    "1Serie": {"num_questions": 26}  # Número de questões por disciplina (26)
}

avaliados = "1Serie"
tipo_prova = f"saes{avaliados}"

result = process_data(workbook)

with open('../01. PRE_PROCESSING/01. input/Marcações.txt', 'w+', encoding='utf-8') as f_txt:
    f_txt.write(
        json.dumps(result, default=lambda o: int(o) if isinstance(o, pd.Int64Dtype) else str(o), ensure_ascii=False))
