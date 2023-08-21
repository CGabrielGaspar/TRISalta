import io
import json
import os
from collections import Counter
from typing import List

import pandas as pd

from distance import pdist, squareform, hamming

BASE_DIR = "./"

def extract_nomes():
    filepath = r"C:\Users\Carlos.Gaspar\PycharmProjects\TRISalta\SAES\01. PRE_PROCESSING\01. input\data.csv"
    df = pd.read_excel(filepath, engine='openpyxl')
    unique_pairs = df[['RA', 'Aluno']].drop_duplicates()
    unique_pairs.to_csv("nome_alunos.csv", index=False)


def most_frequent(List, min_contagem, n):
    occurence_count = Counter(List)
    contador = occurence_count.most_common()
    lista_return = []
    for id_x, u in enumerate(contador):
        if u[1] >= min_contagem and id_x + 1 <= n:
            lista_return.append(u[0])
    return lista_return


def get_groupby_disciplinas(disciplinas: List[str]) -> List[str]:
    groupby_columns = ["id_rede", "id_escola", "serie", "turma", "ra_aluno"]
    return groupby_columns


def get_colantes(df_final_gabarito: pd.DataFrame) -> List[str]:
    score_threshold = 0.9
    cola_threshold = 2 / 22  # TODO: Depende do número de questões
    set_colantes = set()
    marcacao_dict = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, 'W': 5}

    df_final_gabarito.loc[:, "marcacao_int"] = df_final_gabarito.marcacao.replace(
        marcacao_dict
    )
    disciplinas = list(df_final_gabarito.disciplina.unique())
    group_by_columns = get_groupby_disciplinas(disciplinas)

    df_pivot = df_final_gabarito.pivot(
        group_by_columns, columns=["id_questao"], values=["marcacao_int"]
    )
    correct_answers = df_final_gabarito.groupby(group_by_columns)["correct"].sum()
    total_questions = df_final_gabarito.groupby(group_by_columns)["correct"].count()
    score = correct_answers / total_questions
    df_pivot["score"] = score
    group_by_columns.remove('ra_aluno')
    groups = list(df_final_gabarito.groupby(group_by_columns)["correct"].sum().index)
    for g in groups:
        df_compare = df_pivot.loc[g]
        filter_score = df_compare.score < score_threshold
        df_compare_filtered = df_compare.loc[filter_score].dropna(axis=1)
        if (len(df_compare_filtered) < 2):
            continue
        compare_values = df_compare_filtered.marcacao_int.values
        matrix = pd.DataFrame(
            squareform(pdist(compare_values, metric=hamming), len(compare_values)),
            index=df_compare_filtered.index.get_level_values("ra_aluno"),
            columns=df_compare_filtered.index.get_level_values("ra_aluno").values,
        )
        for colante_1 in matrix.index:
            set_colantes_in_matrix = set(
                matrix.loc[colante_1][matrix.loc[colante_1] < cola_threshold].index
            )
            set_colantes_in_matrix = set_colantes_in_matrix - set([colante_1])
            set_colantes = set_colantes | set_colantes_in_matrix

    return list(set_colantes)


