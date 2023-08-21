import pandas as pd
import json


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
    return df.groupby(['Marca', 'Escola', 'Série', 'Turma', 'Aluno', 'RA']).agg(
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
            {'id_questao': idx + 1 + (0 if idx < avaliados_params[avaliados]["num_questions"] - 1 else 0),
             'marcacao': m, 'disciplina': 'LP' if idx < avaliados_params[avaliados]["num_questions"] else 'MT'}
            for idx, m in enumerate(row['Marcação'])]
        data_dict[cod]['provas'].append({'ra_aluno': str(int(row['RA'])), '01. input': marcacoes})

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
