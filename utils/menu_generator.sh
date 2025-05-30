#!/bin/zsh

# Utility to scan YAML files in ../configs and generate a staged selection menu using Gum.

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
    log_info "ERROR: yq (YAML processor) is not installed. Please install it first." >&2
    log_info "See: https://github.com/mikefarah/yq#install" >&2
    exit 1
fi

# Ensure gum is installed
if ! command -v gum &> /dev/null; then
    log_info "ERROR: gum (for glamorous shell scripts) is not installed. Please install it first." >&2
    log_info "See: https://github.com/charmbracelet/gum#installation" >&2
    exit 1
fi

CONFIGS_DIR="$(cd "$(dirname "$0")/../configs" && pwd)" # Absolute path to configs/
log_debug "Menu Generator: CONFIGS_DIR is $CONFIGS_DIR"

# Arrays to store all item details from all YAMLs
all_item_names=()
all_item_ids=()
all_item_categories=()
all_item_selected_by_default_flags=() # Stores true/false strings

all_categories_map=() # Associative array to store unique categories
typeset -A all_categories_map # Declare as associative

if [ ! -d "$CONFIGS_DIR" ]; then
    log_info "ERROR: Configuration directory not found: $CONFIGS_DIR" >&2
    echo "STATUS:NO_CONFIG_DIR_FOUND" # Specific status for this error
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
    raw_category_from_yq=$(yq e '.category // "Uncategorized"' "$yaml_file") # Default if category missing

    log_debug "(YQ Output): Raw Name: '$raw_name_from_yq', Raw ID: '$raw_id_from_yq', Raw SelectedByDefault: '$raw_selected_by_default', Raw Category: '$raw_category_from_yq'"
    
    item_name=$(echo "$raw_name_from_yq" | tr -cd '[[:print:]]' | xargs)
    item_id=$(echo "$raw_id_from_yq" | tr -cd '[[:print:]]' | xargs)
    item_category=$(echo "$raw_category_from_yq" | tr -cd '[[:print:]]' | xargs)
    # Convert selected_by_default to a clean true/false string for reliable comparison
    selected_by_default_cleaned=$(echo "$raw_selected_by_default" | tr '[:upper:]' '[:lower:]' | xargs)

    log_debug "(Population): YAML: '$yaml_file', Cleaned Name: '$item_name', Cleaned ID: '$item_id', Cleaned Category: '$item_category', Cleaned SelectedByDefault: '$selected_by_default_cleaned'"
    
    if [[ -n "$item_name" && "$item_name" != "null" && -n "$item_id" && "$item_id" != "null" ]]; then
        all_item_names+=("$item_name")
        all_item_ids+=("$item_id")
        all_item_categories+=("$item_category")
        all_item_selected_by_default_flags+=("$selected_by_default_cleaned")
        all_categories_map["$item_category"]=1 # Store unique category names
        log_debug "(Population): Added '$item_name' (ID: '$item_id', Category: '$item_category') to arrays."
    else
        log_info "WARNING: Skipping '$yaml_file' as it's missing 'name' or 'id', or they are null after cleaning." >&2
    fi
done < <(find "$CONFIGS_DIR" -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) -print0)

