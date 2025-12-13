# Projeto Vitra - API (Grupo Fuxi 2025.2) 

Este repositório contém o código-fonte da API (Django + Postgres) do projeto Vitra.

## 🔗 Links
- **Repositório da Documentação:** [2025.2-Fuxi-Docs](https://github.com/fga-eps-mds/2025.2-Fuxi-Docs)
- **Repositório do Aplicativo Mobile:** [2025.2-Fuxi-Mobile](https://github.com/fga-eps-mds/2025.2-Fuxi-Mobile)


## 🚀 Executar projeto...

### 💻 Pré-requisitos

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clonar o repositório

```bash
git clone https://github.com/fga-eps-mds/2025.2-Fuxi-API.git

cd 2025.2-Fuxi-API
```

### 2. Configurar variáveis de ambiente

Este projeto utiliza variáveis de ambiente para configuração de ALLOWED_HOSTS para que a API aceite requisições de IPs autorizados.

🔒 **Importante:** o arquivo `.env` **não é versionado** por motivos de segurança.

#### Passo a passo:

#### Copie o arquivo de exemplo:

```bash
cp .env.example .env
```
#### Preencha as variáveis conforme seu ambiente local.

```bash
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Executar projeto com Docker Compose

```bash
docker compose up
```

A aplicação rodará localmente neste IP: http://localhost:8000 (Este é o IP que deve ser configurado nas variáveis de ambiente do frontend no repositório **2025.2-Fuxi-Mobile**)

## 🧪 Executar Testes...

### 1. Executar testes unitários e cobertura

```bash
docker compose run --rm djangoapp sh -c "coverage run manage.py test && coverage html"
```
### 2. Verificar resultados de cobertura

- Ao fim da execução dos testes e cobertura, os resultados estarão disponíveis em 
``` htmlcov/index.html ```
