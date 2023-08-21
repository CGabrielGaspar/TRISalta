import os


def combine_files(lp_path, mt_path):
    with open(lp_path, 'r') as lp_file, open(mt_path, 'r') as mt_file:
        lp_content = lp_file.read()
        mt_content = mt_file.read()

    combined_content = lp_content + mt_content[9:]

    return combined_content


def main():
    input_folder = 'input'
    output_folder = 'output'
    os.makedirs(output_folder, exist_ok=True)

    lp_files = [f for f in os.listdir(input_folder) if f.startswith('SAEB_5EF_LP_')]
    mt_files = [f for f in os.listdir(input_folder) if f.startswith('SAEB_5EF_MT_')]

    for lp_file in lp_files:
        number_pair = lp_file.split('_')[-1].split('.')[0]
        mt_file = f'SAEB_5EF_MT_{number_pair}.key'
        print(mt_file)
        if mt_file in mt_files:
            combined_content = combine_files(os.path.join(input_folder, lp_file),
                                             os.path.join(input_folder, mt_file))

            output_file_name = f'SAEB_5EF_{number_pair}.key'
            with open(os.path.join(output_folder, output_file_name), 'w') as output_file:
                output_file.write(combined_content)


if __name__ == '__main__':
    main()