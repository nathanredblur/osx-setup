#!/bin/bash

# Change to the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 MacSnap Setup - Initialization Started"
echo "=========================================="
echo ""
echo "📋 System Information:"
echo "  • macOS Version: $(sw_vers -productVersion)"
echo "  • Architecture: $(uname -m)"
echo "  • User: $(whoami)"
echo "  • Date: $(date)"
echo "  • Working Directory: $(pwd)"
echo ""

echo "🔍 Environment Check:"

# Check essential tools
if command -v brew >/dev/null 2>&1; then
echo "  ✅ Homebrew: $(brew --version | head -1)"
else
echo "  ❌ Homebrew: Not found"
echo ""
echo "📦 Installing Homebrew..."
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

if command -v git >/dev/null 2>&1; then
echo "  ✅ Git: $(git --version)"
else
echo "  ⚠️  Git: Not found (will be installed)"
echo ""
echo "📦 Installing Git..."
brew install git
fi

echo ""
echo "📁 Creating necessary directories..."

# Create logs directory
mkdir -p "$HOME/.macsnap/logs"
echo "  ✅ Created: ~/.macsnap/logs"

# Create downloads cache
mkdir -p "$HOME/.macsnap/cache"
echo "  ✅ Created: ~/.macsnap/cache"

echo ""
echo "⚙️ Initial system configuration..."

# Set some useful macOS defaults for installation process
# Show hidden files in Finder during setup
defaults write com.apple.finder AppleShowAllFiles -bool true

# Disable Gatekeeper temporarily for installations (user will be prompted)
echo "  ℹ️  Some installations may require administrator privileges"

echo ""
echo "✅ Initialization completed successfully!"
echo "🎯 Ready to begin software installations..."
echo ""

# Create session log
SESSION_LOG="$HOME/.macsnap/logs/session-$(date +%Y%m%d-%H%M%S).log"
echo "MacSnap Installation Session" > "$SESSION_LOG"
echo "Started: $(date)" >> "$SESSION_LOG"
echo "User: $(whoami)" >> "$SESSION_LOG"
echo "System: $(sw_vers -productVersion) ($(uname -m))" >> "$SESSION_LOG"
echo "Script Directory: $SCRIPT_DIR" >> "$SESSION_LOG"
echo "Working Directory: $(pwd)" >> "$SESSION_LOG"
echo "----------------------------------------" >> "$SESSION_LOG"

export MACSNAP_SESSION_LOG="$SESSION_LOG"
echo "📄 Session log: $SESSION_LOG"

# Create a function to log and display output - universal compatibility
log_output() {
    while IFS= read -r line; do
        echo "$line"
        echo "$line" >> "$SESSION_LOG"
    done
}

# Function to run commands with logging
run_with_log() {
    "$@" 2>&1 | log_output
    return ${PIPESTATUS[0]}
}

# Install from Brewfile if it exists
if [ -f "Brewfile" ]; then
  echo "" | log_output
  echo "🍺 Installing Homebrew packages..." | log_output
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | log_output
  run_with_log brew bundle
  echo "✅ Homebrew installation completed successfully" | log_output
else
  echo "" | log_output
  echo "⚠️  No Brewfile found, skipping Homebrew installations" | log_output
fi

# Run custom installations if customInstall.sh exists
if [ -f "customInstall.sh" ]; then
  echo "" | log_output
  echo "🔧 Running custom installations..." | log_output
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | log_output
  run_with_log bash ./customInstall.sh
  echo "✅ Custom installations completed" | log_output
else
  echo "" | log_output
  echo "ℹ️  No customInstall.sh found, skipping custom installations" | log_output
fi

# Run post-configuration if postConfig.sh exists
if [ -f "postConfig.sh" ]; then
  echo "" | log_output
  echo "⚙️ Running post-configuration..." | log_output
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | log_output
  run_with_log bash ./postConfig.sh
  echo "✅ Post-configuration completed" | log_output
