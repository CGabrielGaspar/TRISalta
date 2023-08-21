import pandas as pd

# Read the CSV file
data = pd.read_csv("TS_ITEM.csv", delimiter=';')

# Replace "A/B" with "A" in the "GABARITO" column
data['GABARITO'] = data['GABARITO'].replace("A/B", "A")

# Sort the data based on the "POSICAO" column
data.sort_values(by=['ID_PROVA_BRASIL', 'DISCIPLINA', 'ID_SERIE', 'BLOCO', 'POSICAO'], inplace=True)

# Group by the specified columns and concatenate the "GABARITO" column
grouped_data = data.groupby(['ID_PROVA_BRASIL', 'DISCIPLINA', 'ID_SERIE', 'BLOCO'])['GABARITO'].apply(''.join).reset_index()

# Export the grouped data to a CSV file
grouped_data.to_csv("grouped_data.csv", index=False, sep=';')

# Precisa ajustar depois!!!