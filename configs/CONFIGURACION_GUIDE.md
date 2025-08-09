# MacSnap Setup Configuration Guide

This comprehensive guide explains how to create, structure, and configure YAML files for MacSnap Setup, based on the analysis of existing files and the system's technical specifications.

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Basic YAML File Structure](#basic-structure)
3. [Configuration Fields](#configuration-fields)
4. [Installation Types](#installation-types)
5. [Configuration Scripts](#configuration-scripts)
6. [Complete Examples](#complete-examples)
7. [Special Configurations](#special-configurations)
8. [Best Practices](#best-practices)
9. [Validation and Testing](#validation-and-testing)

---

## 🚀 Introduction

MacSnap Setup uses YAML files to define how to install and configure software and system settings on macOS. Each installable element is defined in its own `.yml` file within the `configs/` directory or its subdirectories.

### Main Features:

- **Modularity**: Each application/configuration in its own file
- **Flexibility**: Support for multiple installation types
- **Reusable**: Dependency system and categorization
- **Extensible**: Easy to add new elements

---

## 📁 Basic Structure

### File Structure

```
configs/
├── _configs.yml              # Special configuration (start/end scripts)
├── application.yml           # Individual application file
├── browsers/                 # Optional subdirectory for organization
│   ├── chrome.yml
│   └── firefox.yml
├── development/              # Categorization by type
│   ├── vscode.yml
│   └── docker.yml
└── ...                       # More categories and files
```

### Anatomy of a YAML File

```yaml
# Basic identification
id: "application-id"
name: "Application Name"
description: "Brief description of the application"
image: "https://example.com/logo.png" # Optional: application logo/icon

# Installation configuration
type: "installation_type"
category: "UI Category"
bundle: 'brew "formula"' # Optional: brew bundle format

# Additional options
selected_by_default: false
requires_license: false
tags: ["tag1", "tag2"]
url: "https://official-website.com"

# Additional information
notes: |
  Multi-line notes with:
  - Feature descriptions
  - Usage instructions
  - Important considerations

# Dependencies
dependencies: ["dep1", "dep2"]

# Execution scripts
install: |
  # Installation script (deprecated for brew/cask/mas types)
validate: |
  # Validation script
configure: |
  # Configuration script
uninstall: |
  # Uninstallation script
```

---

## 🏗️ Configuration Fields

### Required Fields

#### `id` (string, required)

Unique identifier for the application/configuration.

```yaml
id: "my-application"
```

**Rules**:

- Unique across the entire system
- Only lowercase letters, numbers, and hyphens
- Descriptive and consistent

#### `name` (string, required)

Friendly name displayed in the interface.

```yaml
name: "My Application"
```

#### `description` (string, required)

Brief description of the application.

```yaml
description: "Brief description of what this application does"
```

#### `type` (string, required)

Defines the installation method. See [Installation Types](#installation-types).

```yaml
type: "brew_cask"
```

#### `category` (string, required)

Category for grouping in the user interface.

```yaml
category: "Development"
```

**Common Categories**:

- `"Core Utilities"`
- `"Development"`
- `"Productivity"`
- `"Browsers"`
- `"Media"`
- `"System Tweaks"`
- `"Security"`
- `"Cloud-Network"`
- `"Communication"`

### Optional Fields

#### `image` (string, optional)

URL or path to the application logo/icon.

```yaml
image: "https://example.com/app-logo.png"
```

#### `bundle` (string, optional)

Brew bundle format string following [Homebrew Bundle guidelines](https://docs.brew.sh/Brew-Bundle-and-Brewfile).

```yaml
# For brew_cask type
bundle: 'cask "firefox"'

# For brew type
bundle: 'brew "git"'

# For mas type
bundle: 'mas "Refined GitHub", id: 1519867270'
```

#### `selected_by_default` (boolean, optional)

Whether the item comes preselected.

```yaml
selected_by_default: true # Default: false
```

#### `requires_license` (boolean, optional)

Indicates if it requires a license or subscription.

```yaml
requires_license: true # Default: false
```

#### `tags` (array, optional)

Tags for additional categorization.

```yaml
tags:
  - "editor"
  - "development"
  - "essential"
```

#### `url` (string, optional)

Official website URL.

```yaml
url: "https://www.example.com/"
```

#### `notes` (string multiline, optional)

Detailed additional information.

```yaml
notes: |
  - Key feature 1
  - Key feature 2
  - Installation considerations
  - Usage instructions
```

#### `dependencies` (array, optional)

List of element IDs that must be installed first. Note: Not used for `mas` type.

```yaml
dependencies: ["git", "homebrew"]
```

---

## 🔧 Installation Types

### 1. `brew` - Command Line Tools

For CLI utilities and tools installed via Homebrew. Uses bundle format for installation.

```yaml
type: "brew"
bundle: 'brew "tool-name"'
validate: |
  command -v tool-name &> /dev/null
```

**Examples**: Git, ripgrep, fzf

### 2. `brew_cask` - GUI Applications

For desktop applications installed via Homebrew Cask. Uses bundle format for installation.

```yaml
type: "brew_cask"
bundle: 'cask "application-name"'
validate: |
  brew list --cask | grep -q "application-name" || ls /Applications/ | grep -q "Application.app"
```

**Examples**: Visual Studio Code, Google Chrome, Docker

### 3. `mas` - Mac App Store Apps

For applications available in the Mac App Store. Uses bundle format with App Store ID.

```yaml
type: "mas"
bundle: 'mas "App Name", id: 123456789'
validate: |
  ls /Applications/ | grep -q "App.app"
```

**Examples**: irvue, Telegram, AdGuard
**Note**: Dependencies are not used for `mas` type installations.

### 4. `direct_download_dmg` - Manual DMG Download

For applications that require manual download of DMG files.

```yaml
type: "direct_download_dmg"
install: |
  echo "Installing Application..."
  echo "Note: Manual download required"
  echo "1. Visit https://example.com/download"
  echo "2. Download the macOS version"
  echo "3. Open DMG and drag to Applications"
validate: |
  ls /Applications/ | grep -q "Application.app"
```

**Example**: Zen Browser

### 5. `system_config` - System Configurations

For system settings using macOS `defaults` commands.

```yaml
type: "system_config"
install: |
  echo "This item only configures existing system settings"
validate: |
  # Always return 1 to force configuration
  exit 1
configure: |
  echo "Applying system settings..."
  defaults write com.apple.system setting -bool true
  killall SystemUIServer
```

**Example**: Dock configuration, trackpad settings

### 6. `proto_tool` - Proto Tools

For tools managed by the Proto system (version manager).

```yaml
type: "proto_tool"
dependencies: ["proto"]
install: |
  echo "Installing tool via Proto..."
  proto install tool-name
validate: |
  proto list | grep -q "tool-name"
```

### 7. `launch_agent` - Launch Agents

For configuring services that run automatically.

```yaml
type: "launch_agent"
install: |
  echo "Setting up launch agent..."
  cp "${ITEM_CONFIG_DIR}/com.example.agent.plist" ~/Library/LaunchAgents/
  launchctl load ~/Library/LaunchAgents/com.example.agent.plist
```

### 8. `shell_script` - Custom Scripts

For installations that require completely custom scripts.

```yaml
type: "shell_script"
install: |
  echo "Running custom installation..."
  # Custom installation logic here
```

---

## 📜 Scripts de Configuración

### Variables de Entorno Disponibles

Todos los scripts tienen acceso a:

- `ITEM_CONFIG_DIR`: Ruta absoluta al directorio `configs/`
- Variables estándar del sistema

### Tipos de Scripts

#### `install` (opcional)

Script que realiza la instalación.

```yaml
install: |
  echo "Installing..."
  # Installation commands here
```

#### `validate` (opcional)

Script que verifica si ya está instalado.

```yaml
validate: |
  # Return 0 if installed, non-zero if not
  command -v application &> /dev/null
```

#### `configure` (opcional)

Script de configuración post-instalación.

```yaml
configure: |
  echo "Configuring..."
  # Configuration commands here
```

#### `uninstall` (opcional)

Script para desinstalar.

```yaml
uninstall: |
  echo "Uninstalling..."
  # Uninstallation commands here
```

### Buenas Prácticas para Scripts

1. **Mensajes Informativos**: Siempre incluir `echo` para informar al usuario
2. **Manejo de Errores**: Verificar comandos antes de usarlos
3. **Paths Absolutos**: Usar rutas completas cuando sea necesario
4. **Permisos**: Considerar requirements de sudo/admin
5. **Cleanup**: Limpiar archivos temporales

---

## 📖 Complete Examples

### Example 1: Simple Application (Homebrew Cask)

```yaml
id: "raycast"
name: "Raycast"
description: "Blazingly fast, totally extendable launcher"
image: "https://www.raycast.com/favicon-32x32.png"
type: "brew_cask"
category: "Productivity"
bundle: 'cask "raycast"'
selected_by_default: true
requires_license: false
tags:
  - launcher
  - productivity
  - shortcuts
url: "https://www.raycast.com/"
notes: |
  - Modern launcher with extensive extension ecosystem
  - Built-in clipboard history and window management
  - Free tier with paid Pro features available
dependencies: []
validate: |
  brew list --cask | grep -q "raycast" || ls /Applications/ | grep -q "Raycast.app"
configure: |
  echo "Raycast configuration complete"
  echo "Launch Raycast and complete the setup process"
uninstall: |
  echo "Uninstalling Raycast..."
  brew uninstall --cask raycast
```

### Example 2: CLI Tool (Homebrew)

```yaml
id: "git"
name: "Git"
description: "Distributed version control system"
image: "https://git-scm.com/images/logos/downloads/Git-Icon-1788C.png"
type: "brew"
category: "Core Utilities"
bundle: 'brew "git"'
selected_by_default: true
requires_license: false
tags:
  - version-control
  - development
  - essential
url: "https://git-scm.com/"
notes: |
  Essential tool for modern software development

  📌 After installation, configure with:
  - git config --global user.name "Your Name"
  - git config --global user.email "your.email@example.com"
dependencies: []
validate: |
  command -v git &> /dev/null
configure: |
  echo "Git configuration complete"
  echo "Configure Git with your details:"
  echo "  git config --global user.name \"Your Name\""
  echo "  git config --global user.email \"your.email@example.com\""
uninstall: |
  echo "Uninstalling Git..."
  brew uninstall git
```

### Example 3: App Store (MAS)

```yaml
id: "irvue"
name: "irVue"
description: "Unsplash wallpaper app for beautiful desktop backgrounds"
image: "https://is1-ssl.mzstatic.com/image/thumb/Purple126/v4/b9/84/12/b9841230-c4e8-7b8e-9f7c-7e8b7f7c7f7c/AppIcon-0-0-1x_U007emarketing-0-0-0-7-0-0-sRGB-0-0-0-GLES2_U002c0-512MB-85-220-0-0.png/512x512bb.jpg"
type: "mas"
category: "Media"
bundle: 'mas "irVue", id: 1039633667'
selected_by_default: false
requires_license: false
tags:
  - wallpaper
  - unsplash
  - photography
url: "https://irvue.tumblr.com/"
notes: |
  - Beautiful wallpaper app powered by Unsplash
  - Automatic wallpaper rotation
  - Free with optional premium features
validate: |
  ls /Applications/ | grep -i "irvue" >/dev/null 2>&1
configure: |
  echo "irVue configuration complete"
  echo "Launch irVue to start enjoying beautiful wallpapers"
uninstall: |
  echo "Uninstalling irVue..."
  echo "Use Mac App Store to uninstall or: mas uninstall 1039633667"
```

### Example 4: System Configuration

```yaml
id: "dock_settings"
name: "Dock Settings"
description: "Configure Dock auto-hide, size, and behavior"
type: "system_config"
category: "System Tweaks"
selected_by_default: true
requires_license: false
tags:
  - system-config
  - dock
  - ui
url: "https://support.apple.com/en-us/HT201730"
notes: |
  - Configures dock auto-hide for more screen space
  - Adjusts dock size and behavior preferences
  - No additional software required
dependencies: []
install: |
  echo "This item only configures existing system settings"
validate: |
  # Always return 1 so configure script runs
  exit 1
configure: |
  echo "Applying Dock settings..."

  # Auto-hide the Dock
  defaults write com.apple.dock autohide -bool true

  # Set Dock size
  defaults write com.apple.dock tilesize -int 48

  # Don't show recent applications
  defaults write com.apple.dock show-recents -bool false

  # Speed up auto-hide animation
  defaults write com.apple.dock autohide-time-modifier -float 0.3

  # Restart Dock to apply changes
  killall Dock

  echo "Dock settings applied successfully"
```

---

## ⚙️ Special Configurations

### `_configs.yml` File

This special file contains scripts that run at the beginning and end of the installation process:

```yaml
start: |
  echo "🚀 MacSnap Setup - Initialization Started"
  # Initialization scripts here
  # Create directories, check system, etc.

end: |
  echo "🏁 MacSnap Setup - Finalization Started"
  # Cleanup scripts here
  # Generate reports, cleanup temp files, etc.
```

**Purpose**:

- **start**: System preparation, initial checks
- **end**: Final cleanup, reports, optimizations

---

## ✅ Best Practices

### 1. Nomenclatura y Organización

```yaml
# ✅ Bueno
id: "visual-studio-code"
name: "Visual Studio Code"

# ❌ Evitar
id: "VSCode123"
name: "vscode"
```

### 2. Categorización Consistente

```yaml
# Use categorías estándar
category: "Development"  # ✅
category: "dev-tools"    # ❌
```

### 3. Scripts Robustos

```yaml
install: |
  echo "Installing Application..."

  # ✅ Verificar herramientas antes de usar
  if command -v brew >/dev/null 2>&1; then
    brew install --cask application
  else
    echo "Error: Homebrew not found"
    exit 1
  fi

validate: |
  # ✅ Múltiples métodos de validación
  brew list --cask | grep -q "application" || \
  ls /Applications/ | grep -q "Application.app"
```

### 4. Información Clara

```yaml
notes: |
  - Clear feature descriptions
  - Installation requirements
  - Post-installation steps
  - Usage tips
  - Licensing information
```

### 5. Dependencias Apropiadas

```yaml
# ✅ Dependencias reales
dependencies: ["git", "node"]

# ❌ Evitar dependencias innecesarias
dependencies: ["every", "possible", "tool"]
```

---

## 🧪 Validation and Testing

### Checklist de Validación

Antes de agregar un nuevo archivo de configuración:

- [ ] **Campos obligatorios**: `id`, `name`, `description`, `type`, `category`
- [ ] **ID único**: No conflictos con otros archivos
- [ ] **Scripts funcionales**: `install`, `validate`, `configure`, `uninstall`
- [ ] **Sintaxis YAML**: Archivo bien formado
- [ ] **Categoría válida**: Usa categorías estándar
- [ ] **Dependencias correctas**: Referencias válidas
- [ ] **Documentación**: `notes` informativas

### Pruebas Recomendadas

1. **Sintaxis YAML**:

   ```bash
   yaml lint configs/my-app.yml
   ```

2. **Validación de scripts**:

   ```bash
   # Probar scripts individualmente
   bash -n script_content
   ```

3. **Prueba completa**:
   - Instalar en sistema limpio
   - Verificar validación funciona
   - Probar configuración
   - Probar desinstalación

---

## 📚 Recursos Adicionales

### Referencias Útiles

- **macOS defaults**: [https://macos-defaults.com/](https://macos-defaults.com/)
- **Homebrew Search**: [https://formulae.brew.sh/](https://formulae.brew.sh/)
- **MAS CLI**: [https://github.com/mas-cli/mas](https://github.com/mas-cli/mas)
- **YAML Validator**: [https://yamlchecker.com/](https://yamlchecker.com/)

### Herramientas de Desarrollo

```bash
# Validar YAML
yamllint configs/

# Buscar en Homebrew
brew search application-name

# Obtener App Store ID
mas search "App Name"

# Verificar defaults
defaults read com.apple.dock
```

---

## 🤝 Contribución

Para contribuir con nuevas configuraciones:

1. **Fork y clone** el repositorio
2. **Crea tu archivo** siguiendo esta guía
3. **Prueba localmente** la configuración
4. **Documenta cambios** en commits claros
5. **Envía pull request** con descripción detallada

### Template para Nuevas Configuraciones

```yaml
id: "new-application"
name: "New Application"
description: "What this application does"
type: "brew_cask" # or appropriate type
category: "Appropriate Category"
selected_by_default: false
requires_license: false # true if needs license
tags:
  - relevant
  - tags
url: "https://official-website.com"
notes: |
  - Key features and benefits
  - Installation considerations
  - Usage instructions
  - Licensing information
dependencies: [] # Add if needed
install: |
  echo "Installing..."
  # Installation commands
validate: |
  # Validation logic
configure: |
  echo "Configuration complete"
  # Post-installation setup
uninstall: |
  echo "Uninstalling..."
  # Uninstallation commands
```

---

_Esta guía es un documento vivo que se actualiza según las necesidades del proyecto MacSnap Setup._