def gera_inputs(json_content):
    objetos = json.loads(json_content)
    pasta_temp = "./02. output/"
    filepath = r"C:\Users\Carlos.Gaspar\PycharmProjects\TRISalta\SAES\01. PRE_PROCESSING\02. output\\"

    # primeiramente a parte dos gabaritos
    gabarito = pd.DataFrame.from_records(objetos["gabarito"])

    # agora, a parte das provas
    # logger.info("gerando data frame geral")
    df_raw = pd.json_normalize(
        objetos["simulados"],
        ["provas", "01. input"],
        [
            "id_escola",
            "id_rede",
            "id_serie",
            "id_turma",
            "tipo_prova",
            ["01. input", "ra_aluno"],
        ],
    )
    df_final = df_raw.copy()
    df_final.columns = [
        "id_questao",
        "marcacao",
        "disciplina",
        "id_escola",
        "id_rede",
        "serie",
        "turma",
        "tipo_prova",
        "ra_aluno",
    ]

    df_final = df_final.reset_index(drop=True).drop_duplicates(
        ['id_escola', 'id_rede', 'serie', 'turma', 'ra_aluno', 'id_questao'])
    alunos_all = list(set(df_final.ra_aluno))
    alunos_all = [t for t in alunos_all if str(t) != "nan"]

    tipo_prova = df_final.tipo_prova[0].upper()
    disciplinas = list(set(df_final.disciplina))

    df_final_gabarito = pd.merge(
        df_final, gabarito, how="left", left_on="id_questao", right_on="id_questao"
    )
    print("df_final_gabarito", df_final_gabarito)
    df_final_gabarito["correct"] = (df_final_gabarito["marcacao"] == df_final_gabarito["gabarito"]) * 1
    print("correct", df_final_gabarito)

    # dando o join nos gabaritos para descobrir qual a disciplina de cada
    gabarito_join = pd.merge(gabarito, df_final, on="id_questao", how="inner")
    gabarito_filter = gabarito_join[
        ["id_questao", "gabarito", "disciplina"]
    ].drop_duplicates()

    ##############COLA####################
    t = 3  # incerteza de questoes para cola
    alunos_out = get_colantes(df_final_gabarito)
    lista_marc_conc = list(df_final_gabarito.groupby('ra_aluno')['marcacao'].apply(lambda x: ''.join(x)).values)
    dic_marc_conc = df_final_gabarito.groupby('ra_aluno')['marcacao'].apply(lambda x: ''.join(x)).to_dict()

    # minimo de repetições para considerar um gabarito como colado
    min_cont = round(0.0008 * len(alunos_all))
    if min_cont < 5:
        min_cont = 5
    gab_moda = most_frequent(lista_marc_conc, min_cont, 2)

    # contagem de questoes da prova
    n_quest = len(df_final.id_questao.drop_duplicates())

    # verificando quais alunos marcaram o gabarito moda
    for aluno in dic_marc_conc:
        for gab in gab_moda:
            iguais = [i for i, j in zip(dic_marc_conc[aluno], gab) if i == j]
            if (n_quest - t) <= len(iguais) <= n_quest:
                alunos_out.append(aluno)

    ##############COLA####################

    # excluindo alunos colantes
    df_final = df_final[~df_final.ra_aluno.isin(alunos_out)]

    # filtra anuladas
    gabarito_filter = gabarito_filter.loc[gabarito_filter.gabarito != "X"]
    df_final = (
        df_final
        .set_index(["id_questao", "disciplina"])
        .join(
            gabarito_filter.set_index(["id_questao", "disciplina"])
            , how="inner", rsuffix="_r")
        .reset_index()
        .drop("gabarito", axis=1)
    )
    # gerando arquivo csv que contem os alunos colantes
    alunos_colantes = pd.DataFrame(data={"Alunos": alunos_out})
    # logger.info('inserindo no s3')
    save_csv_to_local(pasta_temp, "alunos_cola.csv", alunos_colantes)

    # criando o input de alunos e 01. input

    # associando a sequencia de 01. input a cada aluno para cada disciplina
    disciplina_ra_aluno = (
        df_final
        .sort_values(['ra_aluno', 'id_questao'], ascending=True)
        .groupby(['disciplina', 'ra_aluno'])['marcacao'].apply(lambda x: " ".join(x))
    )
    disciplina_ra_aluno = (disciplina_ra_aluno.str.replace('A', '0')
                           .str.replace('B', '1')
                           .str.replace('C', '2')
                           .str.replace('D', '3')
                           .str.replace('E', '4')
                           .str.replace('W', '5'))
    for disc in disciplinas:
        df_disciplina_ra = disciplina_ra_aluno.loc[disc]
        dic_al = df_disciplina_ra.to_dict()
        try:
            len_matricula = (
                df_disciplina_ra
                .reset_index()
                .ra_aluno
                .astype(str)
                .str
                .len()
                .mode()[0])
        except:
            len_matricula = "8"

        gabarito_disc = gabarito_filter[gabarito_filter["disciplina"] == disc]
        gabarito_disc_ = gabarito_disc.sort_values(by="id_questao")
        str_gabarito = ""
        for gab in gabarito_disc_.gabarito:
            str_gabarito = str_gabarito + gab
        str_gabarito = ",".join(str_gabarito)
        str_gabarito = (str_gabarito
                        .replace('A', '0')
                        .replace('B', '1')
                        .replace('C', '2')
                        .replace('D', '3')
                        .replace('E', '4')
                        .replace('W', '5'))

        input_dat = io.StringIO()
        for dic in dic_al:
            txt_input = (
                    (int(len_matricula) - len(str(dic))) * "0"
                    + str(dic)
                    + " "
                    + dic_al[dic]
            )
            input_dat.write(txt_input + "\n")
        with open(os.path.join(BASE_DIR, pasta_temp, f"inp_{tipo_prova}_{disc}.dat"), "w") as f:
            f.write(input_dat.getvalue())
        input_dat.close()

        end_bilog_in = filepath

        end_input = end_bilog_in + "inp_" + tipo_prova + "_" + disc + ".dat"
        df_disciplina_ra_2 = df_disciplina_ra.str.replace(' ', '')
        n_questoes = str(df_disciplina_ra_2.str.len().mode()[0])
        n_questoes_mais = str(int(n_questoes) + 1)
        n_alunos = str(len(dic_al))

        # achando o arquivo de key correspondente à disciplina
        bilog_arquivo = [
            ' <Project>\n',
            '   Title = "ENEM2_CH_SE";\n',
            '   Description = "45 items, 1 factor, 1 Group Calibration, \n',
            '   saving parameter "; \n',
            ' \n',
            ' <Options>\n',
            '   Mode = Calibration;\n',
            '   GOF = Extended;\n',
            '   Score= EAP;\n',
            '   SavePRM = Yes;\n',
            '   SaveSCO = Yes;\n',
            ' \n',
            ' <Groups>\n',
            '   // define your groups and group names\n',
            '   %G1%\n',
            '   File = "C:\\FlexMIRT\\Enem2\\Etapa1_Pre_FlexMIRT\\Enem2_CH_SE.dat" ;\n',
            '   Varnames = v1-v46;\n',
            '   Select = v2-v46;\n',
            '   N = 10219;\n',
            '   Ncats(v2-v46) = 6;\n',
            '   Model(v2-v46) = ThreePL; // model type, e.g., Model(v1-v10) = ThreePL;\n',
            '   Key(v2-v46) = (' + str_gabarito + ');\n',
            '   CaseID = v1;\n',
            ' \n',
            ' <Constraints>',
            '\n',
            '\n'
        ]

        # mudando as linhas necessárias no arquivo input
        bilog_arquivo[1] = '   Title = "' + tipo_prova + '_' + disc + '";\n'
        bilog_arquivo[2] = '   Description = "' + n_questoes + ' items, 1 factor, 1 Group Calibration, \n'
        bilog_arquivo[15] = '   File = "' + end_input + '" ;\n'
        bilog_arquivo[16] = '   Varnames = v1-v' + n_questoes_mais + ';\n'
        bilog_arquivo[17] = '   Select = v2-v' + n_questoes_mais + ';\n'
        bilog_arquivo[18] = '   N = ' + n_alunos + ';\n'
        bilog_arquivo[19] = '   Ncats(v2-v' + n_questoes_mais + ') = 6;\n'
        bilog_arquivo[20] = '   Model(v2-v' + n_questoes_mais + ') = ThreePL;\n'
        bilog_arquivo[21] = f'   Key(v2-v{n_questoes_mais}) = ({str_gabarito});\n'

        input_blm = io.StringIO()
        for row in bilog_arquivo:
            txt_input = row
            input_blm.write(txt_input)
        with open(os.path.join(BASE_DIR, pasta_temp, f"inp_{tipo_prova}_{disc}.flexmirt"), "w") as f:
            f.write(input_blm.getvalue())
        input_blm.close()

    save_csv_to_local(pasta_temp, "df_final.csv", df_final)

    df_tipo = pd.DataFrame(columns=["tipo_prova"])
    df_tipo = df_tipo.append({"tipo_prova": tipo_prova}, ignore_index=True)
    save_csv_to_local(pasta_temp, "tipo_prova.csv", df_tipo)

    df_disci = pd.DataFrame(columns=["disciplinas"])
    for disci in disciplinas:
        df_disci = df_disci.append({"disciplina": disci}, ignore_index=True)
    save_csv_to_local(pasta_temp, "disciplinas.csv", df_disci)


def save_csv_to_local(file_path, file_name, df):
    # return
    os.makedirs(file_path, exist_ok=True)
    file_path = os.path.join(file_path, file_name)
    df.to_csv(file_path, index=False)


if __name__ == "__main__":
    # for file in os.listdir("./01. input/"):
    #     with open("./01. input/" + file, 'r', encoding='utf-8') as f:
    #         json_content = f.read()
    #
    #     gera_inputs(json_content)
    with open("./01. input/" + "Marcações.txt", 'r', encoding='utf-8') as f:
        json_content = f.read()

        gera_inputs(json_content)
    extract_nomes()
