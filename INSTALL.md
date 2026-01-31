# Install GitUI

This repo ships one-run installers for Windows (PowerShell/CMD) and macOS. Each installer creates a local `.venv` and installs GitUI into it.

Prereqs:
- Git
- Python 3.10+ (installers can prompt to install it)

## 1) Clone the repo

```bash
git clone https://github.com/jguida941/gitui
cd gitui
```

## 2) Run the installer

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_windows.ps1
```

### Windows (CMD)

```bat
cmd /c scripts\install_windows.cmd
```

### macOS

```bash
bash scripts/install_mac.sh
```

## 3) Run GitUI

### macOS

```bash
.venv/bin/python -m app.main --repo /path/to/repo
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\python -m app.main --repo C:\path\to\repo
```

### Windows (CMD)

```cmd
.venv\Scripts\python -m app.main --repo C:\path\to\repo
```

## Update (same venv)

```bash
git pull

# macOS
.venv/bin/pip install -U .

# Windows (PowerShell or CMD)
.venv\Scripts\pip install -U .
```

## Homebrew (release required)

Homebrew installs require a tagged release and a tap repository. Use the formula template in `packaging/homebrew/gitui.rb`.
Note: `brew install gitui` installs the Rust TUI from Homebrew/core, not this app. Use the fully-qualified formula name below.

### Install Homebrew (macOS)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Create a tap repo

Tap repo: https://github.com/jguida941/homebrew-gitui

Users will run:

```bash
brew tap jguida941/gitui
brew install jguida941/gitui/gitui
```

If you already installed the Homebrew/core `gitui`, remove it first:

```bash
brew uninstall gitui
```

### Update via Homebrew

```bash
brew update
brew upgrade jguida941/gitui/gitui
```
