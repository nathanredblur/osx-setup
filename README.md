# MacSnap Setup - Technical Design Document (Revised)

## 1. System Overview

**MacSnap Setup** is an interactive terminal application designed to automate the installation and configuration of macOS systems (version 15.4.1 and up). Built with Python, it provides a user-friendly command-line interface for managing software installation and system customization. The tool is designed to be re-runnable, allowing users to install new items without affecting already installed software.

The application is executed via `setup.sh`, which handles the initial setup of prerequisites (Homebrew) and Python environment configuration before launching the main Python application.

## 2. Architecture

### 2.1 Core Components

1.  **Command Line Interface (CLI)**

    - Python-based interactive interface.
    - Interactive selection menus for categories and items.
    - Real-time feedback and progress indicators.
    - Optional verbose logging with `--verbose` parameter.

2.  **Configuration System**

    - YAML configuration files for all installable software, system settings, and custom scripts.
    - Each item is defined in its own YAML file within the `configs/` directory.
    - Support for dependencies to ensure correct installation order.
    - Categorization of items (e.g., essentials, development, shells) within YAML files for UI grouping.

3.  **Installation Engine**

    - Parses YAML configurations and executes associated installation scripts.
    - Validates existing installations to avoid redundant operations.
    - Handles various installation types through specific handlers.
    - Manages error handling: continues on non-critical failures, halts dependent items if a critical dependency fails.
    - Provides detailed logging for debugging.

4.  **System Configuration Engine**

    - Applies system settings via `defaults` commands and other macOS mechanisms.
    - Manages settings for trackpad, keyboard (including custom remapping), dock, and accessibility.
    - Guides users through necessary permission grants.

5.  **Logging System**
    - Comprehensive logging of all operations, script outputs (stdout/stderr), and errors.
    - Optional verbose mode activated with `--verbose` parameter.
    - Logs stored in user-accessible location (e.g., `~/Library/Logs/MacSnap/setup.log`).

### 2.2 Directory Structure

The project files are organized as follows:

```
./
├── setup.sh               # Bootstrap script - installs Homebrew and configures Python environment
├── macsnap.py             # Main Python application entry point
├── requirements.txt       # Python dependencies
├── utils/                 # Python utility modules for the macsnap application
│   ├── __init__.py
│   ├── config_loader.py   # YAML configuration loading and parsing
│   ├── installer.py       # Installation engine and handlers
│   ├── logger.py          # Logging system
│   ├── ui.py             # User interface components
│   └── validators.py      # Configuration validation
└── configs/               # Root directory for all configuration files
    ├── vscode.yml         # Example: VS Code configuration YAML
    ├── iterm2_config.yml  # Example: iTerm2 configuration YAML
    ├── com.googlecode.iterm2.plist # Auxiliary file for iTerm2
    ├── trackpad_settings.yml # Example: System configuration YAML
    ├── development/       # Optional: User-defined subdirectory for organization
    │   ├── docker.yml
    │   └── node.yml
    ├── productivity/      # Optional: User-defined subdirectory for organization
    │   └── raycast.yml
    └── ...                # Other .yml or auxiliary files
```

**Note**: The `configs/` directory can contain user-defined subdirectories for better file organization. However, **the physical directory structure does not determine how items are grouped in the user interface**. Menu categorization is based solely on the `category` field within each YAML file.

### 2.3 Execution Flow

1. **Bootstrap Phase**: `setup.sh` is executed first to:

   - Install Homebrew (core requirement)
   - Set up Python virtual environment
   - Install Python dependencies from `requirements.txt`

2. **Main Application**: `macsnap.py` is launched, which:
   - Loads and validates YAML configurations from `configs/`
   - Presents interactive menus for software selection
   - Executes installation and configuration scripts
   - Provides logging and error handling

### 2.4 Scripting Environment

