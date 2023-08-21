import openpyxl
import pandas as pd
import math
import numpy as np
import json


def set_gabarito(df):
    def extract_questao_gabarito(row):
        questao_gab = row['Questão e Gab']
        prova = row['Prova']

        if isinstance(questao_gab, str):
            # Split 'Questão e Gab' em id_questao and gabarito
            id_questao, gabarito = questao_gab.split(' - ')

            id_questao = int(id_questao)

            # TODO: Mudar calculo de index
            if "M1" in prova:
                id_questao += 10

            # Return dict com 'id_questao' e 'gabarito'
            return {'id_questao': id_questao, 'gabarito': gabarito}
        else:
            return

    result_list = [extract_questao_gabarito(row) for _, row in df.iterrows() if isinstance(row['Questão e Gab'], str)]
    # Remove duplicates and None values da lista
    unique_result_list = []
    for item in result_list:
        if item is not None and item not in unique_result_list:
            unique_result_list.append(item)
    return unique_result_list


def group_marcacoes(df):
    grouped = df.groupby(['Marca', 'Escola', 'Série', 'Turma', 'Aluno', 'Matrícula']).agg(
        {'Marcação': ''.join}).reset_index()
    return grouped


simulados = {'simulados': [], 'gabarito': []}  # simulados(local)
tipo_prova = 'saes'

path_in = "../01. input"
file_in = "data.xlsx"
workbook = pd.read_excel(f"{path_in}/{file_in}")

redes = list(set(workbook.Marca))
escolas = list(set(workbook.Escola))
turmas = list(set(workbook.Turma))
series = list(set(workbook.Série))

simulados['gabarito'] = set_gabarito(workbook)

dados_alunos = group_marcacoes(workbook)

codes = []
pos_cod = {}
pos = -1

for i in range(0, len(dados_alunos)):
    marca = dados_alunos.Marca[i]
    id_marca = redes.index(marca)
    escola = dados_alunos.Escola[i]
    id_escola = escolas.index(escola)
    turma = dados_alunos.Turma[i]
    id_turma = turmas.index(turma)
    serie = dados_alunos.Série[i]
    id_serie = series.index(serie)
    cod = str(id_marca) + str(id_escola) + str(tipo_prova) + str(id_turma) + str(id_serie)

    if cod in codes:
        pos_add = pos_cod[cod]
        try:
            ra_aluno = str(int(dados_alunos.Matrícula[i]))
        except:
            print('erro em i: ' + str(i))

        prova = {'ra_aluno': ra_aluno}
        marcs = dados_alunos.Marcação[i]
        marcacoes = []
        for idx, m in enumerate(marcs):
            if idx + 1 in range(1, 10):
                disciplina = 'LP'
                soma_id = 0
            else:
                disciplina = 'MT'
                soma_id = 10
            marcacao = {'id_questao': idx + 1 + soma_id, 'marcacao': m, 'disciplina': disciplina}
            marcacoes.append(marcacao)
        prova['01. input'] = marcacoes

        simulados['simulados'][pos_add]['provas'].append(prova)

    else:
        local_dic = {'id_rede': id_marca, 'id_escola': id_escola, 'tipo_prova': tipo_prova, 'id_turma': id_turma,
                     'id_serie': id_serie, 'provas': []}

        ra_aluno = dados_alunos.Matrícula[i]
        prova = {'ra_aluno': ra_aluno}
        marcs = dados_alunos.Marcação[i]
        marcacoes = []
        for idx, m in enumerate(marcs):
            if idx + 1 in range(1, 10):
                disciplina = 'LP'
                soma_id = 0
            else:
                disciplina = 'MT'
                soma_id = 10
            marcacao = {'id_questao': idx + 1 + soma_id, 'marcacao': m, 'disciplina': disciplina}
            marcacoes.append(marcacao)
        prova['01. input'] = marcacoes

        local_dic['provas'].append(prova)
        simulados['simulados'].append(local_dic)
        codes.append(cod)
        pos = pos + 1
        pos_cod[cod] = pos


def convert(o):
    if isinstance(o, np.int64): return int(o)
    raise TypeError


json_string = json.dumps(simulados, default=convert)

with open('../../01. PRE_PROCESSING/01. input/Marcações.txt', 'w+', encoding='utf-8') as f_txt:
    f_txt.write(json_string)