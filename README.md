# MacSnap Setup - Technical Design Document (Revised)

## 1. System Overview

**MacSnap Setup** is an interactive terminal application designed to automate the installation and configuration of macOS systems (version 15.4.1 and up). Built with Gum (a tool for glamorous shell scripts), it provides a user-friendly interface for managing software installation and system customization. The tool is designed to be re-runnable, allowing users to install new items without affecting already installed software.

## 2. Architecture

### 2.1 Core Components

1.  **Command Line Interface (CLI)**

    - Gum-based UI.
    - Interactive selection menus for categories and items.
    - Animated progress indicators and real-time feedback.

2.  **Configuration System**

    - YAML configuration files for all installable software, system settings, and custom scripts.
    - Each item is defined in its own YAML file within a structured directory.
    - Support for dependencies to ensure correct installation order.
    - Categorization of items (e.g., essentials, development, shells) within YAML files for UI grouping.

3.  **Installation Engine**

    - Parses YAML configurations and executes associated Zsh scripts.
    - Validates existing installations to avoid redundant operations.
    - Handles various installation types through specific handlers.
    - Manages error handling: continues on non-critical failures, halts dependent items if a critical dependency fails.
    - Provides detailed logging for debugging.

4.  **System Configuration Engine**

    - Applies system settings via `defaults` commands and other macOS mechanisms.
    - Manages settings for trackpad, keyboard (including a custom `hidutil`-based remapping agent), dock, and accessibility.
    - Guides users through necessary permission grants.

5.  **Logging System**
    - Comprehensive logging of all operations, script outputs (stdout/stderr), and errors to a user-accessible file (e.g., `~/Library/Logs/MacSnap/setup.log`).

### 2.2 Directory Structure

The project files (`macsnap.sh`, `utils/`, `configs/`) are located at the root of the workspace:

```
./
├── macsnap.sh              # Main executable shell script
├── utils/                  # Directory for utility shell scripts used by macsnap.sh
└── configs/                # Root directory for all configuration and script files
    ├── homebrew_setup.yml  # Example: Homebrew setup YAML configuration
    ├── iterm2_config.yml   # Example: iTerm2 configuration YAML
    ├── com.googlecode.iterm2.plist # Auxiliary file for iTerm2
    ├── keyboard_fix.sh     # Example: A shell script for keyboard fixes
    ├── custom-keyboard-map.plist # Auxiliary file for keyboard_fix.sh
    └── ...                 # Other .yml, .sh, or auxiliary files
```

### 2.3 Scripting Environment

- All scripts defined within YAML configurations (`install`, `validate`, `configure`, `uninstall`) or standalone `.sh` files in the `configs/` directory will be executed as **Zsh scripts**.
- An environment variable `ITEM_CONFIG_DIR` will be injected into each script's execution context. This variable will contain the absolute path to the `configs/` directory (e.g., if the workspace root is `/Users/name/projects/osx-setup`, then `ITEM_CONFIG_DIR` would be `/Users/name/projects/osx-setup/configs/`). Scripts can use this variable to access any YAML, SH, or auxiliary files located directly within the `configs/` directory (e.g., `cp "${ITEM_CONFIG_DIR}/some_aux_file.plist" /path/to/destination`).

## 3. Configuration File Format (YAML)

Each installable item or system configuration is defined in its own YAML file (e.g., `iterm2.yaml`).

### 3.1 Key Fields:

- `id` (string, required): Unique identifier (e.g., "iterm2", "trackpad-settings").
- `name` (string, required): User-friendly display name (e.g., "iTerm2", "Trackpad Settings").
- `description` (string, optional): Brief description of the item.
- `type` (string, required): Defines the installation/configuration handler to use.
  - Supported types:
    - `brew`: For Homebrew formulae.
    - `brew_cask`: For Homebrew Casks (GUI applications).
    - `mas`: For Mac App Store apps (requires user to be signed into App Store).
    - `direct_download_dmg`: For apps distributed as `.dmg` files (involves mounting, copying `.app`).
    - `direct_download_pkg`: For apps distributed via `.pkg` installers.
    - `proto_tool`: For tools managed by `proto` (e.g., Node.js, npm).
    - `system_config`: For applying system settings using `defaults` commands.
    - `launch_agent`: For setting up and managing custom Launch Agents (e.g., for `hidutil` keyboard remapping).
    - `shell_script`: For generic Zsh scripts that don't fit other types.
