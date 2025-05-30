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

# --- Refactored Functions ---

ensure_core_dependencies() {
  log_info "--- Ensuring Core Dependencies ---"
  install_homebrew
  install_yq
  install_gum
  # install_mas # Keep mas install separate for now as it's after the initial gum style
  log_info "SUCCESS: Core dependencies (Homebrew, yq, Gum) checked/installed."
}

run_menu_and_get_selections() {
  log_info "--- Loading Configuration Menu ---" >&2

  if [ ! -f "$MENU_GENERATOR_SCRIPT" ]; then
    log_info "FATAL: Menu generator script not found at $MENU_GENERATOR_SCRIPT" >&2
    return 1 # Indicate error
  fi

  if [ ! -x "$MENU_GENERATOR_SCRIPT" ]; then
    log_info "FATAL: Menu generator script ($MENU_GENERATOR_SCRIPT) is not executable. Please run: chmod +x $MENU_GENERATOR_SCRIPT" >&2
    return 1 # Indicate error
  fi

  local selected_item_ids_output
  selected_item_ids_output=$("$MENU_GENERATOR_SCRIPT")
  local menu_exit_code=$? # Capture exit code of menu_generator.sh

  log_debug "Raw output from menu_generator.sh (exit code $menu_exit_code):"$'
'"$selected_item_ids_output"

  if [ $menu_exit_code -ne 0 ]; then
      log_info "WARNING: Menu generator exited with a non-zero status code ($menu_exit_code)." >&2
      # Even with non-zero, check specific statuses if output exists
  fi

  # Check for specific status messages from menu_generator.sh
  if echo "$selected_item_ids_output" | grep -q "STATUS:NO_ITEMS_FOUND"; then
      log_info "WARNING: No configuration items found to display in menu." >&2
      echo "" # Return empty to signify no selection
      return 0
  elif echo "$selected_item_ids_output" | grep -q "STATUS:NO_ITEMS_SELECTED"; then
      log_info "INFO: No items were selected from the menu." >&2
      echo "" # Return empty
      return 0
  elif ! echo "$selected_item_ids_output" | grep -q "^Selected item IDs:"; then
      log_info "WARNING: Menu generator returned unexpected output or an error condition:" >&2
      # To prevent its output from being captured if we are in a 'return 1' scenario
      # we should print this potentially multi-line message also to stderr
      echo "$selected_item_ids_output" >&2 # Echo raw output for inspection to stderr
      echo "" # Return empty
      return 1 # Indicate an issue from menu
  fi

  local clean_selected_item_ids
  clean_selected_item_ids=$(echo "$selected_item_ids_output" | tail -n +2 | awk 'NF')
  log_debug "Cleaned selected item IDs for processing: $clean_selected_item_ids"
  
  echo "$clean_selected_item_ids" # This is the "return value" of the function
  return 0
}