if [ ${#all_item_names[@]} -eq 0 ]; then
    log_info "WARNING: No valid configuration items found in $CONFIGS_DIR to display in menu." >&2
    echo "STATUS:NO_ITEMS_FOUND"
    exit 0
fi

# --- Step 2: Get unique sorted categories (no explicit user selection of categories anymore) ---
unique_sorted_categories=()
for cat_key in "${(@k)all_categories_map}"; do unique_sorted_categories+=("$cat_key"); done
if [ ${#unique_sorted_categories[@]} -gt 0 ]; then
    temp_sorted_cats_str=$(printf "%s\n" "${unique_sorted_categories[@]}" | sort -u)
    unique_sorted_categories=(${(f)temp_sorted_cats_str})
fi

if [ ${#unique_sorted_categories[@]} -eq 0 ]; then
    log_info "WARNING: No categories found in any configuration items." >&2
    echo "STATUS:NO_CATEGORIES_FOUND"
    exit 0
fi

log_debug "Iterating through all available categories: ${unique_sorted_categories[*]}"

# --- Step 3: Loop through ALL available categories and let user pick items ---
overall_selected_item_ids_map=()
typeset -A overall_selected_item_ids_map # Associative array for final unique IDs

# The user_selected_categories array is now replaced by unique_sorted_categories directly.
for current_system_category_raw in "${unique_sorted_categories[@]}"; do
    current_system_category=$(echo "$current_system_category_raw" | xargs | tr -d \'\") # Clean the category name
    log_info "--- Presenting items for category: '$current_system_category' ---" >&2
    
    category_specific_item_names=()
    category_specific_item_ids=()
    category_specific_pre_selected_names_for_gum=() # Names to pass to gum --selected

    # Populate category_specific arrays
    for i in {1..${#all_item_names[@]}}; do
        log_debug "  [FilterLoop] Item ${i}: Name='${all_item_names[i]}', StoredCategory='${all_item_categories[i]}'"
        log_debug "  [FilterLoop] Comparing StoredCategory:'${all_item_categories[i]}' vs CurrentDisplayCategory:$current_system_category'"
        if [[ "${all_item_categories[i]}" == "$current_system_category" ]]; then
            log_debug "    MATCH! Adding Name='${all_item_names[i]}' (ID='${all_item_ids[i]}') to items for category '$current_system_category'."
            category_specific_item_names+=("${all_item_names[i]}")
            category_specific_item_ids+=("${all_item_ids[i]}")
            if [[ "${all_item_selected_by_default_flags[i]}" == "true" ]]; then
                log_debug "      Marking Name='${all_item_names[i]}' for pre-selection in '$current_system_category'."
                category_specific_pre_selected_names_for_gum+=("${all_item_names[i]}")
            fi
        fi
    done

    log_debug "[Pre-Gum] For category '$current_system_category', items collected: ${category_specific_item_names[*]}"
    log_debug "[Pre-Gum] For category '$current_system_category', pre-selected names: ${category_specific_pre_selected_names_for_gum[*]}"

    if [ ${#category_specific_item_names[@]} -eq 0 ]; then
        log_info "INFO: No items found in category '$current_system_category' to display. Skipping." >&2
        continue
    fi

    gum_choose_selected_arg=""
    if [ ${#category_specific_pre_selected_names_for_gum[@]} -gt 0 ]; then
      gum_choose_selected_arg="--selected=$(IFS=,; echo "${category_specific_pre_selected_names_for_gum[*]}")"
      log_debug "(Gum Args for '$current_system_category'): $gum_choose_selected_arg"
    fi

    # Modified header to suggest Esc can skip the category (gum default behavior if no selection)
    items_chosen_in_category_str=$(gum choose --no-limit --header "Category: '$current_system_category' (Space to toggle, Enter for selections, Esc to skip category)" "${category_specific_item_names[@]}" ${=gum_choose_selected_arg})

    if [ -z "$items_chosen_in_category_str" ]; then
        log_info "INFO: User skipped or selected no items from category '$current_system_category'." >&2
        continue
    fi

    while IFS= read -r selected_name_in_cat_raw; do
        selected_name_in_cat_cleaned=$(echo "$selected_name_in_cat_raw" | xargs)
        found_id_for_name=""
        for j in {1..${#category_specific_item_names[@]}}; do
            if [[ "${category_specific_item_names[j]}" == "$selected_name_in_cat_cleaned" ]]; then
                found_id_for_name="${category_specific_item_ids[j]}"
                overall_selected_item_ids_map["$found_id_for_name"]=1
                log_debug "(Item Marked): Name:'$selected_name_in_cat_cleaned', ID:'$found_id_for_name' (Cat:'$current_system_category') added to overall map."
                break
            fi
        done
        if [[ -z "$found_id_for_name" ]]; then
             log_info "WARNING: Could not map '$selected_name_in_cat_cleaned' to ID in '$current_system_category'." >&2
        fi
    done <<< "$items_chosen_in_category_str"

done # End of loop through all unique_sorted_categories

# --- Step 4: Final Output ---
final_unique_ids=()
for id_val in "${(@k)overall_selected_item_ids_map}"; do final_unique_ids+=("$id_val"); done

if [ ${#final_unique_ids[@]} -eq 0 ]; then
    log_info "INFO: No items were selected across all chosen categories." >&2
    echo "STATUS:NO_ITEMS_SELECTED_OVERALL"
    exit 0
fi

log_info "--- Final Item IDs For Processing ---" >&2
# The actual IDs for macsnap.sh are printed to stdout below.
# This log_info is just for menu_generator.sh's own log clarity.
for id_to_log in "${final_unique_ids[@]}"; do
    log_info "  ID: $id_to_log" >&2
done

# Output for macsnap.sh (stdout)
echo "Selected item IDs:"
# printf "%s\n" "${final_unique_ids[@]}"
for id_to_print in "${final_unique_ids[@]}"; do
    echo "$(echo "$id_to_print" | tr -cd '[[:print:]]' | xargs)" # Ensure IDs are clean
done

log_debug "Menu generator finished. Total unique items for processing: ${#final_unique_ids[@]}"
exit 0 