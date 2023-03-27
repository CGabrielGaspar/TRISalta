import numpy as np
from scipy.optimize import minimize


def log_likelihood_student_2pl(params, ability, response):
    if len(params) != 3:
        return -np.inf
    difficulty, discrimination, guessing = params
    theta = ability
    probabilities = guessing + (1 - guessing) * 1 / (1 + np.exp(-discrimination * (theta - difficulty)))
    if len(probabilities.shape) > 1:
        probabilities = probabilities.squeeze()  # Remove dimensão desnecessária
    if probabilities.shape[0] != response.shape[0]:
        probabilities = probabilities.T
    log_likelihoods = response * np.log(probabilities) + (1 - response) * np.log(1 - probabilities)
    return np.sum(log_likelihoods)


def estimate_2pl_parameters(response_matrix):
    n_items = response_matrix.shape[0]
    item_parameters = np.zeros((n_items, 3))
    for i in range(n_items):
        result = minimize(lambda x: -log_likelihood_student_2pl(
            np.concatenate((item_parameters[:i], np.atleast_2d(x), item_parameters[i + 1:])), 0, response_matrix[i]),
                          [1, 0, 0.5])
        item_parameters[i] = result.x
    return item_parameters


def calculate_item_probabilities(item_parameters):
    a = item_parameters[:, 0]
    b = item_parameters[:, 1]
    probabilities = lambda theta: 1 / (1 + np.exp(-a * (theta - b)))
    return probabilities


def calculate_student_probabilities(item_parameters, response_matrix):
    n_students = response_matrix.shape[1]
    item_probabilities = calculate_item_probabilities(item_parameters)
    probabilities = np.zeros((n_students, item_parameters.shape[0]))
    for i in range(n_students):
        theta = estimate_student_ability(item_parameters, response_matrix[:, i])
        probabilities[i] = item_probabilities(theta)
    return probabilities


def estimate_student_ability(item_parameters, responses):
    result = minimize(lambda theta: -log_likelihood_student_2pl(item_parameters, theta, responses), 0)
    return result.x[0]


def calculate_student_scores(item_parameters, response_matrix):
    probabilities = calculate_student_probabilities(item_parameters, response_matrix)
    score = np.sum(probabilities, axis=1)
    return score


response_matrix = np.array([
    [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
    [0, 0, 0, 1, 1, 0, 0, 0, 1, 1],
    [0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
    [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
    [1, 1, 1, 1, 0, 0, 0, 1, 1, 1],
    [1, 1, 0, 0, 0, 1, 1, 0, 0, 1],
    [1, 1, 0, 0, 0, 1, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 1, 1],
    [0, 0, 0, 1, 1, 0, 0, 0, 1, 1],
    [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
    [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 0, 0, 1, 1, 0, 0, 1]])

# Estimando os parâmetros dos itens
item_parameters = estimate_2pl_parameters(response_matrix.T)

# Calculando as probabilidades de acerto em cada questão para cada aluno
probabilities = calculate_student_probabilities(item_parameters, response_matrix)

# Estimando as habilidades dos alunos
student_abilities = np.zeros((response_matrix.shape[1],))
for i in range(response_matrix.shape[1]):
    student_abilities[i] = estimate_student_ability(item_parameters, response_matrix[:, i])

# Calculando as notas dos alunos
scores = calculate_student_scores(item_parameters, response_matrix)

# Imprimindo os resultados
print("Parâmetros dos itens:")
print(item_parameters)
print("\nProbabilidades de acerto em cada questão para cada aluno:")
print(probabilities)
print("\nHabilidades dos alunos:")
print(student_abilities)
print("\nNotas dos alunos:")
print(scores)
