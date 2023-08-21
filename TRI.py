import pandas as pd
import numpy as np
from scipy.optimize import curve_fit, minimize
from openpyxl import load_workbook


def func_logistica_3PL(x, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (x - b)))


def importar_excel(arquivo):
    wb = load_workbook(arquivo)
    ws = wb.active
    dados = pd.DataFrame(ws.values)
    dados.columns = dados.iloc[0]
    dados = dados.drop(0)
    return dados


def calcular_parametros_tri(dados):
    parametros = []
    habilidades_iniciais = dados.iloc[:, 1:].mean(axis=1).values
    for coluna in dados.columns[1:]:
        respostas = dados[coluna].astype(int)
        popt, _ = curve_fit(func_logistica_3PL, habilidades_iniciais, respostas, bounds=(0, [4.0, 4.0, 1.0]),
                            maxfev=10000)
        parametros.append(popt)
    return parametros


def habilidade_aluno(respostas, parametros):
    def log_verossimilhanca(theta, respostas, parametros):
        p = np.array([func_logistica_3PL(theta, a, b, c) for a, b, c in parametros])
        return -np.sum(respostas * np.log(p) + (1 - respostas) * np.log(1 - p))

    resultado = minimize(log_verossimilhanca, 0, args=(respostas, parametros), bounds=[(-4, 4)])
    return resultado.x[0]


def transformar_escala(habilidade, min_habilidade, max_habilidade, min_nota, max_nota):
    return ((habilidade - min_habilidade) * (max_nota - min_nota) / (max_habilidade - min_habilidade)) + min_nota


def calcular_notas_alunos(dados, parametros):
    notas = []
    for _, aluno in dados.iterrows():
        nome = aluno['nome']
        respostas = np.array(aluno[1:])
        habilidade = habilidade_aluno(respostas, parametros)
        print(habilidade)
        nota_transformada = 202.6008424 + habilidade * 46.15773604
        # nota_transformada = transformar_escala(habilidade, -4, 4, 0, 100)
        notas.append((nome, nota_transformada))
    return notas


def main():
    arquivo = "Base_testes.xlsx"
    dados = importar_excel(arquivo)
    parametros = calcular_parametros_tri(dados)
    notas_alunos = calcular_notas_alunos(dados, parametros)

    print("Parâmetros do TRI (a, b, c) para cada questão:")
    for i, p in enumerate(parametros):
        print(f"Questão {i + 1}: a = {p[0]:.2f}, b = {p[1]:.2f}, c = {p[2]:.2f}")

    print("\nNotas dos alunos (habilidade estimada, escala de 0 a 100):")
    for nome, nota in notas_alunos:
        print(f"{nome}: {nota:.2f}")


if __name__ == "__main__":
    main()

'''
    a: é o parâmetro de discriminação, que mede a habilidade da questão em distinguir entre candidatos com diferentes 
    níveis de proficiência. Quanto maior o valor de a, mais discriminante é a questão.

    b: é o parâmetro de dificuldade, que indica o nível de proficiência em que a probabilidade de acerto é de 50%. 
    Ou seja, b representa o ponto em que a curva de probabilidade de acerto passa por 0,5. Quanto maior o valor de b, 
    mais difícil é a questão.

    c: é o parâmetro de acerto ao acaso, que representa a probabilidade de um candidato acertar a questão por puro 
    acaso, sem realmente possuir a habilidade ou conhecimento necessário para respondê-la corretamente. 
    Quanto menor o valor de c, menos provável é que um candidato acerte a questão por acaso. 
    O parâmetro c é equivalente ao chute em um teste de múltipla escolha, em que cada alternativa tem a mesma 
    probabilidade de ser escolhida.
'''
