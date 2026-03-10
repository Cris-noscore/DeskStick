#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import App, is_already_running


def main():
    if is_already_running():
        from PyQt6.QtWidgets import QApplication, QMessageBox
        tmp = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setWindowTitle("DeskStick")
        msg.setText("DeskStick já está rodando!\nProcure o ícone 📝 na barra do sistema.")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
        sys.exit(0)

    app = App(sys.argv)

    if "--new" in sys.argv:
        app.new_postit()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
