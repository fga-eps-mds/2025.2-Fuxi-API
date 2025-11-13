import os
import sys
from importlib import import_module

# Garante que o diretório atual está no sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Importa a classe normalmente
    api_apps = import_module("api.apps")
    ApiConfig = getattr(api_apps, "ApiConfig")

    # Cria uma subclasse temporária com o 'path' definido (sem alterar o código original)
    class TestApiConfig(ApiConfig):
        path = os.path.dirname(os.path.abspath(api_apps.__file__))

    config = TestApiConfig('api', None)
    print(" AppConfig importado com sucesso:", config.name)
    print(" Caminho do app:", config.path)

except Exception as e:
    print(" Erro ao importar AppConfig:", e)
