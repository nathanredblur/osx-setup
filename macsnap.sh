#!/bin/zsh

# MacSnap - Initial Setup Script

# Exit immediately if a command exits with a non-zero status.
set -e

# Determine the script's absolute directory to reliably find utils/ and configs/
SCRIPT_DIR="$(cd "$(dirname "${0%/*}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/utils"
CONFIGS_DIR="${SCRIPT_DIR}/configs"
MENU_GENERATOR_SCRIPT="${UTILS_DIR}/menu_generator.sh"
LOGGER_SCRIPT="${UTILS_DIR}/logger.sh"

# Source the logger utility
if [ -f "$LOGGER_SCRIPT" ]; then
    source "$LOGGER_SCRIPT"
else
    echo "FATAL: Logger script not found at $LOGGER_SCRIPT" >&2
    exit 1
fi

# --- Gum Colors (using environment variables for gum) ---
# export GUM_INPUT_PROMPT_FOREGROUND="#00FFFF"
# export GUM_CHOOSE_ITEM_FOREGROUND="#FF00FF"
# export GUM_CHOOSE_SELECTED_FOREGROUND="#00FF00"
# Add more gum styling variables as needed

# --- Helper Functions ---
# print_header() { ... }
# print_info() { ... }
# print_success() { ... }
# print_warning() { ... }

# --- Installation Functions ---

# 1. Install Homebrew
install_homebrew() {
  log_info "Checking for Homebrew..."
  if ! command -v brew &> /dev/null; then
    log_info "Homebrew not found. Installing Homebrew..."
    # Suppressing output of the Homebrew install script for cleaner logs, 
    # but errors will still cause script to exit due to 'set -e' in this main script.
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" > /dev/null
    log_info "Homebrew installer finished. Adding brew to PATH for current session..."
    if [[ "$(uname -m)" == "arm64" ]]; then # Apple Silicon
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else # Intel
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    log_info "SUCCESS: Homebrew installed and configured in PATH."
  else
    log_info "SUCCESS: Homebrew is already installed."
  fi
  # Ensure brew is in PATH for subsequent commands in this script
  if [[ "$(uname -m)" == "arm64" ]] && [[ -x /opt/homebrew/bin/brew ]]; then
      export PATH="/opt/homebrew/bin:$PATH"
       log_debug "Homebrew (ARM64) PATH exported: /opt/homebrew/bin"
  elif [[ -x /usr/local/bin/brew ]]; then
      export PATH="/usr/local/bin:$PATH"
      log_debug "Homebrew (Intel) PATH exported: /usr/local/bin"
  fi
}

# 2. Install yq (YAML processor)
install_yq() {
  log_info "Checking for yq (YAML processor)..."
  if ! command -v yq &> /dev/null; then
    log_info "yq not found. Installing yq via Homebrew..."
    if ! command -v brew &> /dev/null; then
        log_info "ERROR: Homebrew is required to install yq, but brew command was not found."
        log_info "ERROR: Please ensure Homebrew is installed and in your PATH."
        exit 1
    fi
    brew install yq
    log_info "SUCCESS: yq installed."
  else
    log_info "SUCCESS: yq is already installed."
  fi
}

# 3. Install gum
install_gum() {
  log_info "Checking for gum..."
  if ! command -v gum &> /dev/null; then
    log_info "gum not found. Installing gum via Homebrew..."
    if ! command -v brew &> /dev/null; then
        log_info "ERROR: Homebrew is required to install gum, but brew command was not found."
        log_info "ERROR: Please ensure Homebrew is installed and in your PATH."
        exit 1
    fi
    brew install gum
    log_info "SUCCESS: gum installed."
  else
    log_info "SUCCESS: gum is already installed."
  fi
}

# 4. Install mas-cli (Mac App Store CLI)
install_mas() {
  log_info "Checking for mas-cli..."
  if ! command -v mas &> /dev/null; then
    log_info "mas-cli not found. Installing mas-cli via Homebrew..."
    if ! command -v brew &> /dev/null; then
        log_info "ERROR: Homebrew is required to install mas-cli, but brew command was not found." >&2
        exit 1
    fi
    brew install mas
    log_info "SUCCESS: mas-cli installed."
  else
    log_info "SUCCESS: mas-cli is already installed."
  fi
}

# --- Main Script ---
main() {
  log_info "--- MacSnap Initial Setup ---"
  log_info "Starting MacSnap setup process..."
  log_debug "MACSNAP_DEBUG is true. Debug messages will be shown."

  install_homebrew
  install_yq
  install_gum

  # Now that gum is confirmed to be installed, we can use gum-styled helper functions
  if command -v gum &> /dev/null; then
    gum style --border normal --margin "1" --padding "1 2" --border-foreground "#00FFFF" "MacSnap Setup"
  else
    log_info "MacSnap Setup Header"
  fi
  gum spin --spinner dot --title "Finalizing essential tools setup..." -- sleep 1

  install_mas

  log_info "Initial essential tools (Homebrew, yq, Gum, Mas) have been checked/installed."
  log_info "SUCCESS: Setup phase 1 complete!"

  # --- User software selection via menu_generator.sh ---
  log_info "Loading configuration menu..."

  if [ ! -f "$MENU_GENERATOR_SCRIPT" ]; then
    log_info "FATAL: Menu generator script not found at $MENU_GENERATOR_SCRIPT"
    exit 1
  fi

  if [ ! -x "$MENU_GENERATOR_SCRIPT" ]; then
    log_info "FATAL: Menu generator script ($MENU_GENERATOR_SCRIPT) is not executable. Please run: chmod +x $MENU_GENERATOR_SCRIPT"
    exit 1
  fi

  selected_item_ids_output=$("$MENU_GENERATOR_SCRIPT")
  log_debug "Raw output from menu_generator.sh:"$'
'"$selected_item_ids_output"

  # Check for specific status messages from menu_generator.sh
  if echo "$selected_item_ids_output" | grep -q "STATUS:NO_ITEMS_FOUND"; then
      log_info "WARNING: No configuration items found to display in menu."
      log_info "SUCCESS: MacSnap script finished."
      exit 0
  elif echo "$selected_item_ids_output" | grep -q "STATUS:NO_ITEMS_SELECTED"; then
      log_info "WARNING: No items were selected from the menu."
      log_info "SUCCESS: MacSnap script finished."
      exit 0
  elif ! echo "$selected_item_ids_output" | grep -q "^Selected item IDs:"; then
      log_info "WARNING: Menu generator returned unexpected output or an error condition:" 
      echo "$selected_item_ids_output" # Echo raw output for inspection
      log_info "SUCCESS: MacSnap script finished (due to menu error/unexpected state)."
      exit 1 # Indicate an issue
  fi

  clean_selected_item_ids=$(echo "$selected_item_ids_output" | tail -n +2 | awk 'NF')
  log_debug "Cleaned selected item IDs: $clean_selected_item_ids"

  if [ -z "$clean_selected_item_ids" ]; then
    log_info "WARNING: No item IDs were retrieved after processing menu output."
    log_info "SUCCESS: MacSnap script finished."
    exit 0
  fi

  log_info "Will attempt to process the following selected item IDs:"
  echo "$clean_selected_item_ids" # Keep this raw echo for clear list
  gum spin --spinner dot --title "Preparing to process selections..." -- sleep 1

  for selected_id in $(echo "$clean_selected_item_ids"); do
    log_info "Attempting to process selected ID: $selected_id"
    processed_this_id=false
    
    while IFS= read -r -d '' yaml_file_path; do
      current_file_id=$(yq e '.id // "__MISSING_ID__"' "$yaml_file_path")
      log_debug "Checking YAML: $yaml_file_path (ID: $current_file_id) against Selected ID: $selected_id"
      
      if [[ "$current_file_id" == "$selected_id" ]]; then
        log_info "SUCCESS: Found configuration file for '$selected_id': $yaml_file_path"
        
        should_skip_install_and_configure=false
        validate_script_content=$(yq e '.validate.script // ""' "$yaml_file_path")

        if [[ -n "$validate_script_content" ]]; then
            log_info "Executing validate script for $selected_id..."
            TEMP_VALIDATE_SCRIPT_FILE=$(mktemp)
            if [[ -z "$TEMP_VALIDATE_SCRIPT_FILE" || ! -f "$TEMP_VALIDATE_SCRIPT_FILE" ]]; then
                log_info "WARNING: Failed to create temporary validate script file for $selected_id. Assuming installation is needed."
            else
                echo "#!/bin/zsh" > "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "set -e" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "source \"$LOGGER_SCRIPT\"" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "log_debug \"Running validate script for $selected_id from temp file $TEMP_VALIDATE_SCRIPT_FILE\"" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "$validate_script_content" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                chmod +x "$TEMP_VALIDATE_SCRIPT_FILE"

                if "$TEMP_VALIDATE_SCRIPT_FILE"; then
                    log_info "SUCCESS: Validation passed for '$selected_id' (already installed/configured). Skipping install & configure steps."
                    should_skip_install_and_configure=true
                else
                    validate_script_exit_code=$?
                    log_info "Validation failed for '$selected_id' (exit code: $validate_script_exit_code) or item not present. Proceeding with installation."
                fi
                rm "$TEMP_VALIDATE_SCRIPT_FILE"
            fi
        else
            log_info "No '.validate.script' found for '$selected_id'. Assuming installation is needed."
        fi

        if ! $should_skip_install_and_configure; then
            install_script_content=$(yq e '.install.script // ""' "$yaml_file_path")
            if [[ -n "$install_script_content" ]]; then
              log_info "Executing install script for $selected_id..."
              TEMP_INSTALL_SCRIPT_FILE=$(mktemp)
              if [[ -z "$TEMP_INSTALL_SCRIPT_FILE" || ! -f "$TEMP_INSTALL_SCRIPT_FILE" ]]; then 
                  log_info "WARNING: Failed to create temporary install script file for $selected_id. Skipping."
              else
                  echo "#!/bin/zsh" > "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "set -e" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "source \"$LOGGER_SCRIPT\"" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "log_debug \"Running install script for $selected_id from temp file $TEMP_INSTALL_SCRIPT_FILE\"" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "$install_script_content" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  chmod +x "$TEMP_INSTALL_SCRIPT_FILE"
                  
                  if "$TEMP_INSTALL_SCRIPT_FILE"; then
                    log_info "SUCCESS: Install script for '$selected_id' completed successfully."
                    
                    configure_script_content=$(yq e '.configure.script // ""' "$yaml_file_path")
                    if [[ -n "$configure_script_content" ]]; then
                      log_info "Executing configure script for $selected_id..."
                      TEMP_CONFIGURE_SCRIPT_FILE=$(mktemp)
                      if [[ -z "$TEMP_CONFIGURE_SCRIPT_FILE" || ! -f "$TEMP_CONFIGURE_SCRIPT_FILE" ]]; then
                          log_info "WARNING: Failed to create temporary configure script file for $selected_id. Skipping configure step."
                      else
                          echo "#!/bin/zsh" > "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "set -e" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "source \"$LOGGER_SCRIPT\"" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "log_debug \"Running configure script for $selected_id from temp file $TEMP_CONFIGURE_SCRIPT_FILE\"" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "$configure_script_content" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          chmod +x "$TEMP_CONFIGURE_SCRIPT_FILE"
                          
                          if "$TEMP_CONFIGURE_SCRIPT_FILE"; then
                              log_info "SUCCESS: Configure script for '$selected_id' completed successfully."
                          else
                              configure_script_exit_code=$?
                              log_info "WARNING: Configure script for '$selected_id' failed with exit code: $configure_script_exit_code."
                          fi
                          rm "$TEMP_CONFIGURE_SCRIPT_FILE"
                      fi
                    else
                      log_info "No '.configure.script' found for '$selected_id'. Skipping configure step."
                    fi
                  else
                    script_exit_code=$?
                    log_info "WARNING: Install script for '$selected_id' failed with exit code: $script_exit_code."
                  fi
                  rm "$TEMP_INSTALL_SCRIPT_FILE"
              fi
            else
              log_info "No '.install.script' found in $yaml_file_path for '$selected_id'. Nothing to execute for installation step."
            fi
        fi
        processed_this_id=true
        break
      fi
    done < <(find "$CONFIGS_DIR" -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) -print0)

    if ! $processed_this_id; then
      log_info "WARNING: Could not find a configuration YAML file with id '$selected_id' in $CONFIGS_DIR"
    fi
  done

  # Remove or comment out the old placeholder section
  # print_info "Next steps (TODO): Ask user for software selection using YAML configurations."
  # gum confirm "Proceed to placeholder for custom software installation?" && {
  #   print_info "User chose to proceed."
  #   # --- Placeholder for installing selected software ---
  #   print_info "TODO: Install software selected by the user."
  # } || {
  #   print_warning "User chose not to proceed with custom software installation at this time."
  # }

  log_info "SUCCESS: MacSnap script finished processing selected items."
}

# Run main function
main 