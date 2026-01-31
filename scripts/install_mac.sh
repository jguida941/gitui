#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

need_python=0
if command -v python3 >/dev/null 2>&1; then
  if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)'; then
    need_python=1
  fi
else
  need_python=1
fi

if [ "$need_python" -eq 1 ]; then
  echo "Python 3.10+ not found."
  read -r -p "Install Python with Homebrew now? (y/N): " ans
  case "$ans" in
    y|Y|yes|YES)
      ;;
    *)
      exit 1
      ;;
  esac

  BREW_CMD=""
  if command -v brew >/dev/null 2>&1; then
    BREW_CMD="brew"
  elif [ -x "/opt/homebrew/bin/brew" ]; then
    BREW_CMD="/opt/homebrew/bin/brew"
  elif [ -x "/usr/local/bin/brew" ]; then
    BREW_CMD="/usr/local/bin/brew"
  fi

  if [ -z "$BREW_CMD" ]; then
    read -r -p "Homebrew not found. Install Homebrew now? (y/N): " brew_ans
    case "$brew_ans" in
      y|Y|yes|YES)
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ;;
      *)
        exit 1
        ;;
    esac
    if [ -x "/opt/homebrew/bin/brew" ]; then
      BREW_CMD="/opt/homebrew/bin/brew"
    elif [ -x "/usr/local/bin/brew" ]; then
      BREW_CMD="/usr/local/bin/brew"
    fi
  fi

  if [ -z "$BREW_CMD" ]; then
    echo "Homebrew install not detected. Install Python 3.10+ manually and re-run."
    exit 1
  fi

  "$BREW_CMD" install python
  export PATH="$("$BREW_CMD" --prefix)/bin:$PATH"

  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python install not detected. Restart your shell or install manually."
    exit 1
  fi
  if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)'; then
    echo "Python 3.10+ still not available. Restart your shell or install manually."
    exit 1
  fi
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install .

echo "Install complete!"
echo ""
echo "To launch GitUI:"
echo "  $ROOT/.venv/bin/python -m app.main"
echo ""
echo "To open a specific repo:"
echo "  $ROOT/.venv/bin/python -m app.main --repo <path>"
