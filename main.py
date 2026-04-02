import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QShortcut
from PyQt5.QtGui import QFont, QTextCharFormat, QKeySequence
from PyQt5.QtCore import Qt

class AphoroxApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aphorox")
        self.setGeometry(100, 100, 750, 520)

        layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Escribe... Doble Enter para nueva entrada")

        layout.addWidget(self.text_area)
        self.setLayout(layout)

        # Archivo
        self.file_path = self.get_today_file()

        # Fuente global
        self.font_size = 14
        self.fonts = ["Helvetica", "Times New Roman", "Menlo"]
        self.current_font_index = 0

        self.apply_global_font()

        # Control Enter
        self.enter_count = 0

        # Atajos
        self.setup_shortcuts()

        # Key handling limpio (no rompe acentos)
        self.text_area.keyPressEvent = self.handle_keypress

        # Cargar archivo
        self.load_today_file()

    # ---------------------------
    # Fuente global (ZOOM)
    # ---------------------------
    def apply_global_font(self):
        font = QFont(self.fonts[self.current_font_index], self.font_size)
        self.text_area.setFont(font)

    def increase_font(self):
        self.font_size += 1
        self.apply_global_font()

    def decrease_font(self):
        self.font_size = max(8, self.font_size - 1)
        self.apply_global_font()

    # ---------------------------
    # Estilo por selección
    # ---------------------------
    def apply_format(self, format_func):
        cursor = self.text_area.textCursor()
        if not cursor.hasSelection():
            return

        fmt = QTextCharFormat()
        format_func(fmt)

        cursor.mergeCharFormat(fmt)
        self.text_area.mergeCurrentCharFormat(fmt)

    def toggle_italic(self):
        def fmt(f):
            f.setFontItalic(not self.text_area.fontItalic())
        self.apply_format(fmt)

    def switch_font(self):
        self.current_font_index = (self.current_font_index + 1) % len(self.fonts)
        new_font = self.fonts[self.current_font_index]

        def fmt(f):
            f.setFontFamily(new_font)

        self.apply_format(fmt)

    # ---------------------------
    # Timestamp (DISEÑO NUEVO)
    # ---------------------------
    def insert_timestamp(self):
        time_str = datetime.now().strftime("%H:%M")
        timestamp = f"\n── {time_str} ──\n\n"

        cursor = self.text_area.textCursor()
        cursor.insertText(timestamp)

    # ---------------------------
    # Archivos
    # ---------------------------
    def get_today_file(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join("journal", f"journal_{date_str}.txt")

    def load_today_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.text_area.setText(f.read())

    def save_file(self):
        with open(self.file_path, "w") as f:
            f.write(self.text_area.toPlainText())

    # ---------------------------
    # Teclado (sin romper macOS)
    # ---------------------------
    def handle_keypress(self, event):
        if event.key() == Qt.Key_Return:
            self.enter_count += 1

            if self.enter_count == 2:
                self.insert_timestamp()
                self.enter_count = 0
                return
        else:
            self.enter_count = 0

        QTextEdit.keyPressEvent(self.text_area, event)
        self.save_file()

    # ---------------------------
    # Atajos
    # ---------------------------
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl++"), self, self.increase_font)
        QShortcut(QKeySequence("Ctrl+-"), self, self.decrease_font)
        QShortcut(QKeySequence("Ctrl+I"), self, self.toggle_italic)
        QShortcut(QKeySequence("Ctrl+T"), self, self.switch_font)

    # ---------------------------
    # Cierre seguro
    # ---------------------------
    def closeEvent(self, event):
        self.save_file()
        event.accept()

# ---------------------------
# Run
# ---------------------------
app = QApplication(sys.argv)
window = AphoroxApp()
window.show()
sys.exit(app.exec_())