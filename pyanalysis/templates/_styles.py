# Shared style constants for email templates
# All CSS is inline for maximum email client compatibility

# Font stack for Chinese and English
FONT_FAMILY = (
    "'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', "
    "Helvetica, Arial, sans-serif"
)

# Color palette
COLORS = {
    # Primary colors
    "primary": "#1890ff",
    "primary_dark": "#096dd9",

    # Severity colors
    "critical": "#ff4d4f",
    "critical_bg": "#fff2f0",
    "critical_border": "#ffccc7",
    "warning": "#faad14",
    "warning_bg": "#fffbe6",
    "warning_border": "#ffe58f",
    "info": "#1890ff",
    "info_bg": "#e6f7ff",
    "info_border": "#91d5ff",
    "success": "#52c41a",
    "success_bg": "#f6ffed",
    "success_border": "#b7eb8f",

    # Neutral colors
    "text_primary": "#333333",
    "text_secondary": "#666666",
    "text_muted": "#999999",
    "border": "#e8e8e8",
    "background": "#f5f5f5",
    "white": "#ffffff",

    # Table colors
    "table_header_bg": "#fafafa",
    "table_row_hover": "#f5f5f5",
    "table_highlight": "#fffbe6",
}

# Icon SVGs (inline for email compatibility)
# noqa: E501 - SVGs are intentionally long single-line strings for email compatibility
ICONS = {
    "info": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" stroke="#1890ff" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"></circle>'
        '<line x1="12" y1="16" x2="12" y2="12"></line>'
        '<line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
    ),
    "success": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" stroke="#52c41a" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>'
        '<polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
    ),
    "warning": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" stroke="#faad14" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 '
        '1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>'
        '<line x1="12" y1="9" x2="12" y2="13"></line>'
        '<line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
    ),
    "bell": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" stroke="#1890ff" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>'
        '<path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>'
    ),
    "critical": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" stroke="#ff4d4f" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"></circle>'
        '<line x1="15" y1="9" x2="9" y2="15"></line>'
        '<line x1="9" y1="9" x2="15" y2="15"></line></svg>'
    ),
}

# Common inline styles
STYLES = {
    "container": f'''
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        font-family: {FONT_FAMILY};
        font-size: 14px;
        line-height: 1.6;
        color: {COLORS["text_primary"]};
    '''.strip(),

    "card": f'''
        background-color: {COLORS["white"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        padding: 24px;
        margin: 16px 0;
    '''.strip(),

    "title": f'''
        font-size: 20px;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin: 0 0 16px 0;
        padding: 0;
    '''.strip(),

    "subtitle": f'''
        font-size: 14px;
        color: {COLORS["text_secondary"]};
        margin: 0 0 16px 0;
        padding: 0;
    '''.strip(),

    "content": f'''
        font-size: 14px;
        line-height: 1.8;
        color: {COLORS["text_primary"]};
        margin: 0 0 16px 0;
    '''.strip(),

    "button": f'''
        display: inline-block;
        padding: 10px 24px;
        background-color: {COLORS["primary"]};
        color: {COLORS["white"]};
        text-decoration: none;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
    '''.strip(),

    "footer": f'''
        font-size: 12px;
        color: {COLORS["text_muted"]};
        text-align: center;
        margin-top: 24px;
        padding-top: 16px;
        border-top: 1px solid {COLORS["border"]};
    '''.strip(),

    "table": '''
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
    '''.strip(),

    "th": f'''
        background-color: {COLORS["table_header_bg"]};
        border: 1px solid {COLORS["border"]};
        padding: 12px;
        text-align: left;
        font-weight: 600;
        font-size: 14px;
    '''.strip(),

    "td": f'''
        border: 1px solid {COLORS["border"]};
        padding: 12px;
        font-size: 14px;
    '''.strip(),

    "badge": '''
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    '''.strip(),

    "progress_bar_container": f'''
        width: 100%;
        height: 8px;
        background-color: {COLORS["border"]};
        border-radius: 4px;
        overflow: hidden;
        margin: 8px 0;
    '''.strip(),

    "progress_bar_fill": f'''
        height: 100%;
        background-color: {COLORS["primary"]};
        border-radius: 4px;
    '''.strip(),
}
