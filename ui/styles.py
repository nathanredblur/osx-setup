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
    layout: horizontal;
}

/* Category sidebar on the left */
#category-sidebar {
    width: 25%;
    padding: 1;
    border: round;
    margin-right: 1;
}

/* Main content area */
#content-area {
    padding: 0;
    width: 75%;
}

/* Search bar */
#search-bar {
    height: 3;
    margin-bottom: 1;
    border: round;
    padding: 0 1;
}

/* Item table - takes most of the space */
#item-table {
    height: 3fr;
    border: round;
    margin-bottom: 1;
    padding: 1;
}

/* Item detail panel - smaller */
#item-detail {
    height: 1fr;
    border: round;
    padding: 1;
    min-height: 8;
}

/* Control panel - compact height */
#control-panel {
    height: 3;
    margin: 1 0;
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