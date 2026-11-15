# Dot-source before any project command:   . .\scripts\env.ps1
# Keeps every tool, cache and model download inside the project folder
# (shared machine: nothing system-wide, nothing in the user profile).
$root = Split-Path -Parent $PSScriptRoot

$env:UV_PYTHON_INSTALL_DIR = "$root\.tools\python"   # project-local CPython
$env:UV_PYTHON_PREFERENCE  = "only-managed"
$env:UV_CACHE_DIR          = "$root\.cache\uv"
$env:UV_PROJECT_ENVIRONMENT = "$root\.venv"
$env:UV_NO_MODIFY_PATH     = "1"

$env:HF_HOME               = "$root\.cache\hf"       # model weights land here
$env:HF_HUB_DISABLE_TELEMETRY = "1"
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"
$env:TORCH_HOME            = "$root\.cache\torch"
$env:MPLCONFIGDIR          = "$root\.cache\mpl"
$env:PYTHONUTF8            = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:TOKENIZERS_PARALLELISM = "false"

$env:Path = "$root\.tools\uv;$root\.venv\Scripts;$env:Path"
