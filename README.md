# CyberMac Setup - Technical Design Document (Updated)

## 1. System Overview

**CyberMac Setup** is an interactive terminal application with a cyberpunk theme that automates the installation and configuration of macOS systems (version 15.4.1 and up). Built with Ink (React for terminal), it provides a visually appealing interface for managing software installation and system configuration.

## 2. Architecture

### 2.1 Core Components

1. **Command Line Interface (CLI)**
   - Ink-based cyberpunk-themed UI
   - Interactive selection menus
   - Animated progress indicators

2. **Configuration System**
   - YAML configuration files for all installable items
   - Support for dependencies and installation order
   - Categorization of software and configurations

3. **Installation Engine**
   - Executes installation scripts based on configuration
   - Validates existing installations
   - Handles different installation types (brew, mas, direct download)

4. **System Configuration Engine**
   - Applies system settings via defaults commands
   - Manages keyboard, trackpad, dock, and accessibility settings
   - Handles permission requests when needed

### 2.2 Directory Structure

```
cybermac/
├── bin/
│   └── cybermac              # Main executable
├── src/
│   ├── cli/                  # CLI components
│   │   ├── components/       # Reusable UI components
│   │   │   ├── Header.jsx    # Cyberpunk header
│   │   │   ├── Footer.jsx    # Status footer
│   │   │   ├── ProgressBar.jsx # Animated progress
│   │   │   └── SelectionList.jsx # Interactive selection
│   │   ├── screens/          # Full-screen views
│   │   │   ├── MainMenu.jsx  # Main category menu
│   │   │   ├── CategoryView.jsx # Category items view
│   │   │   └── InstallProgress.jsx # Installation progress
│   │   └── styles/           # UI styling
│   │       └── theme.js      # Cyberpunk color scheme
│   ├── core/                 # Core functionality
│   │   ├── engine.js         # Installation engine
│   │   ├── validator.js      # Installation validation
│   │   ├── config-loader.js  # Config processor
│   │   └── system-config.js  # System settings manager
│   └── utils/                # Utility functions
│       ├── shell.js          # Shell command execution
│       ├── permissions.js    # Permission handling
│       └── logger.js         # Logging functionality
├── configs/                  # Configuration files
│   ├── essentials/           # Essential software
│   │   ├── brew.yaml         # Homebrew
│   │   ├── mas.yaml          # Mac App Store CLI
│   │   └── iterm2.yaml       # iTerm2
│   ├── shells/               # Shell configurations
│   │   ├── oh-my-posh.yaml   # Oh My Posh
│   │   └── antidote.yaml     # Antidote (Zsh plugins)
│   ├── development/          # Dev tools
│   │   ├── proto.yaml        # Proto version manager
│   │   ├── node.yaml         # Node.js
│   │   ├── pnpm.yaml         # PNPM
│   │   ├── npm.yaml          # NPM
│   │   ├── yarn.yaml         # Yarn
│   │   ├── docker.yaml       # Docker
│   │   └── vscode.yaml       # VS Code
│   ├── utilities/            # Utility apps
│   │   ├── raycast.yaml      # Raycast
│   │   ├── rectangle.yaml    # Rectangle Pro
│   │   ├── meetingbar.yaml   # MeetingBar
│   │   ├── bartender.yaml    # Bartender
│   │   ├── alttab.yaml       # AltTab
│   │   └── ...               # Other utilities
│   ├── browsers/             # Web browsers
│   │   ├── chrome.yaml       # Chrome
│   │   ├── edge.yaml         # Edge
│   │   ├── vivaldi.yaml      # Vivaldi
│   │   └── ...               # Other browsers
│   ├── media/                # Media applications
│   │   ├── spotify.yaml      # Spotify
│   │   ├── vlc.yaml          # VLC
│   │   ├── stremio.yaml      # Stremio
│   │   └── ...               # Other media apps
│   ├── communication/        # Communication apps
│   │   ├── telegram.yaml     # Telegram
│   │   ├── whatsapp.yaml     # WhatsApp
│   │   └── ...               # Other communication apps
│   └── system/               # System settings
│       ├── trackpad.yaml     # Trackpad settings
│       ├── keyboard.yaml     # Keyboard settings
│       ├── dock.yaml         # Dock settings
│       ├── accessibility.yaml # Accessibility settings
│       └── keyboard-fix.yaml # Keyboard fix agent
└── package.json              # Node.js package definition
```

