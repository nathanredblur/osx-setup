#!/bin/zsh

# MacSnap - Initial Setup Script

# Exit immediately if a command exits with a non-zero status.
set -e

# Determine the script's absolute directory to reliably find utils/ and configs/
SCRIPT_DIR="$(cd "$(dirname "${0%/*}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/utils"
CONFIGS_DIR="${SCRIPT_DIR}/configs"
MENU_GENERATOR_SCRIPT="${UTILS_DIR}/menu_generator.sh"

# --- Gum Colors (using environment variables for gum) ---
export GUM_INPUT_PROMPT_FOREGROUND="#00FFFF"
export GUM_CHOOSE_ITEM_FOREGROUND="#FF00FF"
export GUM_CHOOSE_SELECTED_FOREGROUND="#00FF00"
# Add more gum styling variables as needed

# --- Helper Functions ---
print_header() {
  gum style --border normal --margin "1" --padding "1 2" --border-foreground "#00FFFF" "MacSnap Setup"
}

print_info() {
  echo "$(gum style --foreground \"#00FFFF\" \"INFO:\") $1"
}

print_success() {
  echo "$(gum style --foreground \"#00FF00\" \"SUCCESS:\") $1"
}

print_warning() {
  echo "$(gum style --foreground \"#FFFF00\" \"WARNING:\") $1"
}

# --- Installation Functions ---

# 1. Install Homebrew
install_homebrew() {
  echo "INFO: Checking for Homebrew..."
  if ! command -v brew &> /dev/null; then
    echo "INFO: Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for the current script session
    if [[ "$(uname -m)" == "arm64" ]]; then # Apple Silicon
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else # Intel
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    echo "SUCCESS: Homebrew installed."
  else
    echo "SUCCESS: Homebrew is already installed."
  fi
  # Ensure brew is in PATH for subsequent commands in this script
  if [[ "$(uname -m)" == "arm64" ]] && [[ -x /opt/homebrew/bin/brew ]]; then # Apple Silicon
      export PATH="/opt/homebrew/bin:$PATH"
  elif [[ -x /usr/local/bin/brew ]]; then # Intel
      export PATH="/usr/local/bin:$PATH"
  fi
}

# 2. Install yq (YAML processor)
install_yq() {
  echo "INFO: Checking for yq (YAML processor)..."
  if ! command -v yq &> /dev/null; then
    echo "INFO: yq not found. Installing yq via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "ERROR: Homebrew is required to install yq, but brew command was not found."
        echo "Please ensure Homebrew is installed and in your PATH."
        exit 1
    fi
    brew install yq
    echo "SUCCESS: yq installed."
  else
    echo "SUCCESS: yq is already installed."
  fi
}

# 3. Install gum
install_gum() {
  echo "INFO: Checking for gum..."
  if ! command -v gum &> /dev/null; then
    echo "INFO: gum not found. Installing gum via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "ERROR: Homebrew is required to install gum, but brew command was not found."
        echo "Please ensure Homebrew is installed and in your PATH."
        exit 1
    fi
    brew install gum
    echo "SUCCESS: gum installed."
  else
    echo "SUCCESS: gum is already installed."
  fi
}

# 4. Install mas-cli (Mac App Store CLI)
install_mas() {
  print_info "Checking for mas-cli..." # Uses gum-styled output as gum should be installed by now
  if ! command -v mas &> /dev/null; then
    print_info "mas-cli not found. Installing mas-cli via Homebrew..."
    if ! command -v brew &> /dev/null; then
        # This case should ideally not be hit if install_homebrew succeeded
        echo "ERROR: Homebrew is required to install mas-cli, but brew command was not found." >&2
        exit 1
    fi
    brew install mas
    print_success "mas-cli installed."
  else
    print_success "mas-cli is already installed."
  fi
}

# --- Main Script ---
main() {
  echo "--- MacSnap Initial Setup ---"
  echo "INFO: Starting MacSnap setup process..."

  install_homebrew # Uses basic echo for output
  install_yq       # Uses basic echo for output
  install_gum      # Uses basic echo for output

  # Now that gum is confirmed to be installed, we can use gum-styled helper functions
  print_header
  gum spin --spinner dot --title "Finalizing essential tools setup..." -- sleep 1

  install_mas # Can now safely use print_info, print_success

  print_info "Initial essential tools (Homebrew, yq, Gum, Mas) have been checked/installed."
  gum style --foreground "#00FF00" "Setup phase 1 complete!"

  # --- User software selection via menu_generator.sh ---
  print_info "Loading configuration menu..."

  if [ ! -f "$MENU_GENERATOR_SCRIPT" ]; then
    print_warning "Menu generator script not found at $MENU_GENERATOR_SCRIPT"
    exit 1
  fi

  if [ ! -x "$MENU_GENERATOR_SCRIPT" ]; then
    print_warning "Menu generator script ($MENU_GENERATOR_SCRIPT) is not executable. Please run: chmod +x $MENU_GENERATOR_SCRIPT"
    exit 1
  fi

  selected_item_ids_output=$("$MENU_GENERATOR_SCRIPT")

  if echo "$selected_item_ids_output" | grep -q "No items selected."; then
    print_warning "No items were selected from the menu."
    print_success "MacSnap script finished."
    exit 0
  fi

  if ! echo "$selected_item_ids_output" | grep -q "^Selected item IDs:"; then
    print_warning "Menu generator returned unexpected output:"
    echo "$selected_item_ids_output"
    exit 1
  fi

  clean_selected_item_ids=$(echo "$selected_item_ids_output" | tail -n +2 | awk 'NF') # Get all lines after header, and remove any fully blank lines

  if [ -z "$clean_selected_item_ids" ]; then
    print_warning "No item IDs were retrieved after processing menu output (or only blank lines found)."
    print_success "MacSnap script finished."
    exit 0
  fi

  print_info "Will attempt to process the following selected item IDs:"
  echo "$clean_selected_item_ids"
  gum spin --spinner dot --title "Preparing to process selections..." -- sleep 1

  for selected_id in $(echo "$clean_selected_item_ids"); do
    print_info "Attempting to process selected ID: $selected_id"
    processed_this_id=false
    
    # Find the YAML file corresponding to this ID
    # We iterate through .yml files in CONFIGS_DIR and check their 'id' field.
    # Using find with -print0 and while read -d '' is safer for filenames with spaces, etc.
    while IFS= read -r -d '' yaml_file_path; do
      # Ensure yq can read the id, provide a default or handle error if id is missing
      current_file_id=$(yq e '.id // "__MISSING_ID__"' "$yaml_file_path")
      
      if [[ "$current_file_id" == "$selected_id" ]]; then
        print_success "Found configuration file for '$selected_id': $yaml_file_path"
        
        # --- BEGIN VALIDATE SCRIPT EXECUTION ---
        should_skip_install_and_configure=false
        validate_script_content=$(yq e '.validate.script // ""' "$yaml_file_path")

        if [[ -n "$validate_script_content" ]]; then
            print_info "Executing validate script for $selected_id..."
            TEMP_VALIDATE_SCRIPT_FILE=$(mktemp)
            if [[ -z "$TEMP_VALIDATE_SCRIPT_FILE" || ! -f "$TEMP_VALIDATE_SCRIPT_FILE" ]]; then
                print_warning "Failed to create temporary validate script file for $selected_id. Assuming installation is needed."
            else
                echo "#!/bin/zsh" > "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "set -e" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                # Note: validate scripts might also need to not exit on error for certain checks, 
                # but for now, we assume they will handle their own logic and exit 0 for "is_installed=true"
                echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "# Original file: $yaml_file_path" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "# Item ID: $selected_id (validate step)" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                echo "$validate_script_content" >> "$TEMP_VALIDATE_SCRIPT_FILE"
                chmod +x "$TEMP_VALIDATE_SCRIPT_FILE"

                if "$TEMP_VALIDATE_SCRIPT_FILE"; then
                    print_success "Validation passed for '$selected_id' (already installed/configured). Skipping install & configure steps."
                    should_skip_install_and_configure=true
                else
                    validate_script_exit_code=$?
                    print_info "Validation failed for '$selected_id' (exit code: $validate_script_exit_code) or item not present. Proceeding with installation."
                fi
                rm "$TEMP_VALIDATE_SCRIPT_FILE"
            fi
        else
            print_info "No '.validate.script' found for '$selected_id'. Assuming installation is needed."
        fi
        # --- END VALIDATE SCRIPT EXECUTION ---

        if ! $should_skip_install_and_configure; then
            # Extract and run install script
            install_script_content=$(yq e '.install.script // ""' "$yaml_file_path")
            
            if [[ -n "$install_script_content" ]]; then
              print_info "Executing install script for $selected_id..."
              TEMP_INSTALL_SCRIPT_FILE=$(mktemp)
              if [[ -z "$TEMP_INSTALL_SCRIPT_FILE" || ! -f "$TEMP_INSTALL_SCRIPT_FILE" ]]; then 
                  print_warning "Failed to create temporary install script file for $selected_id. Skipping."
              else
                  echo "#!/bin/zsh" > "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "set -e" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "# Original file: $yaml_file_path" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "# Item ID: $selected_id (install step)" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  echo "$install_script_content" >> "$TEMP_INSTALL_SCRIPT_FILE"
                  chmod +x "$TEMP_INSTALL_SCRIPT_FILE"
                  
                  if "$TEMP_INSTALL_SCRIPT_FILE"; then
                    print_success "Install script for '$selected_id' completed successfully."
                    
                    # --- BEGIN CONFIGURE SCRIPT EXECUTION ---
                    configure_script_content=$(yq e '.configure.script // ""' "$yaml_file_path")
                    if [[ -n "$configure_script_content" ]]; then
                      print_info "Executing configure script for $selected_id..."
                      TEMP_CONFIGURE_SCRIPT_FILE=$(mktemp)
                      if [[ -z "$TEMP_CONFIGURE_SCRIPT_FILE" || ! -f "$TEMP_CONFIGURE_SCRIPT_FILE" ]]; then
                          print_warning "Failed to create temporary configure script file for $selected_id. Skipping configure step."
                      else
                          echo "#!/bin/zsh" > "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "set -e" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "export ITEM_CONFIG_DIR=\"$CONFIGS_DIR\"" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "# Original file: $yaml_file_path" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "# Item ID: $selected_id (configure step)" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          echo "$configure_script_content" >> "$TEMP_CONFIGURE_SCRIPT_FILE"
                          chmod +x "$TEMP_CONFIGURE_SCRIPT_FILE"
                          
                          if "$TEMP_CONFIGURE_SCRIPT_FILE"; then
                              print_success "Configure script for '$selected_id' completed successfully."
                          else
                              configure_script_exit_code=$?
                              print_warning "Configure script for '$selected_id' failed with exit code: $configure_script_exit_code."
                          fi
                          rm "$TEMP_CONFIGURE_SCRIPT_FILE"
                      fi
                    else
                      print_info "No '.configure.script' found for '$selected_id'. Skipping configure step."
                    fi
                    # --- END CONFIGURE SCRIPT EXECUTION ---
                    
                  else
                    script_exit_code=$?
                    print_warning "Install script for '$selected_id' failed with exit code: $script_exit_code."
                  fi
                  rm "$TEMP_INSTALL_SCRIPT_FILE"
              fi # end check for TEMP_INSTALL_SCRIPT_FILE creation
            else
              print_info "No '.install.script' found in $yaml_file_path for '$selected_id'. Nothing to execute for installation step."
            fi # end check for install_script_content
        fi # end check for should_skip_install_and_configure

        processed_this_id=true
        break # Found and processed the file for this selected_id, move to next selected_id
      fi
    done < <(find "$CONFIGS_DIR" -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) -print0)

    if ! $processed_this_id; then
      print_warning "Could not find a configuration YAML file with id '$selected_id' in $CONFIGS_DIR"
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

  print_success "MacSnap script finished processing selected items."
}

# Run main function
main 