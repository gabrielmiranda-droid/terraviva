$ErrorActionPreference = "Stop"

$BackendDir = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$ProjectDir = Resolve-Path -LiteralPath (Join-Path $BackendDir "..")
$EnvPath = Join-Path $ProjectDir ".env"
$PythonPath = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (!(Test-Path -LiteralPath $EnvPath)) {
    throw "Arquivo .env nao encontrado na raiz do projeto."
}

if (!(Test-Path -LiteralPath $PythonPath)) {
    throw "Ambiente Python nao encontrado em backend\.venv. Rode pip install -r requirements.txt no backend antes."
}

$env:DATABASE_URL = $null
$env:AUTO_SEED = "true"
Set-Location -LiteralPath $BackendDir
& $PythonPath -m alembic upgrade head
& $PythonPath -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
