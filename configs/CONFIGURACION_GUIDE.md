# Guía de Configuración de MacSnap Setup

Esta guía completa explica cómo crear, estructurar y configurar archivos YAML para MacSnap Setup, basándose en el análisis de los archivos existentes y las especificaciones técnicas del sistema.

## 📋 Índice

1. [Introducción](#introducción)
2. [Estructura Básica de Archivos YAML](#estructura-básica)
3. [Campos de Configuración](#campos-de-configuración)
4. [Tipos de Instalación](#tipos-de-instalación)
5. [Scripts de Configuración](#scripts-de-configuración)
6. [Ejemplos Completos](#ejemplos-completos)
7. [Configuraciones Especiales](#configuraciones-especiales)
8. [Buenas Prácticas](#buenas-prácticas)
9. [Validación y Pruebas](#validación-y-pruebas)

---

## 🚀 Introducción

MacSnap Setup utiliza archivos YAML para definir cómo instalar y configurar software y ajustes del sistema en macOS. Cada elemento instalable se define en su propio archivo `.yml` dentro del directorio `configs/` o sus subdirectorios.

### Características Principales:

- **Modularidad**: Cada aplicación/configuración en su propio archivo
- **Flexibilidad**: Soporte para múltiples tipos de instalación
- **Reutilizable**: Sistema de dependencias y categorización
- **Extensible**: Fácil agregar nuevos elementos

---

## 📁 Estructura Básica

### Estructura de Archivos

```
configs/
├── _configs.yml              # Configuración especial (scripts start/end)
├── application.yml           # Archivo individual de aplicación
├── browsers/                 # Subdirectorio opcional para organización
│   ├── chrome.yml
│   └── firefox.yml
├── development/              # Categorización por tipo
│   ├── vscode.yml
│   └── docker.yml
└── ...                       # Más categorías y archivos
```

### Anatomía de un Archivo YAML

```yaml
# Identificación básica
id: "application-id"
name: "Application Name"
description: "Brief description of the application"

# Configuración de instalación
type: "installation_type"
category: "UI Category"

# Opciones adicionales
selected_by_default: false
requires_license: false
tags: ["tag1", "tag2"]
url: "https://official-website.com"

# Información adicional
notes: |
  Multi-line notes with:
  - Feature descriptions
  - Usage instructions
  - Important considerations

# Dependencias
dependencies: ["dep1", "dep2"]

# Scripts de ejecución
install: |
  # Installation script
validate: |
  # Validation script
configure: |
  # Configuration script
uninstall: |
  # Uninstallation script
```

---

## 🏗️ Campos de Configuración

### Campos Obligatorios

#### `id` (string, requerido)

Identificador único para la aplicación/configuración.

```yaml
id: "my-application"
```

**Reglas**:

- Único en todo el sistema
- Solo minúsculas, números y guiones
- Descriptivo y consistente

#### `name` (string, requerido)

Nombre amigable mostrado en la interfaz.

```yaml
name: "My Application"
```

#### `description` (string, requerido)

Descripción breve de la aplicación.

```yaml
description: "Brief description of what this application does"
```

#### `type` (string, requerido)

Define el método de instalación. Ver [Tipos de Instalación](#tipos-de-instalación).

```yaml
type: "brew_cask"
```

#### `category` (string, requerido)

Categoría para agrupar en la interfaz de usuario.

```yaml
category: "Development"
```

**Categorías Comunes**:

- `"Core Utilities"`
- `"Development"`
- `"Productivity"`
- `"Browsers"`
- `"Media"`
- `"System Tweaks"`
- `"Security"`
- `"Cloud-Network"`
- `"Communication"`

### Campos Opcionales

#### `selected_by_default` (boolean, opcional)

Si el elemento viene preseleccionado.

```yaml
selected_by_default: true # Por defecto: false
```

#### `requires_license` (boolean, opcional)

Indica si requiere licencia o suscripción.

```yaml
requires_license: true # Por defecto: false
```

#### `tags` (array, opcional)

Etiquetas para categorización adicional.

```yaml
tags:
  - "editor"
  - "development"
  - "essential"
```

#### `url` (string, opcional)

URL del sitio web oficial.

```yaml
url: "https://www.example.com/"
```

#### `notes` (string multilínea, opcional)

Información adicional detallada.

```yaml
notes: |
  - Key feature 1
  - Key feature 2
  - Installation considerations
  - Usage instructions
```

#### `dependencies` (array, opcional)

Lista de IDs de elementos que deben instalarse antes.

```yaml
dependencies: ["git", "homebrew"]
```

---

## 🔧 Tipos de Instalación

### 1. `brew` - Herramientas de Línea de Comandos

Para utilidades y herramientas CLI instaladas mediante Homebrew.

```yaml
type: "brew"
install: |
  echo "Installing tool..."
  brew install tool-name
validate: |
  command -v tool-name &> /dev/null
```

**Ejemplo**: Git, ripgrep, fzf

### 2. `brew_cask` - Aplicaciones GUI

Para aplicaciones de escritorio instaladas mediante Homebrew Cask.

```yaml
type: "brew_cask"
install: |
  echo "Installing Application..."
  brew install --cask application-name
validate: |
  brew list --cask | grep -q "application-name" || ls /Applications/ | grep -q "Application.app"
```

**Ejemplo**: Visual Studio Code, Google Chrome, Docker

### 3. `mas` - Apps del Mac App Store

Para aplicaciones disponibles en la Mac App Store.

```yaml
type: "mas"
install: |
  echo "Installing App..."
  echo "App Store ID: 123456789"
  if command -v mas >/dev/null 2>&1; then
    mas install 123456789
  else
    echo "Please install manually from App Store"
  fi
validate: |
  ls /Applications/ | grep -q "App.app"
```

**Ejemplo**: irvue, Telegram, AdGuard

### 4. `direct_download_dmg` - Descarga Manual de DMG

Para aplicaciones que requieren descarga manual de archivos DMG.

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

**Ejemplo**: Zeb Browser

### 5. `system_config` - Configuraciones del Sistema

Para ajustes del sistema usando comandos `defaults` de macOS.

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

**Ejemplo**: Configuración del Dock, ajustes del trackpad

### 6. `proto_tool` - Herramientas de Proto

Para herramientas gestionadas por el sistema Proto (version manager).

```yaml
type: "proto_tool"
dependencies: ["proto"]
install: |
  echo "Installing tool via Proto..."
  proto install tool-name
validate: |
  proto list | grep -q "tool-name"
```

### 7. `launch_agent` - Agentes de Inicio

Para configurar servicios que se ejecutan automáticamente.

```yaml
type: "launch_agent"
install: |
  echo "Setting up launch agent..."
  cp "${ITEM_CONFIG_DIR}/com.example.agent.plist" ~/Library/LaunchAgents/
  launchctl load ~/Library/LaunchAgents/com.example.agent.plist
```

### 8. `shell_script` - Scripts Personalizados

Para instalaciones que requieren scripts completamente personalizados.

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

## 📖 Ejemplos Completos

### Ejemplo 1: Aplicación Simple (Homebrew Cask)

```yaml
id: "raycast"
name: "Raycast"
description: "Blazingly fast, totally extendable launcher"
type: "brew_cask"
category: "Productivity"
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
install: |
  echo "Installing Raycast..."
  brew install --cask raycast
validate: |
  brew list --cask | grep -q "raycast" || ls /Applications/ | grep -q "Raycast.app"
configure: |
  echo "Raycast configuration complete"
  echo "Launch Raycast and complete the setup process"
uninstall: |
  echo "Uninstalling Raycast..."
  brew uninstall --cask raycast
```

### Ejemplo 2: Herramienta CLI (Homebrew)

```yaml
id: "git"
name: "Git"
description: "Distributed version control system"
type: "brew"
category: "Core Utilities"
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
install: |
  echo "Installing Git..."
  brew install git
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

### Ejemplo 3: App Store (MAS)

```yaml
id: "irvue"
name: "irVue"
description: "Unsplash wallpaper app for beautiful desktop backgrounds"
type: "mas"
category: "Media"
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
dependencies: []
install: |
  echo "Installing irVue..."
  echo "App Store ID: 1039633667"
  if command -v mas >/dev/null 2>&1; then
    mas install 1039633667
  else
    echo "Please install manually from App Store"
  fi
validate: |
  ls /Applications/ | grep -i "irvue" >/dev/null 2>&1
configure: |
  echo "irVue configuration complete"
  echo "Launch irVue to start enjoying beautiful wallpapers"
uninstall: |
  echo "Uninstalling irVue..."
  echo "Use Mac App Store to uninstall or: mas uninstall 1039633667"
```

### Ejemplo 4: Configuración del Sistema

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

## ⚙️ Configuraciones Especiales

### Archivo `_configs.yml`

Este archivo especial contiene scripts que se ejecutan al inicio y final del proceso de instalación:

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

**Propósito**:

- **start**: Preparación del sistema, verificaciones iniciales
- **end**: Limpieza final, reportes, optimizaciones

---

## ✅ Buenas Prácticas

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

## 🧪 Validación y Pruebas

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