process_selected_item() {
  local selected_id="$1"
  if [ -z "$selected_id" ]; then
    log_info "WARNING: process_selected_item called with no ID."
    return 1 # Indicate failure
  fi

  log_info "--- Processing Item: $selected_id ---"
  local found_yaml_file_path=""

  # Find the YAML file corresponding to this ID
  # Using a while loop and process substitution for safer file handling
  while IFS= read -r -d '' yaml_file_candidate; do
    current_file_id=$(yq e '.id // "__MISSING_ID__"' "$yaml_file_candidate")
    log_debug "Checking YAML in process_selected_item: $yaml_file_candidate (ID: $current_file_id) against Selected ID: $selected_id"
    
    if [[ "$current_file_id" == "$selected_id" ]]; then
        found_yaml_file_path="$yaml_file_candidate"
        break # Found the file
    fi
  done < <(find "$CONFIGS_DIR" -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) -print0)

  if [[ -z "$found_yaml_file_path" ]]; then
    log_info "WARNING: Could not find a configuration YAML file with id '$selected_id' in $CONFIGS_DIR"
    return 1 # Indicate failure to process this item
  fi

  log_info "SUCCESS: Found configuration file for '$selected_id': $found_yaml_file_path"

  # --- VALIDATE SCRIPT ---
  local should_skip_install_and_configure=false
  local validate_script_content
  validate_script_content=$(yq e '.validate.script // ""' "$found_yaml_file_path")

  if [[ -n "$validate_script_content" ]]; then
    log_info "Executing validate script for $selected_id..."
    local TEMP_VALIDATE_SCRIPT_FILE
    TEMP_VALIDATE_SCRIPT_FILE=$(mktemp)
    if [[ -z "$TEMP_VALIDATE_SCRIPT_FILE" || ! -f "$TEMP_VALIDATE_SCRIPT_FILE" ]]; then
        log_info "WARNING: Failed to create temporary validate script file for $selected_id. Assuming installation is needed."
    else
        echo "#!/bin/zsh" > "$TEMP_VALIDATE_SCRIPT_FILE"
        echo "set -e" >> "$TEMP_VALIDATE_SCRIPT_FILE"
        echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_VALIDATE_SCRIPT_FILE"
        echo "source \"$LOGGER_SCRIPT\"" >> "$TEMP_VALIDATE_SCRIPT_FILE"
        echo "log_debug \"Running validate script for $selected_id from temp file $TEMP_VALIDATE_SCRIPT_FILE (macsnap.sh)\"" >> "$TEMP_VALIDATE_SCRIPT_FILE"
        echo "$validate_script_content" >> "$TEMP_VALIDATE_SCRIPT_FILE"
        chmod +x "$TEMP_VALIDATE_SCRIPT_FILE"

        if "$TEMP_VALIDATE_SCRIPT_FILE"; then
            log_info "SUCCESS: Validation passed for '$selected_id' (already installed/configured). Skipping install & configure steps."
            should_skip_install_and_configure=true
        else
            local validate_script_exit_code=$?
            log_info "Validation failed for '$selected_id' (exit code: $validate_script_exit_code) or item not present. Proceeding with installation."
        fi
        rm "$TEMP_VALIDATE_SCRIPT_FILE"
    fi
  else
    log_info "No '.validate.script' found for '$selected_id'. Assuming installation is needed."
  fi

  if ! $should_skip_install_and_configure; then
    # --- INSTALL SCRIPT ---
    local install_script_content
    install_script_content=$(yq e '.install.script // ""' "$found_yaml_file_path")
    if [[ -n "$install_script_content" ]]; then
      log_info "Executing install script for $selected_id..."
      local TEMP_INSTALL_SCRIPT_FILE
      TEMP_INSTALL_SCRIPT_FILE=$(mktemp)
      if [[ -z "$TEMP_INSTALL_SCRIPT_FILE" || ! -f "$TEMP_INSTALL_SCRIPT_FILE" ]]; then 
          log_info "WARNING: Failed to create temporary install script file for $selected_id. Skipping."
      else
          echo "#!/bin/zsh" > "$TEMP_INSTALL_SCRIPT_FILE"
          echo "set -e" >> "$TEMP_INSTALL_SCRIPT_FILE"
          echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_INSTALL_SCRIPT_FILE"
          echo "source \"$LOGGER_SCRIPT\"" >> "$TEMP_INSTALL_SCRIPT_FILE"
          echo "log_debug \"Running install script for $selected_id from temp file $TEMP_INSTALL_SCRIPT_FILE (macsnap.sh)\"" >> "$TEMP_INSTALL_SCRIPT_FILE"
          echo "$install_script_content" >> "$TEMP_INSTALL_SCRIPT_FILE"
          chmod +x "$TEMP_INSTALL_SCRIPT_FILE"
          
          local install_succeeded=false
          if "$TEMP_INSTALL_SCRIPT_FILE"; then
            log_info "SUCCESS: Install script for '$selected_id' completed successfully."
            install_succeeded=true
            
            # --- CONFIGURE SCRIPT (only if install succeeded) ---
            local configure_script_content
            configure_script_content=$(yq e '.configure.script // ""' "$found_yaml_file_path")
            if [[ -n "$configure_script_content" ]]; then
              log_info "Executing configure script for $selected_id..."
              local TEMP_CONFIGURE_SCRIPT_FILE
              TEMP_CONFIGURE_SCRIPT_FILE=$(mktemp)
              if [[ -z "$TEMP_CONFIGURE_SCRIPT_FILE" || ! -f "$TEMP_CONFIGURE_SCRIPT_FILE" ]]; then
                  log_info "WARNING: Failed to create temporary configure script file for $selected_id. Skipping configure step."
              else
                  echo "#!/bin/zsh" > "$TEMP_CONFIGURE_SCRIPT_FILE"
                  echo "set -e" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                  echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                  echo "source \"$LOGGER_SCRIPT\"" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                  echo "log_debug \"Running configure script for $selected_id from temp file $TEMP_CONFIGURE_SCRIPT_FILE (macsnap.sh)\"" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                  echo "$configure_script_content" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                  chmod +x "$TEMP_CONFIGURE_SCRIPT_FILE"
                  
                  if "$TEMP_CONFIGURE_SCRIPT_FILE"; then
                    log_info "SUCCESS: Configure script for '$selected_id' completed successfully."
                  else
                    local configure_script_exit_code=$?
                    log_info "WARNING: Configure script for '$selected_id' failed with exit code: $configure_script_exit_code."
                  fi
                  rm "$TEMP_CONFIGURE_SCRIPT_FILE"
              fi # end temp configure file creation check
            else
              log_info "No '.configure.script' found for '$selected_id'. Skipping configure step."
            fi # end configure_script_content check
          else # install script failed
            local script_exit_code=$?
            log_info "WARNING: Install script for '$selected_id' failed with exit code: $script_exit_code."
          fi # end install script execution
          rm "$TEMP_INSTALL_SCRIPT_FILE"
      fi # end temp install file creation check
    else
      log_info "No '.install.script' found in $found_yaml_file_path for '$selected_id'. Nothing to execute for installation step."
    fi # end install_script_content check
  fi # end check for should_skip_install_and_configure
  
  log_info "--- Finished Processing Item: $selected_id ---"
  return 0 # Success for this item
}

