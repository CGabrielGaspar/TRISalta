import os
import gzip

# Folder containing JSON files
json_folder = './Test'

with gzip.open(f'{json_folder}/compressed.gz', 'wb') as gz_file:
    for filename in os.listdir(json_folder):
        if filename.endswith('.json'):
            with open(os.path.join(json_folder, filename), 'rb') as json_file:
                gz_file.write(json_file.read())