- `category` (string, required): Groups the item in the UI (e.g., "Essentials", "Development Tools", "System Tweaks", "Browsers"). This field is for UI presentation and is independent of the `configs/` subdirectory the YAML resides in.
- `required` (boolean, optional, default: `false`): If `true`, this item might be a critical dependency. Items in `configs/init/` are typically implicitly required or ordered.
- `dependencies` (list of strings, optional): A list of `id`s of other items that must be successfully processed before this item.
- `install` (object, optional):
  - `script` (string, required): Zsh script to perform the installation.
- `validate` (object, optional):
  - `script` (string, required): Zsh script to check if the item is already installed/configured. Should exit with `0` if validation passes (item is present/configured), non-zero otherwise.
- `configure` (object, optional):
  - `script` (string, required): Zsh script for post-installation configuration.
- `uninstall` (object, optional):
  - `script` (string, required): Zsh script to uninstall the item.

### 3.2 Example: Software Installation (`iterm2.yaml`)

Located at `configs/apps/iterm2/iterm2.yaml`:

```yaml
id: "iterm2"
name: "iTerm2"
description: "A replacement for Terminal and the successor to iTerm."
type: "brew_cask"
category: "Terminal" # UI Grouping
dependencies:
  - "brew" # Assumes a brew.yaml exists with id: "brew", likely in configs/init/
install:
  script: |
    echo "Installing iTerm2..."
    brew install --cask iterm2
validate:
  script: |
    brew list --cask | grep -q "^iterm2$"
configure:
  script: |
    echo "Configuring iTerm2 preferences..."
    # ITEM_CONFIG_DIR will point to configs/apps/iterm2/
    cp "${ITEM_CONFIG_DIR}/com.googlecode.iterm2.plist" "${HOME}/Library/Preferences/com.googlecode.iterm2.plist"
uninstall:
  script: |
    echo "Uninstalling iTerm2..."
    brew uninstall --cask iterm2
```

Auxiliary file `configs/apps/iterm2/com.googlecode.iterm2.plist` would contain the iTerm2 preferences.

### 3.3 Example: System Configuration (`trackpad-settings.yaml`)

Located at `configs/system/trackpad-settings/trackpad-settings.yaml`:

```yaml
id: "trackpad-settings"
name: "Trackpad Settings"
description: "Configure trackpad with tap to click."
type: "system_config"
category: "System Tweaks" # UI Grouping
configure:
  script: |
    echo "Applying trackpad settings..."
    defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true
    defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true
    defaults -currentHost write NSGlobalDomain com.apple.mouse.tapBehavior -int 1
    defaults write NSGlobalDomain com.apple.mouse.tapBehavior -int 1
validate:
  script: |
    defaults read com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking | grep -q "1"

# uninstall script could revert settings if desired
```

### 3.4 Example: Keyboard Remapping Agent (`keyboard-fix.yaml`)

Located at `configs/system/keyboard-fix/keyboard-fix.yaml`:

```yaml
id: "keyboard-fix"
name: "Custom Keyboard Remapping"
description: "Applies custom keyboard remappings using hidutil via a Launch Agent."
type: "launch_agent"
category: "System Tweaks" # UI Grouping
install:
  script: |
    PLIST_NAME="com.user.keyboardremap.plist"
    PLIST_TARGET_DIR="${HOME}/Library/LaunchAgents"
    PLIST_TARGET_PATH="${PLIST_TARGET_DIR}/${PLIST_NAME}"

    echo "Installing keyboard remapping Launch Agent..."
    # ITEM_CONFIG_DIR points to configs/system/keyboard-fix/
    # Assume custom-keyboard-map.plist in ITEM_CONFIG_DIR defines the hidutil commands
    cp "${ITEM_CONFIG_DIR}/custom-keyboard-map.plist" "${PLIST_TARGET_PATH}"
    launchctl load "${PLIST_TARGET_PATH}"
validate:
  script: |
    launchctl list | grep -q "com.user.keyboardremap"
uninstall:
  script: |
    PLIST_NAME="com.user.keyboardremap.plist"
    PLIST_TARGET_PATH="${HOME}/Library/LaunchAgents/${PLIST_NAME}"
    echo "Uninstalling keyboard remapping Launch Agent..."
    launchctl unload "${PLIST_TARGET_PATH}"
    rm -f "${PLIST_TARGET_PATH}"
```