## 3. Configuration File Format

Each software or configuration will be defined in a YAML file:

```yaml
id: "iterm2"
name: "iTerm2"
description: "A replacement for Terminal and the successor to iTerm"
type: "brew_cask"
category: "essentials"
required: false  # Whether this is a required installation
install:
  script: |
    brew install --cask iterm2
  dependencies:
    - "brew"
validate:
  script: |
    brew list --cask | grep -q "^iterm2$"
configure:
  script: |
    # Copy preferences
    cp "${CONFIG_DIR}/iterm2/com.googlecode.iterm2.plist" \
       "${HOME}/Library/Preferences/com.googlecode.iterm2.plist"
uninstall:
  script: |
    brew uninstall --cask iterm2
```

For system configurations:

```yaml
id: "trackpad-settings"
name: "Trackpad Settings"
description: "Configure trackpad with tap to click"
type: "system_config"
category: "system"
required: false
configure:
  script: |
    # Enable tap to click
    defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true
    defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true
    defaults -currentHost write NSGlobalDomain com.apple.mouse.tapBehavior -int 1
    defaults write NSGlobalDomain com.apple.mouse.tapBehavior -int 1
validate:
  script: |
    defaults read com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking | grep -q "1"
```

## 4. User Interface Design

### 4.1 Cyberpunk Theme Elements