- All scripts defined within YAML configurations (`install`, `validate`, `configure`, `uninstall`) will be executed as shell scripts from within the Python application.
- An environment variable `ITEM_CONFIG_DIR` will be injected into each script's execution context, containing the absolute path to the `configs/` directory.
- Scripts can use this variable to access any YAML or auxiliary files located within the `configs/` directory (e.g., `cp "${ITEM_CONFIG_DIR}/some_aux_file.plist" /path/to/destination`).

## 3. Configuration File Format (YAML)

Each installable item or system configuration is defined in its own YAML file (e.g., `vscode.yml`).

### 3.1 Key Fields:

- `id` (string, required): Unique identifier (e.g., "vscode", "trackpad-settings").
- `name` (string, required): User-friendly display name (e.g., "Visual Studio Code", "Trackpad Settings").
- `description` (string, optional): Brief description of the item.
- `type` (string, required): Defines the installation/configuration handler to use.
  - Supported types:
    - `brew`: For Homebrew formulae.
    - `brew_cask`: For Homebrew Casks (GUI applications).
    - `mas`: For Mac App Store apps (requires user to be signed into App Store).
    - `direct_download_dmg`: For apps distributed as `.dmg` files.
    - `direct_download_pkg`: For apps distributed via `.pkg` installers.
    - `proto_tool`: For tools managed by `proto` (e.g., Node.js, npm).
    - `system_config`: For applying system settings using `defaults` commands.
    - `launch_agent`: For setting up and managing custom Launch Agents.
    - `shell_script`: For generic shell scripts that don't fit other types.
- `category` (string, required): Groups the item in the UI (e.g., "Core Utilities", "Development", "System Tweaks", "Browsers").
- `selected_by_default` (boolean, optional, default: `false`): If `true`, this item will be pre-selected in the interface.
- `dependencies` (list of strings, optional): A list of `id`s of other items that must be successfully processed before this item.
- `install` (object, optional):
  - `script` (string, required): Shell script to perform the installation.
- `validate` (object, optional):
  - `script` (string, required): Shell script to check if the item is already installed/configured. Should exit with `0` if validation passes, non-zero otherwise.
- `configure` (object, optional):
  - `script` (string, required): Shell script for post-installation configuration.
- `uninstall` (object, optional):
  - `script` (string, required): Shell script to uninstall the item.

### 3.2 Example: Software Installation (`vscode.yml`)

```yaml
id: "vscode"
name: "Visual Studio Code"
description: "Free source-code editor made by Microsoft"
type: "brew_cask"
category: "Development"
selected_by_default: false
install:
  script: |
    echo "Installing Visual Studio Code..."
    brew install --cask visual-studio-code
validate:
  script: |
    brew list --cask | grep -q "visual-studio-code" || ls /Applications/ | grep -q "Visual Studio Code.app"
configure:
  script: |
    echo "Configuring Visual Studio Code..."
    # Install the 'code' command in PATH if available
    if command -v code &> /dev/null; then
      echo "VS Code 'code' command is available"
    else
      echo "You may need to install 'code' command from VS Code Command Palette"
    fi
```

### 3.3 Example: System Configuration (`trackpad_settings.yml`)

```yaml
id: "trackpad_settings"
name: "Trackpad Settings"
description: "Configure trackpad with tap to click and other improvements"
type: "system_config"
category: "System Tweaks"
selected_by_default: true
install:
  script: |
    echo "This item only configures existing system settings"
validate:
  script: |
    # Always return 1 (not configured) so configure script runs
    exit 1
configure:
  script: |
    echo "Applying trackpad settings..."
    # Enable tap to click
    defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true
    defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true
    defaults -currentHost write NSGlobalDomain com.apple.mouse.tapBehavior -int 1
    defaults write NSGlobalDomain com.apple.mouse.tapBehavior -int 1
    echo "Trackpad settings applied successfully"
```

## 4. User Interface (UI) Design

### 4.1 Python CLI Interface

- **Two-Column Layout**: Left sidebar for category navigation, main content area for item selection.
- **Interactive Navigation**: Real-time description display when browsing options.
- **Progress Feedback**: Real-time feedback during installation and configuration processes.
- **Error Handling**: Clear error messages and recovery suggestions.
- **Logging Options**: Optional verbose output with `--verbose` flag.