else
  echo "" | log_output
  echo "ℹ️  No postConfig.sh found, skipping post-configuration" | log_output
fi

# Continue logging for the rest of the script
{
echo ""
echo ""
echo "🏁 MacSnap Setup - Finalization"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🧹 Performing final cleanup..."

# Cleanup Homebrew
if command -v brew >/dev/null 2>&1; then
echo "  🍺 Cleaning up Homebrew cache..."
brew cleanup --prune=7 2>/dev/null || true
brew doctor 2>/dev/null | head -10 || true
fi

# Reset Finder to normal (hide hidden files again)
defaults write com.apple.finder AppleShowAllFiles -bool false
killall Finder 2>/dev/null || true
echo "  👁️  Reset Finder view settings"

# Clear temporary files
echo "  🗑️  Clearing temporary files..."
rm -rf /tmp/macsnap-* 2>/dev/null || true
rm -rf "$HOME/.macsnap/cache/"*.tmp 2>/dev/null || true

echo ""
echo "📊 Installation Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count installed applications
APP_COUNT=$(find /Applications -maxdepth 1 -name "*.app" | wc -l | tr -d ' ')
echo "  📱 Applications installed: $APP_COUNT"

# Check Homebrew packages
if command -v brew >/dev/null 2>&1; then
BREW_COUNT=$(brew list --formula 2>/dev/null | wc -l | tr -d ' ')
CASK_COUNT=$(brew list --cask 2>/dev/null | wc -l | tr -d ' ')
echo "  🍺 Homebrew formulas: $BREW_COUNT"
echo "  📦 Homebrew casks: $CASK_COUNT"
fi

# # Update locate database
# echo "  🔍 Updating locate database..."
# sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.locate.plist 2>/dev/null || true

# # Rebuild Launch Services database
# echo "  🚀 Rebuilding Launch Services database..."
# /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user 2>/dev/null || true

echo ""
echo "💡 Next Steps:"
echo "━━━━━━━━━━━━━━━"
echo "  1. 🔄 Restart your Mac to ensure all changes take effect"
echo "  2. 🔐 Review System Preferences > Security & Privacy"
echo "  3. 📱 Launch newly installed applications to complete setup"
echo "  4. ☁️  Sign in to cloud services (iCloud, Dropbox, etc.)"
echo "  5. 🔑 Configure SSH keys and development tools"
echo "  6. 🎨 Customize Dock, menu bar, and desktop settings"
echo ""

echo "🎯 Quick Start:"
echo "━━━━━━━━━━━━━━━"
echo "  • ⌘+Space: Spotlight Search to find applications"
echo "  • System Preferences: Customize your Mac"
echo "  • Terminal/iTerm2: Access command-line tools"
echo "  • brew search <package>: Find more software"
echo ""

# Generate installation report
REPORT_FILE="$HOME/.macsnap/installation-report-$(date +%Y%m%d-%H%M%S).txt"
{
echo "MacSnap Installation Report"
echo "=========================="
echo "Date: $(date)"
echo "System: $(sw_vers -productVersion) ($(uname -m))"
echo ""
echo "Installed Applications:"
ls -1 /Applications | grep -E '\.app$' | sed 's/\.app$//' | sort
echo ""
if command -v brew >/dev/null 2>&1; then
    echo "Homebrew Packages:"
    brew list --formula 2>/dev/null | sort
    echo ""
    echo "Homebrew Casks:"
    brew list --cask 2>/dev/null | sort
fi
} > "$REPORT_FILE"

echo ""
echo "📋 Reports Generated:"
echo "━━━━━━━━━━━━━━━━━━━"
echo "  📄 Session log: $MACSNAP_SESSION_LOG"
echo "  📊 Installation report: $REPORT_FILE"

echo ""
echo "✅ MacSnap Setup completed successfully!"
echo "🚀 Your Mac is now configured and ready to use!"
echo ""

} | log_output
