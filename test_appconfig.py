import os
import sys
from importlib import import_module

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    api_apps = import_module("api.apps")
    ApiConfig = getattr(api_apps, "ApiConfig")

    class TestApiConfig(ApiConfig):
        path = os.path.dirname(os.path.abspath(api_apps.__file__))

    config = TestApiConfig('api', None)
    print(" AppConfig importado com sucesso:", config.name)
    print(" Caminho do app:", config.path)

except Exception as e:
    print(" Erro ao importar AppConfig:", e)
