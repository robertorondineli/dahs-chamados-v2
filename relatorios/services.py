import requests
import json

class DeskAPI:
    BASE_URL = 'https://api.desk.ms'
    AUTH_KEY = '7d814df2751a4c08a2663ceba404e490216604ce'
    PUBLIC_KEY = 'fbebcfe8e24f830965d9a21900ba6481c642f830'

    def __init__(self):
        self.token = None

    def autenticar(self):
        try:
            headers = {
                'Authorization': self.AUTH_KEY,
                'Content-Type': 'application/json'
            }
            data = {'PublicKey': self.PUBLIC_KEY}
            
            response = requests.post(
                f'{self.BASE_URL}/Login/autenticar',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                # A API retorna o token como string entre aspas
                self.token = response.text.strip('"')
                return True
            return False
        except Exception as e:
            print(f"Erro na autenticação: {str(e)}")
            return False

    def obter_relatorio(self, chave):
        try:
            if not self.token:
                if not self.autenticar():
                    return None

            headers = {
                'Authorization': self.token,  # Removido o 'Bearer ' pois parece não ser necessário
                'Content-Type': 'application/json'
            }
            data = {
                'Chave': chave,
                'Total': '1000'
            }

            print(f"Headers do relatório: {headers}")  # Debug
            print(f"Data do relatório: {data}")  # Debug

            response = requests.post(
                f'{self.BASE_URL}/Relatorios/imprimir',
                headers=headers,
                json=data
            )

            print(f"Status Code Relatório: {response.status_code}")
            print(f"Response Text Relatório: {response.text}")

            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print("Erro ao decodificar JSON do relatório")
                    return None
            return None
        except Exception as e:
            print(f"Erro ao obter relatório: {str(e)}")
            return None 