$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $PSScriptRoot

if (-not (Test-Path '.venv')) {
  python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

if (-not $env:AIRTABLE_TOKEN) {
  throw 'AIRTABLE_TOKEN não está definido neste terminal.'
}

$env:NAVE_REPO_PATH = $Repo
python worker.py