- **Color Palette**:
  - Primary: Electric blue (#00FFFF)
  - Secondary: Neon pink (#FF00FF)
  - Accent: Neon green (#00FF00)
  - Background: Dark with grid patterns
  - Text: High contrast with glow effects

- **Typography**:
  - Monospace fonts with "digital" appearance
  - ASCII art for headers and decorative elements
  - Glitch effects for transitions

- **Animations**:
  - "Matrix-like" data flow for loading
  - Scan-line effects
  - Pulsing elements for selection

### 4.2 Main UI Components

1. **Header Component**
   - ASCII art logo
   - System information display
   - Current operation status

2. **Main Menu Screen**
   - Categories displayed in a grid
   - Cyberpunk-styled selection indicators
   - Status summary of installed/pending items

3. **Category View Screen**
   - List of installable items with status indicators
   - Multi-select capability
   - Dependency visualization

4. **Installation Progress Screen**
   - Animated progress bars with cyberpunk styling
   - Real-time command output
   - Error handling with visual indicators

5. **Summary Screen**
   - Installation results with success/failure counts
   - System configuration status
   - Options for next steps

## 5. Core Functions

### 5.1 Configuration Management

**`loadConfigurations(configDir)`**
- Loads all YAML configuration files
- Organizes by category and type
- Builds dependency graph

**`validateConfigurations(configs)`**
- Checks for format errors
- Validates required fields
- Ensures scripts are properly formed

**`checkDependencies(configs, selections)`**
- Identifies missing dependencies for selected items
- Builds installation order

### 5.2 Installation Engine

**`checkInstallStatus(config)`**
- Runs validation script to check if already installed
- Returns status object with details

**`installItem(config)`**
- Executes installation script with progress reporting
- Handles errors and retries
- Updates status in real-time

**`configureItem(config)`**
- Applies configuration settings
- Handles permission requests when needed

**`batchInstall(configs, options)`**
- Installs multiple items in correct order
- Provides aggregate progress

### 5.3 System Configuration

**`applySystemSettings(configs)`**
- Applies macOS defaults commands
- Handles permission elevation when needed
- Validates successful application

**`installKeyboardFix()`**
- Installs keyboard remapping agent
- Sets up launchd service

### 5.4 UI Functions

**`renderMainMenu(categories, stats)`**
- Displays cyberpunk-styled main menu
- Shows installation statistics

**`renderCategoryView(category, items)`**
- Displays items in selected category
- Allows multi-selection with dependencies

**`renderProgressView(operations)`**
- Shows real-time installation progress
- Displays command output with styling

## 6. Implementation Details

### 6.1 Specific Software Installation Handlers

We'll implement specialized handlers for different installation types:

1. **Homebrew Formula/Cask Handler**
   - Installs via `brew install` or `brew install --cask`
   - Handles updates and reinstalls

2. **Mac App Store Handler**
   - Uses `mas` to install from App Store
   - Requires Apple ID authentication

3. **Direct Download Handler**
   - Downloads from URLs and installs packages
   - Handles verification and cleanup

4. **Node Package Handler**
   - Installs global npm/yarn/pnpm packages
   - Manages version requirements

### 6.2 System Configuration Handlers

1. **Defaults Command Handler**
   - Manages macOS defaults commands
   - Handles domain-specific settings

2. **Plist Configuration Handler**
   - Modifies property list files
   - Handles binary and XML formats

3. **Permission Handler**
   - Manages accessibility permissions
   - Handles security preferences

### 6.3 Shell Integration

1. **Oh My Posh Setup**
   - Installs Oh My Posh
   - Configures themes
   - Installs required fonts

2. **Antidote Configuration**
   - Sets up Zsh plugin management
   - Configures plugin list

3. **Terminal Configuration**
   - Configures Warp and iTerm2 preferences
   - Sets up default profiles

## 7. Specific Software Installation List

### 7.1 Essential Tools
- Homebrew
- Mac App Store CLI (mas)
- iTerm2
- Antidote (Zsh plugin manager)

### 7.2 Development Tools
- Proto (version manager)
- Node.js (via Proto)
- Package managers (npm, yarn, pnpm, uv) (via Proto)
- Docker
- Visual Studio Code

### 7.3 Terminal & Shell
- Oh My Posh
- Custom fonts (via Oh My Posh)
- Zsh plugins (via Antidote)

### 7.4 Productivity Applications
- Warp Terminal
- Raycast
- Rectangle Pro
- MeetingBar
- Bartender
- AltTab
- CleanShot X

### 7.5 Browsers
- Google Chrome
- Microsoft Edge
- Vivaldi
- Zen Browser

### 7.6 Media Applications
- Spotify
- VLC
- Stremio
- Audacity
- YACReader
- Transmission

### 7.7 Communication
- Telegram
- WhatsApp

### 7.8 Utilities
- BetterZip
- Calibre
- ChatGPT
- Claude
- DBeaver
- MonitorControl
- Time Out
- Synthesia

### 7.9 System Configurations
- Trackpad: Tap to click
- Accessibility: Full keyboard access
- Accessibility: Zoom settings
- Dock: Auto-hide, size, remove default apps
- Keyboard: Repeat rate, delay until repeat
- Keyboard: Disable Spotlight shortcuts
- Custom keyboard remapping agent

## 8. Implementation Plan

### 8.1 Phase 1: Core Framework
- Set up project structure with Node.js and Ink
- Implement configuration loading and validation
- Create basic UI components with cyberpunk styling

### 8.2 Phase 2: Essential Installations
- Implement Homebrew installation
- Add support for brew formula/cask installations
- Implement Mac App Store integration

### 8.3 Phase 3: System Configuration
- Implement defaults command handling
- Add support for accessibility and security settings
- Create keyboard remapping agent installation

### 8.4 Phase 4: UI Enhancement
- Develop full cyberpunk theme
- Add animations and interactive elements
- Implement progress visualization

### 8.5 Phase 5: Application-Specific Configurations
- Add post-installation configuration for applications
- Implement preference file management
- Add support for extension installation

## 9. Technical Requirements

- Node.js 18+
- Ink framework for terminal UI
- YAML for configuration files
- macOS 15.4.1 or newer
- Administrative privileges for system modifications

## 10. Next Steps

1. Set up basic project structure
2. Create initial configuration files for essential software
3. Implement core installation engine
4. Develop basic UI components
5. Test with a subset of installations

This updated technical design incorporates your specific requirements for software installation and system configuration. The cyberpunk-themed interface will provide an engaging experience while automating the setup of your macOS environment.