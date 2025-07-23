#!/bin/zsh

# MacSnap - Simple Setup (Using macOS native Python)

set -e

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${0%/*}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"
MACSNAP_SCRIPT="${SCRIPT_DIR}/macsnap.py"

# Simple logging
log_info() { echo "🔵 INFO: $1"; }
log_warn() { echo "🟡 WARN: $1" >&2; }
log_error() { echo "🔴 ERROR: $1" >&2; }
log_success() { echo "✅ SUCCESS: $1"; }

log_info "MacSnap Simple Setup - Using macOS native tools"
log_info "Script directory: $SCRIPT_DIR"

# --- 1. Install Xcode Developer Tools (Essential for Homebrew and development) ---
install_xcode_tools() {
  log_info "Checking for Xcode Command Line Tools..."
  
  if xcode-select -p &>/dev/null; then
    log_success "Xcode Command Line Tools already installed at: $(xcode-select -p)"
  else
    log_info "Installing Xcode Command Line Tools..."
    log_warn "A dialog will appear - click 'Install' to continue"
    
    # xcode-select --install
    # This temporary file prompts the 'softwareupdate' utility to list the Command Line Tools
    touch /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress;
    PROD=$(softwareupdate -l | grep "\*.*Command Line" | tail -n 1 | sed 's/^[^C]* //')
    softwareupdate -i "$PROD" --verbose;
    
    log_info "Waiting for Xcode Command Line Tools installation..."
    log_info "This may take several minutes depending on your connection"
    
    # Wait for installation to complete
    while ! xcode-select -p &>/dev/null; do
      echo -n "."
      sleep 5
    done
    echo ""
    
    log_success "Xcode Command Line Tools installed successfully!"
  fi
}

# --- 2. Install Homebrew (if not installed) ---
install_homebrew() {
  log_info "Checking for Homebrew..."
  
  if command -v brew &>/dev/null; then
    log_success "Homebrew already installed"
    
    # Configure brew PATH for current session
    if [[ "$(uname -m)" == "arm64" ]]; then
      export PATH="/opt/homebrew/bin:$PATH"
    else
      export PATH="/usr/local/bin:$PATH"
    fi
    
    # Disable analytics and update
    brew analytics off 2>/dev/null || true
    log_info "Updating Homebrew..."
    brew update
    
  else
    log_info "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Configure PATH
    if [[ "$(uname -m)" == "arm64" ]]; then
      eval "$(/opt/homebrew/bin/brew shellenv)"
      export PATH="/opt/homebrew/bin:$PATH"
    else
      eval "$(/usr/local/bin/brew shellenv)"
      export PATH="/usr/local/bin:$PATH"
    fi
    
    # Disable analytics
    brew analytics off
    log_success "Homebrew installed successfully!"
  fi
}

# --- 3. Verify Python 3 (should be available natively on macOS) ---
verify_python() {
  log_info "Verifying Python 3 availability..."
  
  if command -v python3 &>/dev/null; then
    local python_version=$(python3 --version)
    log_success "Python 3 found: $python_version"
    
    # Check if it's a reasonable version (3.8+)
    local version_check=$(python3 -c "import sys; print(1 if sys.version_info >= (3, 8) else 0)")
    if [[ "$version_check" == "1" ]]; then
      log_success "Python version is compatible (3.8+)"
    else
      log_warn "Python version might be old. Consider updating if you encounter issues."
    fi
  else
    log_error "Python 3 not found on system"
    log_error "This is unexpected on macOS. Please install Python 3 manually or use setup.sh instead"
    exit 1
  fi
}

# --- 4. Create Virtual Environment ---
create_venv() {
  if [[ -d "$VENV_DIR" ]]; then
    log_info "Virtual environment already exists at $VENV_DIR"
  else
    log_info "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created at $VENV_DIR"
  fi
}

# --- 5. Install Dependencies ---
install_dependencies() {
  if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
    log_error "requirements.txt not found at $REQUIREMENTS_FILE"
    exit 1
  fi
  
  log_info "Installing Python dependencies..."
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"
  log_success "Dependencies installed successfully"
}

# --- 6. Launch MacSnap ---
launch_macsnap() {
  if [[ ! -f "$MACSNAP_SCRIPT" ]]; then
    log_error "macsnap.py not found at $MACSNAP_SCRIPT"
    exit 1
  fi
  
  log_success "Setup complete! Launching MacSnap..."
  log_info "=============================================="
  
  # Launch MacSnap with all passed arguments
  exec "$VENV_DIR/bin/python" "$MACSNAP_SCRIPT" "$@"
}

# --- Main Execution ---
main() {
  log_info "Starting MacSnap Simple Setup..."
  
  # Install essential tools
  install_xcode_tools
  #install_homebrew
  
  # Verify and setup Python environment
  verify_python
  create_venv
  install_dependencies
  
  # Launch the application
  launch_macsnap "$@"
}

# Run main function with all script arguments
main "$@" 