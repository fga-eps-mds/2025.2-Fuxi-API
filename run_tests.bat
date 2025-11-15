@echo off
REM Script para executar testes unitários das views de pesquisa no Windows

echo === Executando Testes Unitarios para Research Views ===
echo.

REM Ativar ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Executar testes específicos
echo Executando testes das research views...
python manage.py test api.test_research_views -v 2

echo.
echo === Executando com Coverage ===

REM Instalar coverage se não estiver instalado
pip install coverage >nul 2>&1

REM Executar com coverage
coverage run --source="." manage.py test api.test_research_views
coverage report --include="*research_views.py"

echo.
echo Para ver relatorio HTML detalhado, execute:
echo coverage html
echo Depois abra htmlcov/index.html no navegador

pause