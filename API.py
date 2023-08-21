import os

import requests
import dotenv


def api_key():
    dotenv.load_dotenv()
    api_url = os.getenv("URL")
    api_key = os.getenv("KEY")
    return api_url, api_key


def enviar_arquivo_para_api(arquivo_gz: str, url, key):
    # Configurações da API
    base_url = url
    api_key = key
    headers = {"x-api-key": api_key}

    # Abre o arquivo .gz
    with open(arquivo_gz, "rb") as f:
        file_data = f.read()

    # Envia o arquivo para a API usando um POST
    response = requests.post(base_url, headers=headers, data=file_data)
    return response


# Caminho do arquivo .gz a ser enviado
arquivo_gz = "./criaJson/MarcacoesD1.gz"

url, key = api_key()

# Chama a função para enviar o arquivo
response = enviar_arquivo_para_api(arquivo_gz, url, key)

# Imprime a resposta da API
print(response.status_code)
print(response.text)
