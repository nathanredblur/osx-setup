#!/bin/zsh

# Utility to scan YAML files in ../configs and generate a selection menu using Gum.

# Ensure yq is installed
if ! command -v yq &> /dev/null; then
    echo "Error: yq (YAML processor) is not installed. Please install it first."
    echo "See: https://github.com/mikefarah/yq#install"
    exit 1
fi

# Ensure gum is installed
if ! command -v gum &> /dev/null; then
    echo "Error: gum (for glamorous shell scripts) is not installed. Please install it first."
    echo "See: https://github.com/charmbracelet/gum#installation"
    exit 1
fi

CONFIGS_DIR="$(cd "$(dirname "$0")/../configs" && pwd)" # Absolute path to configs/

# Use parallel indexed arrays for mapping names to IDs
menu_item_names=()
menu_item_ids=()

# Removed Associative Array Sanity Check as we are no longer using them.

if [ ! -d "$CONFIGS_DIR" ]; then
    echo "Error: Configuration directory not found: $CONFIGS_DIR" >&2
    exit 1
fi

# Find all .yml files in the configs directory
# and extract 'name' and 'id' for the menu
while IFS= read -r -d '' yaml_file; do
    echo "Debug (Find Loop): Processing file path from find: '$yaml_file'" >&2

    raw_name_from_yq=$(yq e -r '.name' "$yaml_file")
    raw_id_from_yq=$(yq e -r '.id' "$yaml_file")

    echo "Debug (YQ Output): Raw Name from yq: '$raw_name_from_yq', Raw ID from yq: '$raw_id_from_yq'" >&2
    
    # Aggressively clean item_name and item_id
    item_name=$(echo "$raw_name_from_yq" | tr -cd '[[:print:]]' | xargs)
    item_id=$(echo "$raw_id_from_yq" | tr -cd '[[:print:]]' | xargs)

    echo "Debug (Population): YAML: '$yaml_file', Cleaned Name: '$item_name', Cleaned ID: '$item_id'" >&2
    
    if [[ -n "$item_name" && "$item_name" != "null" && -n "$item_id" && "$item_id" != "null" ]]; then
        menu_item_names+=("$item_name")
        menu_item_ids+=("$item_id")
        echo "Debug (Population): Added '$item_name' (ID: '$item_id') to arrays." >&2
    else
        echo "Warning: Skipping '$yaml_file' as it's missing 'name' or 'id', or they are null after cleaning." >&2
    fi
done < <(find "$CONFIGS_DIR" -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) -print0)

if [ ${#menu_item_names[@]} -eq 0 ]; then
    echo "No valid configuration items found in $CONFIGS_DIR to display in menu." >&2
    # Output a specific message that macsnap.sh can check for if needed
    echo "STATUS:NO_ITEMS_FOUND"
    exit 0 # Exit cleanly so macsnap.sh can handle this message
fi

# Display the menu using gum choose. Allow multiple selections with --no-limit.
selected_names_str=$(gum choose --no-limit --header "Select items to process:" "${menu_item_names[@]}")

# If nothing is selected (e.g., user pressed Esc or string is empty), exit
if [ -z "$selected_names_str" ]; then
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
    echo "Debug: Processing selected name from gum: '${selected_name_cleaned}'" >&2
    found_id=""
    
    # Iterate through the menu_item_names array to find the index
    for i in {1..${#menu_item_names[@]}}; do # Zsh arrays are 1-indexed by default
        # Note: Accessing array elements in Zsh: menu_item_names[i]
        if [[ "${menu_item_names[i]}" == "$selected_name_cleaned" ]]; then
            found_id="${menu_item_ids[i]}"
            echo "Debug: Matched '${selected_name_cleaned}'. Found ID: '${found_id}' at index $i" >&2
            echo "$found_id"
            print_ids=true
            break # Found the ID for this selected name, move to the next selected name
        fi
    done
    
    if [[ -z "$found_id" ]]; then
        echo "Warning: Could not find ID for selected name: '${selected_name_cleaned}'" >&2
    fi
done <<< "$selected_names_str"

if ! $print_ids; then
    echo "STATUS:NO_VALID_IDS_PRINTED_AFTER_SELECTION"
fi

exit 0 