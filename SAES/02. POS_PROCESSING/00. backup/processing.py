import pandas as pd
import numpy as np
import logging
import os

logger = logging.getLogger()
local_directory = "./"


def pos_process():
    files = []
    processed_directory = "../01. PRE_PROCESSING/02. output/"
    for file_name in os.listdir(processed_directory):
        files.append(file_name)
    if len(files) == 0:
        return
    files_out_b = [file for file in files if '-sco.txt' in file]
    files_out = files_out_b

    for file in files_out:
        trata_saida(file)


def get_local_file(file_path):
    return os.path.join(local_directory, file_path)


def read_csv_local(file_path, delimiter=';', decimal=','):
    full_path = get_local_file(file_path)
    return pd.read_csv(full_path, delimiter=delimiter, decimal=decimal)


def save_csv_to_local(file_path, df):
    full_path = get_local_file(file_path)
    df.to_csv(full_path, index=False)


def write_json_local(file_path, df):
    full_path = get_local_file(file_path)
    df.to_json(full_path, orient="records", force_ascii=False)


def trata_saida(score):
    pasta_out = "../01. PRE_PROCESSING/02. output/"
    # importando o que eram variáveis globais
    df_final_bucket = "../01. PRE_PROCESSING/02. output/df_final.csv"
    df_final = pd.read_csv(df_final_bucket,
                           delimiter=',')

    # abrindo o arquivo de output do bilog
    f = pasta_out + score

    disciplinas = ["LP", "MT"]

    # identificando a disciplina do score
    disc_atual = ""
    for disc in disciplinas:
        if disc in score:
            disc_atual = disc

    # relacionando a disciplina com as colunas correspondente. Considera 5º ou 9º Ano
    turma = df_final["tipo_prova"][0]
    if turma == "saes6Ano":
        dic_disc = {'LP': [3, 7], 'MT': [5, 9]}
    elif turma == "saes1Serie":
        dic_disc = {'LP': [4, 8], 'MT': [6, 10]}

    # criando a tabela que recebera as informacoes relevantes desse arquivo
    col_names = ["I1", "I2", "ra_aluno", "dist_da_media", "I5"]

    df_score = pd.read_csv(f, delim_whitespace=True, decimal='.', names=col_names)
    df_score = df_score[["ra_aluno", "dist_da_media"]]

    # receber a tabela com as notas médias do ENEM
    medias_bucket = './03. resources/Media_Desv_Pad_SAEP_2021(250-50).csv'
    medias = pd.read_csv(medias_bucket,
                         delimiter=';', decimal=',')

    col_media = dic_disc[disc_atual][0]
    col_dp = dic_disc[disc_atual][1]
    # Define a coluna de ponderação com base na turma
    if turma == "saes6Ano":
        ponderacao = medias.alunos_5
    elif turma == "saes1Serie":
        ponderacao = medias.alunos_9

    media = np.average(medias.iloc[:, col_media], weights=ponderacao)
    dp = np.average(medias.iloc[:, col_dp], weights=ponderacao)

    df_score['dist_da_media'] = pd.to_numeric(df_score['dist_da_media'], errors='coerce')
    df_score['notaSAES'] = media + df_score['dist_da_media'].astype("float") * dp

    # todo: bring this guy back
    df_merge = df_final.drop(["id_questao", "marcacao", "disciplina"], axis=1)
    df_merge = df_merge.drop_duplicates()
    df_score = df_score.merge(df_merge, how='inner', left_on='ra_aluno', right_on='ra_aluno')
    df_score = df_score.drop_duplicates()

    # gerando o csv e json
    save_csv_to_local("./02. output/" + 'Scores_' + disc_atual + '.csv', df_score)


if __name__ == "__main__":
    pos_process()