### 4.2 Main UI Layout

The interface uses a two-column design:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MacSnap Setup v1.0                          │
│                 macOS 15.4.1 | User: john                      │
├──────────────────┬──────────────────────────────────────────────┤
│   Categories     │               Selected Category              │
│                  │                                              │
│ > Core Utilities │  ┌─ Visual Studio Code ──────────────────┐   │
│   Development    │  │ Free source-code editor made by       │   │
│   Productivity   │  │ Microsoft for Windows, Linux and      │   │
│   Browsers       │  │ macOS. It includes support for        │   │
│   System Tweaks  │  │ debugging, Git control, syntax        │   │
│   Media          │  │ highlighting, intelligent code         │   │
│                  │  │ completion, snippets, and code         │   │
│                  │  │ refactoring.                           │   │
│                  │  └─ [✓] Install [Configure] [Details] ───┘   │
│                  │                                              │
│                  │  ┌─ Docker Desktop ──────────────────────┐   │
│                  │  │ Containerization platform for         │   │
│                  │  │ developers...                          │   │
│                  │  └─ [ ] Install [Configure] [Details] ───┘   │
│                  │                                              │
└──────────────────┴──────────────────────────────────────────────┘
```

### 4.3 UI Components

1.  **Header Section**: Application banner, system information (macOS version, username), current operation status.

2.  **Left Sidebar (Categories Panel)**:

    - Displays all available categories derived from YAML `category` fields
    - Allows navigation between categories
    - Shows selection indicator for current category
    - Categories are sorted alphabetically

3.  **Main Content Area (Items Panel)**:

    - Displays all items within the selected category
    - Shows item name, description, and status for each option
    - Provides real-time description viewing when navigating through items
    - Status indicators: installed (✓), not installed ( ), failed (✗), pending (⏳)
    - Multi-select capability for batch operations
    - Action buttons: Install, Configure, Uninstall, Details

4.  **Description Display**:

    - Dynamic description text that updates as user navigates through items
    - Shows full item description from YAML files
    - Displays dependencies and requirements

5.  **Installation Progress Screen**:

    - Full-screen overlay during operations
    - Progress indicators and real-time script output
    - Clear error messages and visual indicators for failures

6.  **Summary Screen**:
    - Post-operation summary with success/failure counts
    - List of problematic items with details
    - Options for viewing logs or performing additional actions

## 5. Core Functions and Logic

### 5.1 Configuration Management (`utils/config_loader.py`, `utils/validators.py`)

- `load_configurations()`: Recursively scans the entire `configs/` directory and all subdirectories for `*.yml` files, parses them using Python YAML parser, and builds configuration objects. The physical directory structure is used only for file organization and does not affect UI categorization.
- `validate_configurations()`: Checks YAMLs for schema compliance, valid `type` values, and presence of required script blocks.
- **Dependency Resolution**: Builds and resolves dependencies listed in YAML files.
- **Category Extraction**: Extracts unique categories from all YAML files based on the `category` field for UI organization.

### 5.2 Installation Engine (`utils/installer.py`)

- `check_install_status()`: Executes `validate` script for an item.
- `install_item()`: Executes `install` script for an item.
- `configure_item()`: Executes `configure` script for an item.
- `uninstall_item()`: Executes `uninstall` script for an item.
- `batch_process()`: Orchestrates processing of selected items, handles dependencies, manages error flow.

### 5.3 Logging System (`utils/logger.py`)

- Configurable logging levels (INFO, DEBUG, ERROR).
- Optional verbose mode activated with `--verbose` parameter.
- File-based logging to `~/Library/Logs/MacSnap/setup.log`.
- Console output formatting and progress indication.

### 5.4 User Interface (`utils/ui.py`)

- **Two-Column Layout Management**: Handles the left sidebar (categories) and main content area (items) layout.
- **Category Navigation**: Manages category selection and switching between different software categories.
- **Item Display and Selection**: Renders items within selected categories with descriptions, status indicators, and action buttons.
- **Real-time Description Updates**: Updates item descriptions dynamically as users navigate through options.
- **Multi-Selection Support**: Allows users to select multiple items for batch operations.
- **Progress Indication**: Real-time progress feedback during installation and configuration processes.
- **Error Handling**: Clear error message formatting and display with recovery suggestions.
- **User Input Validation**: Handles user input validation and confirmation prompts.

## 6. Implementation Details for Handlers

Specific logic for each `type` in YAML configurations:

1.  **`brew`, `brew_cask`**: Scripts use `brew install/uninstall/list` commands.
2.  **`mas`**: Scripts use `mas install/list`. User must be signed into App Store.
3.  **`direct_download_dmg`**: Scripts download DMG files, mount them, copy applications, and clean up.
4.  **`direct_download_pkg`**: Scripts download and install PKG files using `installer` command.
5.  **`proto_tool`**: Scripts use `proto install <tool>` and related commands.
6.  **`system_config`**: Scripts primarily use `defaults write/read/delete` commands.
7.  **`launch_agent`**: Scripts manage `.plist` files in `~/Library/LaunchAgents` using `launchctl`.
8.  **`shell_script`**: Generic shell script execution with environment variable injection.

## 7. Technical Requirements

- **Python 3.8+**: Core runtime environment
- **macOS 15.4.1+**: Target operating system
- **Homebrew**: Installed automatically by `setup.sh` as a core requirement
- **Internet Connection**: Required for downloading software and packages

**Note**: Homebrew is not included in the YAML configurations as it is a core requirement of the application and is installed directly by the `setup.sh` bootstrap script.

## 8. Usage

### 8.1 Initial Setup

```bash
# Clone or download MacSnap Setup
cd macsnap-setup

