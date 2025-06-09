"""
Minimal Layout Styles for MacSnap UI

Using native tokyo-night theme with only structural layout styles.
Colors and theming are handled by Textual's built-in theme system.
"""

# Minimal layout styles - only structure, no colors
LAYOUT_CSS = """
/* Main layout structure */
#main-container {
    height: 1fr;
}

#content-area {
    padding: 0;
}

/* Modal screens structure */
#progress-container, #results-container {
    width: 80%;
    height: 80%;
    margin: 2;
}

#progress-title, #results-title {
    text-style: bold;
    text-align: center;
    margin: 1;
}

#progress-log-container {
    height: 60%;
    margin: 1;
}

#progress-log {
    padding: 1;
}
"""

# Backward compatibility
TOKYO_NIGHT_CSS = LAYOUT_CSS
GLOBAL_CSS = LAYOUT_CSS 