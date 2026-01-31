$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$Venv = Join-Path $Root ".venv"

function Test-Python {
    param([string[]]$Cmd)
    & $Cmd -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" | Out-Null
    return $LASTEXITCODE -eq 0
}

function Resolve-PythonCmd {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $cmd = @("py", "-3")
        if (Test-Python $cmd) { return $cmd }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $cmd = @("python")
        if (Test-Python $cmd) { return $cmd }
    }
    return $null
}

$PythonCmd = Resolve-PythonCmd
if (-not $PythonCmd) {
    Write-Host "Python 3.10+ not found."
    $resp = Read-Host "Install Python 3.11 with winget now? (y/N)"
    if ($resp -match "^(y|yes)$") {
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            Write-Error "winget not found. Install Python 3.10+ manually and re-run."
            exit 1
        }
        & winget install -e --id Python.Python.3.11 --source winget
    } else {
        exit 1
    }
    $PythonCmd = Resolve-PythonCmd
    if (-not $PythonCmd) {
        Write-Error "Python install not detected. Restart your shell or install manually."
        exit 1
    }
}

if (-not (Test-Path $Venv)) {
    & $PythonCmd -m venv $Venv
}

$Pip = Join-Path $Venv "Scripts\pip.exe"
$Py = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Pip)) {
    Write-Error "pip not found in .venv. Delete .venv and re-run the installer."
    exit 1
}

& $Py -m pip install --upgrade pip
& $Py -m pip install .

Write-Host "Install complete. Run: .venv\\Scripts\\python -m app.main --repo <path>"
