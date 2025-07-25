#!/bin/zsh

# MacSnap - Python Bootstrapper

# Exit immediately if a command exits with a non-zero status.
set -e

# Determine the script's absolute directory
SCRIPT_DIR="$(cd "$(dirname "${0%/*}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
# PYTHON_EXEC will be determined after Python is ensured
# PIP_EXEC will be determined after Python is ensured
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"
MACSNAP_PYTHON_SCRIPT="${SCRIPT_DIR}/macsnap.py"

# --- Logging (simple echo for bootstrap) ---
_log_info() { echo "BOOTSTRAP INFO: $1"; }
_log_warn() { echo "BOOTSTRAP WARN: $1" >&2; }
_log_error() { echo "BOOTSTRAP ERROR: $1" >&2; }

_log_info "Starting MacSnap Python Bootstrapper..."
_log_info "Script directory: $SCRIPT_DIR"

# --- 1. Install Homebrew (if not installed) ---
install_homebrew() {
  _log_info "Checking for Homebrew..."
  if ! command -v brew &> /dev/null; then
    _log_info "Homebrew not found. Installing Homebrew..."
    # Suppressing output of the Homebrew install script for cleaner logs,
    # but errors will still cause script to exit due to 'set -e'.
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" > /dev/null
    _log_info "Homebrew installer finished. Adding brew to PATH for current session..."
    if [[ "$(uname -m)" == "arm64" ]]; then # Apple Silicon
        eval "$(/opt/homebrew/bin/brew shellenv)"
        export PATH="/opt/homebrew/bin:$PATH" # Explicitly ensure it for subsequent commands
    else # Intel
        eval "$(/usr/local/bin/brew shellenv)"
        export PATH="/usr/local/bin:$PATH" # Explicitly ensure it
    fi
    _log_info "SUCCESS: Homebrew installed and configured in PATH."
  else
    _log_info "SUCCESS: Homebrew is already installed."
    # Ensure brew is in PATH for subsequent commands in this script, even if already installed
    if [[ "$(uname -m)" == "arm64" ]] && [[ -x /opt/homebrew/bin/brew ]]; then
        export PATH="/opt/homebrew/bin:$PATH"
    elif [[ -x /usr/local/bin/brew ]]; then
        export PATH="/usr/local/bin:$PATH"
    fi
  fi
  brew analytics off
}

install_homebrew # Call the function

# --- 2. Check for Python 3 & Install with Homebrew if needed ---
PYTHON3_EXECUTABLE="python3" # Default command to check

if ! command -v $PYTHON3_EXECUTABLE &>/dev/null; then
    _log_warn "Python 3 (as '$PYTHON3_EXECUTABLE') is not found in your PATH."
    _log_info "Attempting to install Python 3 using Homebrew..."
    if ! command -v brew &> /dev/null; then
        _log_error "Homebrew command (brew) not found. Cannot install Python."
        _log_error "Please ensure Homebrew was installed correctly in the previous step or is already available."
        exit 1
    fi
    brew install python
    _log_info "Homebrew finished attempting to install Python."
    # After brew install python, python3 should be in the PATH if successful
    # Homebrew handles symlinking python3 from its keg, e.g. /opt/homebrew/bin/python3
    if ! command -v $PYTHON3_EXECUTABLE &>/dev/null; then
        _log_error "Failed to find '$PYTHON3_EXECUTABLE' after 'brew install python'."
        _log_error "Please check Homebrew's output and ensure Python was installed and is in your PATH."
        _log_error "Common Python 3 paths from Homebrew: /opt/homebrew/bin/python3 (Apple Silicon) or /usr/local/bin/python3 (Intel)."
        exit 1
    fi
    _log_info "SUCCESS: Python 3 installed via Homebrew and '$PYTHON3_EXECUTABLE' is now available."
else
    _log_info "Python 3 (as '$PYTHON3_EXECUTABLE') found: $($PYTHON3_EXECUTABLE --version)"
fi

# Define Python and Pip executables for the virtual environment relative to SCRIPT_DIR
PYTHON_EXEC_FOR_VENV="$PYTHON3_EXECUTABLE" # Use the python3 found/installed
PIP_EXEC_FOR_VENV="$PYTHON3_EXECUTABLE -m pip" # Use python3 -m pip for robustness

ACTUAL_PYTHON_EXEC="${VENV_DIR}/bin/python3"
ACTUAL_PIP_EXEC="${VENV_DIR}/bin/pip"

# --- 3. Check/Ensure pip for the selected Python 3 (needed for venv) ---
# This step checks if the selected python3 has a working pip module.
if ! $PYTHON_EXEC_FOR_VENV -m ensurepip --default-pip --check &>/dev/null; then
    _log_warn "Standard pip module not confirmed with '$PYTHON_EXEC_FOR_VENV -m ensurepip --check'."
    _log_info "Attempting to ensure pip module is available for $PYTHON_EXEC_FOR_VENV..."
    if ! $PYTHON_EXEC_FOR_VENV -m ensurepip --default-pip --user; then # --user might not be ideal if we immediately use venv
    # Alternative: if system python doesn't have ensurepip, brew installed python usually does.
        _log_warn "Failed to ensure pip module using '$PYTHON_EXEC_FOR_VENV -m ensurepip --default-pip'."
        _log_warn "If '$PYTHON_EXEC_FOR_VENV -m venv .venv' fails, you may need to configure pip for $PYTHON_EXEC_FOR_VENV manually."
    else
        _log_info "Pip module should now be available for $PYTHON_EXEC_FOR_VENV."
    fi
fi

# --- 4. Create Virtual Environment (.venv) if it doesn't exist ---
if [ ! -d "$VENV_DIR" ]; then
    _log_info "Python virtual environment not found at $VENV_DIR. Creating with $PYTHON_EXEC_FOR_VENV..."
    if ! $PYTHON_EXEC_FOR_VENV -m venv "$VENV_DIR"; then
        _log_error "Failed to create Python virtual environment using $PYTHON_EXEC_FOR_VENV."
        _log_error "Please check your Python 3 installation and ensure the 'venv' module is available for it."
        exit 1
    fi
    _log_info "Virtual environment created successfully at $VENV_DIR."
else
    _log_info "Python virtual environment found at $VENV_DIR."
fi

# --- 5. Install/Upgrade Dependencies in .venv ---
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    _log_error "requirements.txt not found at $REQUIREMENTS_FILE."
    _log_error "Cannot install Python dependencies."
    exit 1
fi

_log_info "Installing/Updating Python dependencies from $REQUIREMENTS_FILE into $VENV_DIR using $ACTUAL_PIP_EXEC..."
if ! "$ACTUAL_PIP_EXEC" install -r "$REQUIREMENTS_FILE"; then
    _log_error "Failed to install Python dependencies using $ACTUAL_PIP_EXEC."
    _log_error "Ensure your virtual environment and pip are functioning correctly."
    exit 1
fi
_log_info "Python dependencies installed/updated successfully."

# --- 6. Execute the main Python script ---
if [ ! -f "$MACSNAP_PYTHON_SCRIPT" ]; then
    _log_error "Main Python script macsnap.py not found at $MACSNAP_PYTHON_SCRIPT."
    exit 1
fi

_log_info "Executing Python application: $MACSNAP_PYTHON_SCRIPT with $ACTUAL_PYTHON_EXEC ..."
_log_info "----------------------------------------------------" # Separator

# Pass all arguments received by this shell script to the Python script
exec "$ACTUAL_PYTHON_EXEC" "$MACSNAP_PYTHON_SCRIPT" "$@"

_log_info "Python application finished." # This line might not be reached if exec is used. 