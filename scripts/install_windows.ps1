$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$Venv = Join-Path $Root ".venv"

function Test-Python {
    param([string[]]$Cmd)
    $code = 'import sys, os; exe=sys.executable or ""; ok=sys.version_info >= (3,10) and "windowsapps" not in exe.lower(); print("PYOK" if ok else "PYNO"); raise SystemExit(0 if ok else 1)'
    $out = & $Cmd -c $code 2>$null
    return ($LASTEXITCODE -eq 0) -and ($out -match "PYOK")
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

function Invoke-Checked {
    param([object]$Cmd, [string[]]$Args)
    & $Cmd @Args
    if ($LASTEXITCODE -ne 0) {
        $cmdText = if ($Cmd -is [System.Collections.IEnumerable] -and $Cmd -notis [string]) { $Cmd -join " " } else { [string]$Cmd }
        $argText = if ($Args) { $Args -join " " } else { "" }
        $msg = ("Command failed: " + $cmdText + " " + $argText).Trim()
        throw $msg
    }
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
    Invoke-Checked -Cmd $PythonCmd -Args @("-m", "venv", $Venv)
}

$Pip = Join-Path $Venv "Scripts\pip.exe"
$Py = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Pip)) {
    Write-Error "pip not found in .venv. Delete .venv and re-run the installer."
    exit 1
}

Invoke-Checked -Cmd $Py -Args @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Checked -Cmd $Py -Args @("-m", "pip", "install", ".")

Write-Host "Install complete!"
Write-Host ""
Write-Host "To launch GitUI:"
Write-Host "  $Root\.venv\Scripts\python -m app.main"
Write-Host ""
Write-Host "To open a specific repo:"
Write-Host "  $Root\.venv\Scripts\python -m app.main --repo <path>"
