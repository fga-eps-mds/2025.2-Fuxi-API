#!/bin/bash
# Script para executar testes unitários das views de pesquisa

echo "=== Executando Testes Unitários para Research Views ==="
echo ""

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Executar testes específicos
echo "Executando testes das research views..."
python manage.py test api.test_research_views -v 2

echo ""
echo "=== Executando com Coverage ==="

# Instalar coverage se não estiver instalado
pip install coverage > /dev/null 2>&1

# Executar com coverage
coverage run --source='.' manage.py test api.test_research_views
coverage report --include="*research_views.py"

echo ""
echo "Para ver relatório HTML detalhado, execute:"
echo "coverage html"
echo "Depois abra htmlcov/index.html no navegador"