import os

import numpy as np
import pandas as pd

LOCAL_DIRECTORY = "./"
PROCESSED_DIRECTORY = "../01. PRE_PROCESSING/02. output/notas/"
MEDIAS_BUCKET = './03. resources/Media_Desv_Pad_SAEP_2021(250-50).csv'


def get_local_file(file_path):
    """
    Constructs the full path of a local file.

    :param file_path: Relative file path.
    :return: Full path to the local file.
    """
    return os.path.join(LOCAL_DIRECTORY, file_path)


def read_csv_local(file_path, delimiter=';', decimal=','):
    """
    Reads a CSV file from the local directory.

    :param file_path: Path to the CSV file.
    :param delimiter: Delimiter used in the CSV file.
    :param decimal: Decimal separator used in the CSV file.
    :return: DataFrame with the CSV data.
    """
    return pd.read_csv(get_local_file(file_path), delimiter=delimiter, decimal=decimal)


def save_csv_to_local(file_path, df):
    """
    Saves a DataFrame to a CSV file in the local directory.

    :param file_path: Path to the output CSV file.
    :param df: DataFrame to save.
    """
    df.to_csv(get_local_file(file_path), index=False, encoding='utf-8-sig', sep=";", decimal=",")


def process_scores(score_file, df_final):
    """
    Processes score data, calculates SAES scores, and saves the results to a CSV file.

    :param score_file: File containing score data.
    :param df_final: Final DataFrame containing additional data.
    """
    output_name = score_file.split(".")[0]

    subject = next(disc for disc in ["LP", "MT"] if disc in score_file)

    grade = df_final["tipo_prova"][0]
    subject_columns = {'LP': [3, 7], 'MT': [5, 9]} if grade == "saes6Ano" else {'LP': [4, 8], 'MT': [6, 10]}

    col_names = ["I1", "I2", "ra_aluno", "dist_da_media", "I5"]
    df_score = pd.read_csv(PROCESSED_DIRECTORY + score_file, delim_whitespace=True, decimal='.', names=col_names)
    df_score = df_score[["ra_aluno", "dist_da_media"]]

    medias = read_csv_local(MEDIAS_BUCKET)
    col_media, col_dp = subject_columns[subject]
    ponderacao = medias.alunos_5 if grade == "saes6Ano" else medias.alunos_9
    media = np.average(medias.iloc[:, col_media], weights=ponderacao)
    dp = np.average(medias.iloc[:, col_dp], weights=ponderacao)

    df_score['dist_da_media'] = pd.to_numeric(df_score['dist_da_media'], errors='coerce')
    df_score['notaSAES'] = media + df_score['dist_da_media'].astype("float") * dp

    df_merge = df_final.drop(["id_questao", "marcacao", "disciplina"], axis=1).drop_duplicates()
    df_score = df_score.merge(df_merge, how='inner', left_on='ra_aluno', right_on='ra_aluno').drop_duplicates()

    save_csv_to_local("./02. output/" + 'Scores_' + subject + "_" + output_name + '.csv', df_score)


def main():
    """
    Main function to execute the code.
    """
    score_files = [file for file in os.listdir(PROCESSED_DIRECTORY) if '-sco.txt' in file]
    dfs = [file for file in os.listdir(PROCESSED_DIRECTORY) if 'df_final.csv' in file]

    for score_file in score_files:
        year = score_file.split("_")[1]
        for df_file in dfs:
            if year in df_file:
                df_final_path = PROCESSED_DIRECTORY + df_file
                df_final = pd.read_csv(df_final_path, delimiter=",")
                process_scores(score_file, df_final)


if __name__ == "__main__":
    main()
