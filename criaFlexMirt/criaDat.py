import csv
import os


def convert_letters_to_numbers(marking):
    letter_to_number = {"A": 1, "B": 2, "C": 3, "D": 4, ".": 5, "*": 5}
    return ' '.join(str(letter_to_number[letter]) for letter in marking)


def main():
    input_file = '../combination/Marcações/Marcações.csv'
    output_folder = './output'
    os.makedirs(output_folder, exist_ok=True)

    data = {}

    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            ano = row['Ano']
            blocos = row['Blocos']
            marcacoes_lp = f"{row['Matrícula']} {convert_letters_to_numbers(row['Marcações_LP'])}"
            marcacoes_mt = f"{row['Matrícula']} {convert_letters_to_numbers(row['Marcações_MT'])}"

            key = f'{ano}_{blocos}'
            if key not in data:
                data[key] = {'LP': [], 'MT': []}

            data[key]['LP'].append(marcacoes_lp)
            data[key]['MT'].append(marcacoes_mt)

    for key, values in data.items():
        ano, blocos = key.split('_')
        for marking_type, markings in values.items():
            output_file_name = f'inp_{ano}_{blocos}_{marking_type}.dat'
            with open(os.path.join(output_folder, output_file_name), 'w') as output_file:
                for marking in markings:
                    output_file.write(f'{marking}\n')


if __name__ == '__main__':
    main()
