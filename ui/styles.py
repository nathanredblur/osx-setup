"""
Global CSS Styles for MacSnap UI

This file contains only global layout styles and shared theme colors.
Component-specific styles are now defined within each component.
"""

# Global layout and theme styles
GLOBAL_CSS = """
/* Tokyo Night Global Theme */
Screen {
    background: #1a1b26;
    color: #c0caf5;
}

/* Header styling */
Header {
    background: #16161e;
    color: #7aa2f7;
    text-style: bold;
    dock: top;
    height: 3;
    content-align: center middle;
    border: round #3b4261;
    margin-bottom: 1;
}

/* Main layout containers */
#main-container {
    background: #1a1b26;
    height: 1fr;
}

#content-area {
    background: #1a1b26;
    padding: 0;
}

/* Footer styling */
Footer {
    background: #16161e;
    color: #c0caf5;
    padding: 0 1;
    height: 3;
    border: round #3b4261;
}

Footer > .footer--highlight {
    background: #7aa2f7;
    color: #1a1b26;
}

Footer > .footer--key {
    color: #7aa2f7;
    text-style: bold;
}

/* Modal screens */
#progress-container, #results-container {
    width: 80%;
    height: 80%;
    margin: 2;
    background: #16161e;
    border: round #7aa2f7;
}

#progress-title, #results-title {
    text-style: bold;
    text-align: center;
    margin: 1;
    color: #7aa2f7;
}

#progress-log-container {
    height: 60%;
    border: round #3b4261;
    margin: 1;
    background: #1a1b26;
}

#progress-log {
    padding: 1;
    color: #c0caf5;
}

/* Data table styling (kept for backward compatibility) */
DataTable {
    background: #1a1b26;
    color: #c0caf5;
}

DataTable > .datatable--header {
    background: #16161e;
    color: #7aa2f7;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #7aa2f7;
    color: #1a1b26;
}
"""

# Backward compatibility
TOKYO_NIGHT_CSS = GLOBAL_CSS 