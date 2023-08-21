import os
import csv


def convert_key_to_numbers(key_string):
    letter_to_number = {"A": 1, "B": 2, "C": 3, "D": 4, "X": 0}
    return ','.join(str(letter_to_number[letter]) for letter in key_string if letter in letter_to_number)


def count_students(dat_file):
    with open(dat_file, 'r') as file:
        return len(file.readlines())


def build_flex():
    dat_folder = './output'
    key_folder = '../gabaritos/SAEB/gabaritos/input'
    output_folder = './output'
    os.makedirs(output_folder, exist_ok=True)

    dat_files = [f for f in os.listdir(dat_folder) if f.endswith('.dat')]

    for dat_file in dat_files:
        file_name = dat_file[:-4]  # Remove the '.dat' extension
        ano, blocos, lp_or_mt = file_name.split('_')[1:]
        key_file = f'SAEB_{ano}_{lp_or_mt}_{blocos}.key'
        key_file_path = os.path.join(key_folder, key_file)

        with open(key_file_path, 'r') as kf:
            key_content = kf.read().strip()
            n_questions = len(key_content[9:])
            gabarito = convert_key_to_numbers(key_content[9:])

        total_students = count_students(os.path.join(dat_folder, dat_file))

        flexmirt_content = f'''
    <Project>
       Title = "{file_name}";
       Description = "{n_questions} items, 1 factor, 1 Group Calibration,
       saving parameter ";

    <Options>
       Mode = Calibration;
       GOF = Extended;
       Score= EAP;
       SavePRM = Yes;
       SaveSCO = Yes;

    <Groups>
       // define your groups and group names
       %G1%
       File = "D:\\Users\\carlos.gaspar\\Desktop\\input\\{dat_file}";
       Varnames = v1-v{n_questions + 1};
       Select = v2-v{n_questions + 1};
       N = {total_students};
       Ncats(v2-v{n_questions + 1}) = 6;
       Model(v2-v{n_questions + 1}) = ThreePL;
       Key(v2-v{n_questions + 1}) = ({gabarito});
       CaseID = v1;

    <Constraints>
    '''

        output_file_name = f'{file_name}.flexmirt'
        with open(os.path.join(output_folder, output_file_name), 'w') as output_file:
            output_file.write(flexmirt_content.strip())


def build_df_final():
    input_file = '../combination/Marcações/Marcações.csv'
    output_folder = './outputFinalDF'

    # Create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(input_file, 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f, delimiter=';')

        # Create output file
        with open(os.path.join(output_folder, 'df_final.csv'), 'w', newline='') as output_file:
            fieldnames = ['id_questao', 'disciplina', 'marcacao', 'blocos', 'Ano', 'ra_aluno', 'tipo_prova']
            writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()

            # Process input data
            for row in reader:
                ra_aluno = row['Matrícula']
                Ano = row['Ano']
                blocos = str(row['Blocos']).replace(",", ".")
                Marcacoes_LP = row['Marcações_LP']
                Marcacoes_MT = row['Marcações_MT']

                # Process Marcações_LP
                for idx, marcacao in enumerate(Marcacoes_LP, start=1):
                    if marcacao != '.':
                        writer.writerow({
                            'id_questao': idx,
                            'disciplina': 'LP',
                            'marcacao': marcacao,
                            'blocos': blocos,
                            'Ano': Ano,
                            'ra_aluno': ra_aluno,
                            'tipo_prova': 'saes6Ano'
                        })

                # Process Marcações_MT
                for idx, marcacao in enumerate(Marcacoes_MT, start=1):
                    if marcacao != '.':
                        writer.writerow({
                            'id_questao': idx,
                            'disciplina': 'MT',
                            'marcacao': marcacao,
                            'blocos': blocos,
                            'Ano': Ano,
                            'ra_aluno': ra_aluno,
                            'tipo_prova': 'saes6Ano'
                        })


def main():
    build_flex()
    build_df_final()


if __name__ == '__main__':
    main()
