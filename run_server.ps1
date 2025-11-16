# Navega para o diretório do backend
Set-Location -Path "packages/backend"

# Ativa o ambiente virtual
.\venv\Scripts\Activate.ps1

# Adiciona a pasta src ao PYTHONPATH
$env:PYTHONPATH = ".\src"

# Executa o uvicorn no ambiente ativado
python -m uvicorn backend_projeto.main:app --host 0.0.0.0 --port 8001
