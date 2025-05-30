#!/bin/zsh

# MacSnap Logger Utility

# Centralized logging functions. Uses Gum for styling if available.

_log_gum_style_available() {
    command -v gum &> /dev/null
}

# log_info "Message"
# log_info "PREFIX: Message"
log_info() {
    local message="$1"
    local prefix="INFO:"
    local color="#00FFFF" # Default: Electric Blue for INFO

    # Check if message contains a known prefix to adjust color/prefix
    if [[ "$message" == SUCCESS:* ]]; then
        prefix="SUCCESS:"
        color="#00FF00" # Neon Green
        message="${message#SUCCESS: }"
    elif [[ "$message" == WARNING:* ]]; then
        prefix="WARNING:"
        color="#FFFF00" # Yellow
        message="${message#WARNING: }"
    elif [[ "$message" == ERROR:* ]]; then
        prefix="ERROR:"
        color="#FF0000" # Red
        message="${message#ERROR: }"
    elif [[ "$message" == DEBUG:* ]]; then # Allow log_info to also handle explicit DEBUG prefixes if needed
        prefix="DEBUG:"
        color="#FF00FF" # Neon Pink
        message="${message#DEBUG: }"
    elif [[ "$message" == FATAL:* ]]; then
        prefix="FATAL:"
        color="#FF0000" # Red, same as error but distinct prefix
        message="${message#FATAL: }"
    fi

    if _log_gum_style_available; then
        gum style --foreground "$color" -- "$prefix $message"
    else
        echo "$prefix $message"
    fi
}

# log_debug "Message"
log_debug() {
    if [[ "${MACSNAP_DEBUG}" == "true" ]]; then
        local message="$1"
        local prefix="DEBUG:"
        local color="#FF00FF" # Neon Pink for DEBUG

        if _log_gum_style_available; then
            # Send to stderr so it doesn't interfere with script output capture
            gum style --foreground "$color" "$prefix" "$message" >&2
        else
            echo "$prefix $message" >&2
        fi
    fi
}

# Example usage (uncomment to test directly):
# MACSNAP_DEBUG=true
# log_info "This is an info message."
# log_info "SUCCESS: Operation was successful."
# log_info "WARNING: Something might be wrong."
# log_info "ERROR: An error occurred."
# log_debug "This is a debug message, will only show if MACSNAP_DEBUG=true."
# MACSNAP_DEBUG=false
# log_debug "This debug message will not show." 