# --- Main Script ---
main() {
  log_info "--- MacSnap Initial Setup ---"
  log_info "Starting MacSnap setup process..."
  if [[ -n "$MACSNAP_DEBUG" && "$MACSNAP_DEBUG" == "true" ]]; then
    log_debug "MACSNAP_DEBUG is true. Debug messages will be shown."
  fi

  ensure_core_dependencies

  # Now that gum is confirmed to be installed, we can use gum-styled helper functions
  if command -v gum &> /dev/null; then
    gum style --border normal --margin "1" --padding "1 2" --border-foreground "#00FFFF" "MacSnap Setup"
  else
    log_info "MacSnap Setup Header (gum not found for styling)"
  fi
  
  # Install mas separately after the initial core deps and header
  install_mas
  
  gum spin --spinner dot --title "Finalizing essential tools setup..." -- sleep 1

  log_info "Initial essential tools (Homebrew, yq, Gum, Mas) have been checked/installed."
  log_info "SUCCESS: Setup phase 1 complete!"

  # --- User software selection ---
  local all_selected_ids
  all_selected_ids=$(run_menu_and_get_selections)
  local menu_call_status=$?

  if [ $menu_call_status -ne 0 ]; then
      log_info "WARNING: Menu generation or selection process reported an error. Exiting."
      log_info "SUCCESS: MacSnap script finished (due to menu error)."
      exit 1
  fi
  
  if [ -z "$all_selected_ids" ]; then
    log_info "No items selected or an issue occurred in menu generation. Nothing further to process."
    log_info "SUCCESS: MacSnap script finished."
    exit 0
  fi

  log_info "Will attempt to process the following selected item IDs:"
  echo "$all_selected_ids" # Keep this raw echo for clear list
  gum spin --spinner dot --title "Preparing to process selections..." -- sleep 1

  local item_process_failed=false
  for id_to_process in $(echo "$all_selected_ids"); do
    if ! process_selected_item "$id_to_process"; then
      log_info "ERROR: Failed to process item '$id_to_process'. Check logs above."
      # Depending on desired behavior, you might want to set a flag or exit.
      # For now, we'll log and continue with other items if possible.
      item_process_failed=true 
    fi
  done

  if $item_process_failed; then
    log_info "WARNING: One or more items failed to process. Please review the logs."
    log_info "MacSnap script finished with errors."
    exit 1
  else
    log_info "SUCCESS: All selected items processed successfully!"
    log_info "MacSnap script finished."
  fi
  exit 0
}

# Call main function
main "$@" 