An auxiliary file like `configs/system/keyboard-fix/custom-keyboard-map.plist` would contain the actual Launch Agent definition invoking `hidutil`.

## 4. User Interface (UI) Design

### 4.1 Cyberpunk Theme Elements

- **Color Palette**: Primary: Electric blue (`#00FFFF`), Secondary: Neon pink (`#FF00FF`), Accent: Neon green (`#00FF00`), Background: Dark with grid patterns, Text: High contrast with glow effects. (Note: Gum styling might be more limited than Ink, adapt as needed)
- **Typography**: Monospace fonts (e.g., "Hack", "Fira Code"). (Note: Gum uses terminal's font)
- **Animations**: Gum offers some styling but complex animations like "Matrix-like" data flow might be simplified or omitted.

### 4.2 Main UI Components

1.  **Header Component**: ASCII art logo, system information (macOS version, username), current operation status.
2.  **Main Menu Screen**: Categories (derived from YAML `category` field) displayed in a grid or selectable list. Cyberpunk-styled selection indicators. Status summary (installed/pending/total).
3.  **Category View Screen**: List of installable items within a selected UI category, status indicators (installed, pending, failed), multi-select capability, dependency highlighting.
4.  **Installation Progress Screen**: Animated progress bars, real-time Zsh script output from installations/configurations, clear error messages and visual indicators for failures.
5.  **Summary Screen**: Post-operation summary with success/failure counts, list of problematic items, options for viewing logs or next steps.

## 5. Core Functions and Logic

### 5.1 Configuration Management (`config-loader.sh`, `validator.sh`)

- `loadConfigurations(baseConfigDir)`: Recursively scans `configs/init/`, `configs/apps/`, and `configs/system/` for `*.yaml` files within their respective item subdirectories. Parses them (using a shell YAML parser like `yq`) and builds an in-memory representation (e.g., associative arrays), storing `ITEM_CONFIG_DIR` for each.
- `validateConfigurations(configs)`: Checks YAMLs for schema compliance, valid `type` values, and presence of required script blocks.
- Dependency Graph: Builds and resolves dependencies listed in YAML files.

### 5.2 Installation Engine (`engine.sh`)

- `checkInstallStatus(config, itemConfigDir)`: Executes `validate` script.
- `installItem(config, itemConfigDir)`: Executes `install` script.
- `configureItem(config, itemConfigDir)`: Executes `configure` script.
- `uninstallItem(config, itemConfigDir)`: Executes `uninstall` script.
- `batchProcess(selectedItems, operationType)`:
  - Determines correct order based on dependencies (items in `configs/init/` might have implicit ordering or be processed first).
  - For each item, calls the relevant function (`installItem`, `uninstallItem`, etc.).
  - Handles error logic: logs errors, continues if non-critical, skips dependents on critical failures.
  - Updates UI (using Gum commands for feedback) with progress and status.

### 5.3 System Configuration (`system-config.sh`)

- Provides helper functions or manages more complex system configuration tasks if needed beyond simple script execution by `engine.sh`.
- Specifically handles the logic for `type: "launch_agent"` for keyboard remapping via `hidutil`.

### 5.4 Shell Execution (`utils/shell.sh` or integrated into `engine.sh`)

- Provides a robust function to execute Zsh scripts, capture stdout/stderr, exit codes, and stream output to the UI (via Gum) and logger.
- Injects `ITEM_CONFIG_DIR` environment variable.

### 5.5 Permissions and Sudo (`utils/permissions.sh`)

- MacSnap Setup itself will not require `sudo` to run.
- Individual Zsh scripts within YAMLs that need elevated privileges must include `sudo` in their commands (e.g., `sudo brew install ...`). macOS will handle the `sudo` prompt.
- The application may guide users to manually grant permissions if required (e.g., Accessibility for certain `defaults` commands or Full Disk Access for broad file operations, though the latter should be minimized).

## 6. Implementation Details for Handlers

Specific logic for each `type` in YAML:

1.  **`brew`, `brew_cask`**: Scripts will use `brew install/uninstall/list` commands.
2.  **`mas`**: Scripts use `mas install/list`. User must be signed into App Store. Failures due to this will be logged.
3.  **`direct_download_dmg`**: Scripts will `curl` the DMG, `hdiutil attach`, `cp -R` the `.app` bundle, `hdiutil detach`, and clean up.
4.  **`direct_download_pkg`**: Scripts will `curl` the PKG and use `sudo installer -pkg ... -target /`.
5.  **`proto_tool`**: Scripts use `proto install <tool>`, `proto run <tool> -- <command>`.
6.  **`system_config`**: Scripts primarily use `defaults write/read/delete` commands.
7.  **`launch_agent`**: `install` script copies/creates a `.plist` in `~/Library/LaunchAgents` (using `ITEM_CONFIG_DIR` for templates) and loads it with `launchctl load`. `uninstall` script uses `launchctl unload` and removes the plist.
8.  **`shell_script`**: Generic Zsh script execution.

## 7. Specific Software Installation List (Examples)

(Items will be placed in `configs/init/`, `configs/apps/`, or `configs/system/` subdirectories as appropriate. The `category` field in YAML will drive UI grouping.)

### 7.1 Initial Setup (`configs/init/`)

- Homebrew (`brew/brew.yaml`, type: `shell_script` for initial install, `category: "Core Utilities"`)
- Mac App Store CLI (`mas-cli/mas-cli.yaml`, type: `brew`, depends on "brew", `category: "Core Utilities"`)
- Proto version manager (`proto/proto.yaml`, type: `brew`, depends on "brew", `category: "Development"`)

### 7.2 Applications (`configs/apps/`)

- iTerm2 (`iterm2/iterm2.yaml`, type: `brew_cask`, `category: "Terminal"`)
- Node.js (`node/node.yaml`, type: `proto_tool`, depends on "proto", `category: "Development"`)
- npm, yarn, pnpm, uv (similar `proto_tool` types, `category: "Development"`)
- Docker (`docker/docker.yaml`, type: `brew_cask`, `category: "Development"`)
- Visual Studio Code (`vscode/vscode.yaml`, type: `brew_cask`, `category: "Development"`)
- Oh My Posh (`oh-my-posh/oh-my-posh.yaml`, type: `brew`, `category: "Shell Enhancement"`)
- Antidote (`antidote/antidote.yaml`, type: `brew` or `shell_script`, `category: "Shell Enhancement"`)
- Warp Terminal (`warp/warp.yaml`, type: `brew_cask`, `category: "Terminal"`)
- Raycast (`raycast/raycast.yaml`, type: `brew_cask`, `category: "Productivity"`)
- CleanShot X (`cleanshotx/cleanshotx.yaml`, type: `mas` or `brew_cask`, `category: "Productivity"`)
- Google Chrome (`chrome/chrome.yaml`, type: `brew_cask`, `category: "Browsers"`)
- Spotify (`spotify/spotify.yaml`, type: `brew_cask`, `category: "Media"`)
- VLC (`vlc/vlc.yaml`, type: `brew_cask`, `category: "Media"`)
- Telegram (`telegram/telegram.yaml`, type: `brew_cask` or `mas`, `category: "Communication"`)
- ChatGPT Desktop (`chatgpt-desktop/chatgpt-desktop.yaml`, type: `brew_cask` or `direct_download_dmg`, `category: "AI Tools"`)
- Claude Desktop (`claude-desktop/claude-desktop.yaml`, type: `brew_cask` or `direct_download_dmg`, `category: "AI Tools"`)
- Synthesia (`synthesia/synthesia.yaml`, type: `direct_download_dmg` or `brew_cask`, `category: "Media"`)

### 7.3 System Configurations (`configs/system/`)

- Trackpad: Tap to click (`trackpad-tap-click/trackpad-tap-click.yaml`, type: `system_config`, `category: "System Tweaks"`)
- Dock: Auto-hide, size (`dock-settings/dock-settings.yaml`, type: `system_config`, `category: "System Tweaks"`)
- Keyboard: Repeat rate (`keyboard-repeat/keyboard-repeat.yaml`, type: `system_config`, `category: "System Tweaks"`)
- Custom keyboard remapping agent (`keyboard-fix/keyboard-fix.yaml`, type: `launch_agent` using `hidutil`, `category: "System Tweaks"`)

## 8. Technical Requirements

- Node.js 18+
- Gum framework (for terminal UI)
- `yaml` library (for parsing configuration files)
- macOS 15.4.1 or newer
- User must have privileges to run `sudo` for commands that require it within scripts.

## 9. Implementation Plan & Checklist

Here is the phased plan for developing MacSnap Setup:

### Phase 0: Project Initialization & Core Setup

- [x] **Set up Project Files:** Ensure `macsnap.sh`, `utils/`, and `configs/` are at the workspace root.
- [x] **Initialize Shell Script Project:** (No equivalent to `pnpm init`, main script `macsnap.sh` will be created)
- [x] **Install Core Dependencies:** Install `gum`, `yq` (for YAML parsing).
- [x] **Establish Directory Structure:** Create the `utils/` and `configs/` directories at the workspace root as specified in section 2.2.
- [/] **Create Main Executable:** Develop the `macsnap.sh` main shell script entry point at the workspace root.

### Phase 1: Configuration System Development

- [ ] **`config-loader.sh` - Load Configurations:**
  - [ ] Implement `loadConfigurations(baseConfigDir)` to recursively find and parse `*.yaml` files from `configs/init/`, `configs/apps/`, and `configs/system/` item subdirectories using `yq`.
  - [ ] Store the path to each item's specific directory to be passed as `ITEM_CONFIG_DIR` to scripts.
- [ ] **`validator.sh` - Validate YAML Structure:**
  - [ ] Implement `validateConfigurations(configs)` to check for correct YAML format, required fields, and defined `type` values.
  - [ ] Ensure all defined `type` values are recognized: `brew`, `brew_cask`, `mas`, `direct_download_dmg`, `direct_download_pkg`, `proto_tool`, `system_config`, `launch_agent`, `shell_script`.
- [ ] **Dependency Resolution:** Implement logic in shell script to build a dependency graph and determine correct processing order.

### Phase 2: Core Engine Development (`engine.sh`)

- [ ] **Script Execution Functions:**
  - [ ] `checkInstallStatus(config, itemConfigDir)`: Execute `validate` script.
  - [ ] `installItem(config, itemConfigDir)`: Execute `install` script.
  - [ ] `configureItem(config, itemConfigDir)`: Execute `configure` script.
  - [ ] `uninstallItem(config, itemConfigDir)`: Execute `uninstall` script.
- [ ] **`batchProcess(selectedItems, operationType)`:** Orchestrate item processing, handle dependencies, manage error flow (continue/halt dependents), and pass `ITEM_CONFIG_DIR`.

### Phase 3: UI Development (Gum commands - `src/cli/`)

- [ ] **Styling (`styles/` - Environment Variables):** Define Gum styling environment variables for colors.
- [ ] **Basic UI Components (`components/` - Shell Functions):** `Header.sh`, `Footer.sh`, `ProgressBar.sh` (using `gum progress`), `SelectionList.sh` (using `gum choose` or `gum filter`).
- [ ] **Main Screens (`screens/` - Shell Scripts):** `MainMenu.sh`, `CategoryView.sh`, `InstallProgress.sh`, `SummaryScreen.sh`.
- [ ] **Integrate UI with Engine:** Connect UI to display data, reflect progress (e.g. `gum spin`), and trigger engine actions, using the YAML `category` field for UI grouping.

### Phase 4: Core Utilities & Handlers

- [ ] **Shell Execution (integrated into `engine.sh`):** Develop robust Zsh script execution function, injecting `ITEM_CONFIG_DIR` and handling output streaming (potentially with `gum log`).
- [ ] **`logger.sh` (`utils/`):** Implement comprehensive file-based logging (e.g., `~/Library/Logs/MacSnap/setup.log`). Log script executions, errors, and key events.
- [ ] **Type Handlers (in `engine.sh` or dedicated functions):** Implement the specific logic wrapper for each `type` to call the correct script fields.
- [ ] **`permissions.sh` (`utils/`):** Basic functions to guide users for manual permission settings if script failures indicate them.

### Phase 5: Populate Configuration Files (`configs/`)

- [ ] **For each item listed in section 7 (and others planned):**
  - [ ] Create its subdirectory within the appropriate top-level folder (`configs/init/`, `configs/apps/`, or `configs/system/`). For example, `configs/apps/iterm2/`.
  - [ ] Create the item's YAML file (e.g., `iterm2.yaml`).
  - [ ] Add auxiliary files (plists, templates, etc.) into the item's subdirectory.
  - [ ] Write idempotent Zsh scripts for `install`, `validate`, `configure` (if needed), and `uninstall`, using `${ITEM_CONFIG_DIR}` to reference local files.
  - [ ] Define `dependencies` where appropriate and set the `category` field for UI display.

### Phase 6: UI Enhancements & Theme (Gum Styling)

- [ ] **Apply Consistent Aesthetic:** Refine all UI components with Gum styling options.
- [ ] **Implement Interactive Elements:** Use `gum input`, `gum write`, `gum confirm`, etc. for interactivity.
- [ ] **Enhance Feedback:** Utilize `gum notify`, `gum spin`, `gum progress` effectively.

### Phase 7: Specific Feature Implementations

- [ ] **Oh My Posh Setup:** Ensure YAML scripts for Oh My Posh correctly handle theme installation and font recommendations, using `ITEM_CONFIG_DIR` if bundling assets.
- [ ] **Antidote Configuration:** Ensure YAML scripts correctly set up Antidote and manage Zsh plugin lists.
- [ ] **Keyboard Fix Agent (`hidutil` + Launch Agent):**
  - [ ] Create `keyboard-fix.yaml` (type `launch_agent`) with its `.plist` template (defining `hidutil` commands) in its `ITEM_CONFIG_DIR` (e.g. `configs/system/keyboard-fix/`).
  - [ ] `install.script` should copy/customize the plist to `~/Library/LaunchAgents/` and load with `launchctl`.
  - [ ] `validate.script` checks if the agent is loaded (`launchctl list`).
  - [ ] `uninstall.script` unloads and removes the plist.

### Phase 8: Testing

- [ ] **Unit Tests:** For core logic (config loading, YAML validation, dependency resolution, script execution utilities).
- [ ] **Integration Tests:** Test individual type handlers with mock configurations.
- [ ] **End-to-End Testing:**
  - [ ] On a clean macOS VM, test installation/configuration of a representative software subset from `init`, `apps`, and `system`.
  - [ ] Verify system settings are applied correctly.
  - [ ] Test error handling (item failure, critical dependency failure) and UI feedback.
  - [ ] Verify correct usage of `ITEM_CONFIG_DIR` in scripts.
  - [ ] Confirm log file creation and content.

### Phase 9: Documentation & Packaging

- [ ] **Refine `logger.sh`:** Ensure logging is robust and informative.
- [ ] **User Documentation:** Update/create comprehensive user guide: how to run, explanation of UI categories (using Gum for presentation), troubleshooting common issues, log file location and interpretation.
- [ ] **Developer Documentation (Optional but Recommended):** Guidelines on how to add new software/configurations (YAML structure, script writing, placing files in `init/`, `apps/`, or `system/`).
- [ ] **Distribution Preparation:** Refine `macsnap` script, consider creating an installer or simple distribution archive.

### Phase 10: Iteration & Refinement

- [ ] **Address Testing Issues:** Fix bugs identified during all testing phases.
- [ ] **Refine UI/UX:** Based on usability testing and feedback.
- [ ] **Incorporate Feedback:** Address any further user feedback on initial versions.

This revised technical design document provides a comprehensive blueprint for the MacSnap Setup application.
