#!/bin/zsh

# Utility to scan YAML files in ../configs and generate a selection menu using Gum.

# Determine the script's absolute directory to reliably find the logger
SCRIPT_DIR_MENU_GEN="$(cd "$(dirname "$0")" && pwd)"
LOGGER_SCRIPT_MENU_GEN="${SCRIPT_DIR_MENU_GEN}/logger.sh"

# Source the logger utility
if [ -f "$LOGGER_SCRIPT_MENU_GEN" ]; then
    source "$LOGGER_SCRIPT_MENU_GEN"
else
    # Fallback echo if logger itself is missing
    echo "FATAL: Logger script not found at $LOGGER_SCRIPT_MENU_GEN. Cannot proceed." >&2
    exit 1
fi

# Ensure yq is installed
if ! command -v yq &> /dev/null; then
    log_info "ERROR: yq (YAML processor) is not installed. Please install it first."
    log_info "See: https://github.com/mikefarah/yq#install"
    exit 1
fi

# Ensure gum is installed
if ! command -v gum &> /dev/null; then
    log_info "ERROR: gum (for glamorous shell scripts) is not installed. Please install it first."
    log_info "See: https://github.com/charmbracelet/gum#installation"
    exit 1
fi

CONFIGS_DIR="$(cd "$(dirname "$0")/../configs" && pwd)" # Absolute path to configs/
log_debug "Menu Generator: CONFIGS_DIR is $CONFIGS_DIR"

# Use parallel indexed arrays for mapping names to IDs
menu_item_names=()
menu_item_ids=()
pre_selected_item_names_list=() # For items to be pre-selected

if [ ! -d "$CONFIGS_DIR" ]; then
    log_info "ERROR: Configuration directory not found: $CONFIGS_DIR"
    exit 1
fi

# Find all .yml/.yaml files in the configs directory
# and extract 'name', 'id', and 'selected_by_default' for the menu
while IFS= read -r -d '' yaml_file; do
    log_debug "(Find Loop): Processing file path from find: '$yaml_file'"

    raw_name_from_yq=$(yq e -r '.name' "$yaml_file")
    raw_id_from_yq=$(yq e -r '.id' "$yaml_file")
    # Read .selected_by_default, default to false if missing or null
    raw_selected_by_default=$(yq e '.selected_by_default // false' "$yaml_file") 

    log_debug "(YQ Output): Raw Name: '$raw_name_from_yq', Raw ID: '$raw_id_from_yq', Raw SelectedByDefault: '$raw_selected_by_default'"
    
    item_name=$(echo "$raw_name_from_yq" | tr -cd '[[:print:]]' | xargs)
    item_id=$(echo "$raw_id_from_yq" | tr -cd '[[:print:]]' | xargs)
    # Convert selected_by_default to a clean true/false string for reliable comparison
    selected_by_default_cleaned=$(echo "$raw_selected_by_default" | tr '[:upper:]' '[:lower:]' | xargs)

    log_debug "(Population): YAML: '$yaml_file', Cleaned Name: '$item_name', Cleaned ID: '$item_id', Cleaned SelectedByDefault: '$selected_by_default_cleaned'"
    
    if [[ -n "$item_name" && "$item_name" != "null" && -n "$item_id" && "$item_id" != "null" ]]; then
        menu_item_names+=("$item_name")
        menu_item_ids+=("$item_id")
        log_debug "(Population): Added '$item_name' (ID: '$item_id') to arrays."
        
        if [[ "$selected_by_default_cleaned" == "true" ]]; then
            pre_selected_item_names_list+=("$item_name")
            log_debug "(Population): '$item_name' marked for pre-selection."
        fi
    else
        log_info "WARNING: Skipping '$yaml_file' as it's missing 'name' or 'id', or they are null after cleaning."
    fi
done < <(find "$CONFIGS_DIR" -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) -print0)

if [ ${#menu_item_names[@]} -eq 0 ]; then
    log_info "WARNING: No valid configuration items found in $CONFIGS_DIR to display in menu."
    echo "STATUS:NO_ITEMS_FOUND"
    exit 0
fi

# Construct the --selected argument for gum choose
gum_choose_selected_arg=""
if [ ${#pre_selected_item_names_list[@]} -gt 0 ]; then
  # Join the array into a comma-separated string
  gum_choose_selected_arg="--selected=$(IFS=,; echo "${pre_selected_item_names_list[*]}")"
  log_debug "(Gum Args): Pre-selected items string for gum: $gum_choose_selected_arg"
fi

# Display the menu using gum choose.
# Pass the pre-selected items string if it was constructed.
# Using ${=gum_choose_selected_arg} ensures Zsh performs word splitting on the argument if it contains spaces,
# and handles it correctly if it's empty.
selected_names_str=$(gum choose --no-limit --header "Select items to process (Space to toggle, Enter to confirm):" "${menu_item_names[@]}" ${=gum_choose_selected_arg})


# If nothing is selected (e.g., user pressed Esc or string is empty), exit
if [ -z "$selected_names_str" ]; then
    log_debug "No items selected by user via gum choose."
    echo "STATUS:NO_ITEMS_SELECTED" # Output a specific message
    exit 0
fi

# Output header for selected IDs
echo "Selected item IDs:"

# Process selected names to find their corresponding IDs
# Read selected names line by line (gum choose outputs one per line for multi-select)
print_ids=false
while IFS= read -r selected_name; do
    # Trim the selected_name just in case gum adds whitespace (though unlikely for its direct output)
    selected_name_cleaned=$(echo "$selected_name" | xargs)
    log_debug "Processing selected name from gum: '${selected_name_cleaned}'"
    found_id=""
    
    # Iterate through the menu_item_names array to find the index
    for i in {1..${#menu_item_names[@]}}; do # Zsh arrays are 1-indexed by default
        # Note: Accessing array elements in Zsh: menu_item_names[i]
        if [[ "${menu_item_names[i]}" == "$selected_name_cleaned" ]]; then
            found_id="${menu_item_ids[i]}"
            log_debug "Matched '${selected_name_cleaned}'. Found ID: '${found_id}' at index $i"
            echo "$found_id"
            print_ids=true
            break # Found the ID for this selected name, move to the next selected name
        fi
    done
    
    if [[ -z "$found_id" ]]; then
        log_info "WARNING: Could not find ID for selected name: '${selected_name_cleaned}'"
    fi
done <<< "$selected_names_str"

if ! $print_ids && [[ -n "$selected_names_str" ]]; then # Only output this status if names were selected but no IDs printed
    echo "STATUS:NO_VALID_IDS_PRINTED_AFTER_SELECTION"
fi

exit 0 