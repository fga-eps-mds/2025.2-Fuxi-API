# Configuração para testes com coverage
# Instale as dependências: pip install coverage

# Para executar os testes:
# python manage.py test

# Para executar apenas os testes das views de pesquisa:
# python manage.py test api.test_research_views

# Para executar os testes originais:
# python manage.py test api.tests

# Para executar com cobertura:
# coverage run --source='.' manage.py test api.test_research_views
# coverage report
# coverage html  # Gera relatório HTML

# Para ver cobertura específica do arquivo research_views.py:
# coverage report --include="*research_views.py"

# Exemplo de comando completo:
# coverage run --source='.' manage.py test api.test_research_views && coverage report --include="*research_views.py"