# Run the bootstrap script (installs Homebrew and sets up Python environment)
./setup.sh

# The setup script will automatically launch macsnap.py after setup
```

### 8.2 Running MacSnap

```bash
# Normal execution
python macsnap.py

# With verbose logging
python macsnap.py --verbose
```

## 9. Implementation Plan & Checklist

### Phase 0: Project Foundation & Setup ✅

- [x] **Project Structure**: Create root directory structure with proper organization
- [x] **Documentation**: Create comprehensive README with architecture and specifications
- [x] **Bootstrap Script**: `setup.sh` for Homebrew installation and Python environment setup
- [x] **Python Dependencies**: `requirements.txt` with necessary packages
- [x] **Initial Files**: Basic `macsnap.py` entry point created

### Phase 1: Core Python Modules Development

#### 1.1 Configuration System (`utils/config_loader.py`) ✅

- [x] **File Discovery**: Implement recursive scanning of `configs/` directory for `*.yml` files
- [x] **YAML Parsing**: Parse YAML files and build configuration objects
- [x] **Category Extraction**: Extract unique categories from `category` fields across all YAML files
- [x] **Environment Variables**: Set up `ITEM_CONFIG_DIR` injection for scripts
- [x] **Error Handling**: Handle malformed YAML files and missing dependencies

#### 1.2 Configuration Validation (`utils/validators.py`) ✅

- [x] **Schema Validation**: Validate YAML structure and required fields (`id`, `name`, `type`, `category`)
- [x] **Type Validation**: Ensure `type` field contains valid values (`brew`, `brew_cask`, `mas`, etc.)
- [x] **Script Validation**: Check presence of required script blocks based on item type
- [x] **Dependency Validation**: Validate that all dependencies reference existing item IDs
- [x] **Circular Dependency Detection**: Prevent circular dependency chains

#### 1.3 Installation Engine (`utils/installer.py`) ✅

- [x] **Script Execution**: Execute shell scripts from YAML with proper environment setup
- [x] **Dependency Resolution**: Build and resolve dependency graphs for correct installation order
- [x] **Installation Functions**:
  - [x] `check_install_status()` - Execute `validate` scripts
  - [x] `install_item()` - Execute `install` scripts
  - [x] `configure_item()` - Execute `configure` scripts
  - [x] `uninstall_item()` - Execute `uninstall` scripts
- [x] **Batch Processing**: Handle multiple item selection and batch operations
- [x] **Error Handling**: Continue on non-critical failures, halt dependents on critical failures
- [x] **Type Handlers**: Implement specific logic for each installation type

#### 1.4 Logging System (`utils/logger.py`) ✅

- [x] **Log Levels**: Implement INFO, DEBUG, ERROR logging levels
- [x] **Verbose Mode**: Support `--verbose` command line parameter
- [x] **File Logging**: Write logs to `~/Library/Logs/MacSnap/setup.log`
- [x] **Console Output**: Formatted console output with progress indication
- [x] **Script Output Capture**: Capture and log stdout/stderr from executed scripts

#### 1.5 User Interface (`utils/ui.py`) ✅

- [x] **Two-Column Layout**: Implement left sidebar (categories) and main content area (items)
- [x] **Category Navigation**:
  - [x] Display categories alphabetically
  - [x] Handle category selection and switching
  - [x] Show current selection indicator
- [x] **Item Display**:
  - [x] List items within selected category
  - [x] Show status indicators (✓, ✗, ⏳, etc.)
  - [x] Display item names and descriptions
  - [x] Real-time description updates during navigation
- [x] **Multi-Selection**: Allow selecting multiple items for batch operations
- [x] **Action Buttons**: Install, Configure, Uninstall, Details buttons
- [x] **Progress Display**: Full-screen overlay for installation progress
- [x] **Error Display**: Clear error messages with recovery suggestions

### Phase 2: Main Application Development

#### 2.1 Main Application (`macsnap.py`) ✅

- [x] **Command Line Arguments**: Parse `--verbose` and other command line options
- [x] **Application Initialization**: Set up logging, load configurations, validate setup
- [x] **Main Loop**: Implement main user interface loop with category/item navigation
- [x] **Event Handling**: Handle user input for navigation, selection, and actions
- [x] **Installation Orchestration**: Coordinate between UI, installer, and logger
- [x] **Graceful Exit**: Handle Ctrl+C and other exit conditions properly

### Phase 3: Configuration Files Population

#### 3.1 Core Utilities

- [x] **mas-cli**: Mac App Store CLI configuration
- [ ] **yq**: YAML processor for potential script use
- [ ] **git**: Git configuration and setup

#### 3.2 Development Tools

- [x] **Visual Studio Code**: Code editor with extensions
- [x] **Docker Desktop**: Containerization platform
- [ ] **Node.js**: JavaScript runtime (via brew or proto)
- [ ] **Python Tools**: pip, pipenv, poetry configurations
- [ ] **Oh My Zsh**: Shell enhancement framework
- [ ] **Git Tools**: GitHub CLI, Git GUI tools

#### 3.3 Productivity Applications

- [x] **Raycast**: Launcher and productivity tool
- [ ] **Alfred**: Alternative launcher (if user prefers)
- [ ] **1Password**: Password manager
- [ ] **Notion**: Note-taking and productivity
- [ ] **Slack**: Team communication
- [ ] **Zoom**: Video conferencing

#### 3.4 Browsers

- [x] **Google Chrome**: Primary browser
- [ ] **Firefox**: Alternative browser
- [ ] **Safari Extensions**: Safari-specific enhancements
- [ ] **Arc**: Modern browser alternative

#### 3.5 Media & Communication

- [ ] **Spotify**: Music streaming
- [ ] **VLC**: Media player
- [ ] **Telegram**: Messaging app
- [ ] **Discord**: Gaming/community chat
- [ ] **WhatsApp**: Messaging app

#### 3.6 System Tweaks

- [x] **Trackpad Settings**: Tap to click and sensitivity
- [x] **Dock Settings**: Auto-hide, size, position
- [ ] **Keyboard Settings**: Repeat rate, modifier keys
- [ ] **Finder Settings**: Show hidden files, default view
- [ ] **Menu Bar**: Hide/show items, organization
- [ ] **Security Settings**: Firewall, privacy configurations

### Phase 4: Advanced Features

#### 4.1 Installation Types Implementation

- [ ] **brew**: Homebrew formula installation
- [ ] **brew_cask**: Homebrew cask (GUI app) installation
- [ ] **mas**: Mac App Store app installation
- [ ] **direct_download_dmg**: DMG download and installation
- [ ] **direct_download_pkg**: PKG download and installation
- [ ] **proto_tool**: Proto tool manager integration
- [ ] **system_config**: macOS defaults configuration
- [ ] **launch_agent**: Launch agent setup and management
- [ ] **shell_script**: Generic shell script execution

#### 4.2 Advanced UI Features

- [ ] **Search/Filter**: Search within categories and across all items
- [ ] **Favorites**: Mark frequently used items as favorites
- [ ] **Installation History**: Track and display installation history
- [ ] **Update Notifications**: Check for updates to installed applications
- [ ] **Backup/Restore**: Export/import configuration selections

### Phase 5: Testing & Quality Assurance

#### 5.1 Unit Testing

- [ ] **Configuration Loading**: Test YAML parsing and validation
- [ ] **Dependency Resolution**: Test dependency graph building and resolution
- [ ] **Script Execution**: Test script execution with mocked commands
- [ ] **UI Components**: Test individual UI components and navigation
- [ ] **Error Handling**: Test error conditions and recovery

#### 5.2 Integration Testing

- [ ] **End-to-End Flows**: Test complete installation workflows
- [ ] **Type Handler Testing**: Test each installation type with real/mock environments
- [ ] **Dependency Chain Testing**: Test complex dependency scenarios
- [ ] **UI Integration**: Test complete UI navigation and selection workflows

#### 5.3 System Testing

- [ ] **Clean macOS Testing**: Test on fresh macOS installation (VM recommended)
- [ ] **Permission Handling**: Test sudo prompts and permission requirements
- [ ] **Error Recovery**: Test recovery from failed installations
- [ ] **Performance Testing**: Test with large numbers of configuration files

### Phase 6: Documentation & Distribution

#### 6.1 User Documentation

- [ ] **Installation Guide**: Step-by-step setup instructions
- [ ] **Usage Guide**: How to navigate and use the interface
- [ ] **Troubleshooting Guide**: Common issues and solutions
- [ ] **Configuration Guide**: How to add custom software configurations

#### 6.2 Developer Documentation

- [ ] **Architecture Documentation**: Code organization and design patterns
- [ ] **API Documentation**: Function and class documentation
- [ ] **Configuration Schema**: YAML configuration format specification
- [ ] **Contributing Guide**: Guidelines for adding new configurations

#### 6.3 Distribution Preparation

- [ ] **Setup Script Refinement**: Polish `setup.sh` for reliable execution
- [ ] **Packaging**: Create distribution package or installer
- [ ] **Version Management**: Implement version checking and updates
- [ ] **Release Notes**: Document features and changes

### Phase 7: Enhancement & Maintenance

#### 7.1 Community Features

- [ ] **Configuration Sharing**: Allow users to share configuration files
- [ ] **Online Repository**: Central repository for community configurations
- [ ] **Update Mechanism**: Automatic updates for configurations and app

#### 7.2 Advanced Features

- [ ] **Profile Management**: Multiple configuration profiles (work, personal, etc.)
- [ ] **Scheduled Operations**: Schedule installations or updates
- [ ] **Notification System**: Native macOS notifications for completed operations
- [ ] **Analytics**: Optional usage analytics and improvement suggestions

---

**Current Status**: Phase 0 Complete ✅ | **Phase 1 Complete ✅** | **Phase 2 Complete ✅**

**Next Priority**: Begin Phase 3 - Configuration Files Population (or test the complete application).

git configs
git config --global pull.rebase true
git config --global rebase.autoStash true

some other nice mac apps
https://www.youtube.com/watch?v=D2_8qJi2jpQ
