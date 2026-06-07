def get_default_style():
    return """
    QWidget {
        background-color: #f4f7fb;
        color: #102a43;
        font-family: 'Avenir Next', 'Segoe UI', sans-serif;
        font-size: 14px;
    }
    QMainWindow {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #fdf8f1,
            stop:0.55 #f4f7fb,
            stop:1 #eef3f9
        );
    }
    QLabel {
        color: #243b53;
    }
    QFrame {
        background-color: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 14px;
    }
    QListWidget, QTextEdit, QLineEdit, QComboBox, QSpinBox {
        background-color: #ffffff;
        color: #102a43;
        border: 1px solid #cfd9e5;
        border-radius: 10px;
        padding: 8px 10px;
        selection-background-color: #d6e8ff;
        selection-color: #102a43;
    }
    QListWidget::item {
        border-radius: 10px;
        margin: 3px 2px;
        padding: 8px 10px;
    }
    QListWidget::item:selected {
        background-color: #d6e8ff;
    }
    QPushButton {
        background-color: #1f7a57;
        color: #ffffff;
        border: 1px solid #1a6b4c;
        border-radius: 11px;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 600;
        min-height: 16px;
    }
    QPushButton:hover {
        background-color: #176547;
    }
    QPushButton:pressed {
        background-color: #0f5137;
    }
    QScrollBar:vertical {
        background: transparent;
        width: 12px;
        margin: 2px;
    }
    QScrollBar::handle:vertical {
        background: #b8c6d6;
        min-height: 28px;
        border-radius: 6px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    """


def get_dark_theme_style():
    return """
    QWidget {
        background-color: #0f1720;
        color: #d9e2ec;
        font-family: 'Avenir Next', 'Segoe UI', sans-serif;
        font-size: 14px;
    }
    QMainWindow {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #111b27,
            stop:0.55 #0f1720,
            stop:1 #162230
        );
    }
    QLabel {
        color: #c4d2df;
    }
    QFrame {
        background-color: #1b2633;
        border: 1px solid #2f3f52;
        border-radius: 14px;
    }
    QListWidget, QTextEdit, QLineEdit, QComboBox, QSpinBox {
        background-color: #1c2835;
        color: #e6edf4;
        border: 1px solid #304256;
        border-radius: 10px;
        padding: 8px 10px;
        selection-background-color: #274c77;
        selection-color: #f0f5fa;
    }
    QListWidget::item {
        border-radius: 10px;
        margin: 3px 2px;
        padding: 8px 10px;
    }
    QListWidget::item:selected {
        background-color: #274c77;
    }
    QPushButton {
        background-color: #d27a00;
        color: #f7fafc;
        border: 1px solid #b86900;
        border-radius: 11px;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 600;
        min-height: 16px;
    }
    QPushButton:hover {
        background-color: #b86900;
    }
    QPushButton:pressed {
        background-color: #9d5a00;
    }
    QScrollBar:vertical {
        background: transparent;
        width: 12px;
        margin: 2px;
    }
    QScrollBar::handle:vertical {
        background: #3a4d62;
        min-height: 28px;
        border-radius: 6px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    """


def get_main_menu_button_style():
    return """
    QPushButton {
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #1f7a57,
            stop:1 #176547
        );
        color: #ffffff;
        border: 1px solid #1a6b4c;
        border-radius: 14px;
        padding: 14px 20px;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.2px;
    }
    QPushButton:hover {
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #176547,
            stop:1 #0f5137
        );
    }
    QPushButton:pressed {
        background-color: #0f5137;
    }
    """


def get_button_style():
    return """
    QPushButton {
        background-color: #102a43;
        color: #f0f4f8;
        border: 1px solid #243b53;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #243b53;
    }
    QPushButton:pressed {
        background-color: #334e68;
    }
    """


def get_theme_button_style():
    return """
    QPushButton {
        background-color: rgba(16, 42, 67, 0.08);
        border: 1px solid rgba(16, 42, 67, 0.15);
        border-radius: 12px;
        font-size: 13px;
        font-weight: 700;
        padding: 5px;
        min-width: 28px;
        max-width: 28px;
        min-height: 28px;
        max-height: 28px;
    }
    QPushButton:hover {
        background-color: rgba(16, 42, 67, 0.15);
    }
    """
