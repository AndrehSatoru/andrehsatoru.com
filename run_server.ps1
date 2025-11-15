# Navega para o diretório do backend
Set-Location -Path "packages/backend"

# Ativa o ambiente virtual
.\venv\Scripts\Activate.ps1

# Executa o uvicorn no ambiente ativado
python -m uvicorn src.backend_projeto.main:app --host 0.0.0.0 --port 8001
