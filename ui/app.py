import sys
import os
import socket
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap, QColor, QKeySequence, QShortcut, QAction
from PyQt6.QtCore import Qt, QTimer

from core.postit_manager import PostItManager
from ui.postit_window import PostItWindow

SINGLE_INSTANCE_PORT = 47832


def _make_tray_icon() -> QIcon:
    px = QPixmap(32, 32)
    px.fill(QColor("#F5C842"))
    return QIcon(px)


MENU_STYLE = """
    QMenu { background: #1e1e28; color: #e8e8f0;
            border: 1px solid #2e2e38; border-radius: 8px; padding: 4px; }
    QMenu::item { padding: 8px 20px; border-radius: 4px; }
    QMenu::item:selected { background: #2e2e38; }
    QMenu::separator { height: 1px; background: #2e2e38; margin: 4px 0; }
"""


def is_already_running() -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", SINGLE_INSTANCE_PORT))
        s.listen(1)
        App._lock_socket = s
        return False
    except OSError:
        return True


class App(QApplication):
    _lock_socket = None

    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.setApplicationName("DeskStick")

        self.manager = PostItManager()
        self.windows: dict[str, PostItWindow] = {}

        self._build_tray()
        self._restore_windows()

        QTimer.singleShot(500, self._show_startup_message)

    def _show_startup_message(self):
        self.tray.showMessage(
            "DeskStick",
            "✅ DeskStick está rodando!\nClique com botão direito no ícone para o menu.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def _build_tray(self):
        self.tray = QSystemTrayIcon(_make_tray_icon(), self)
        self.tray.setToolTip("DeskStick — Clique direito para o menu")

        menu = QMenu()
        menu.setStyleSheet(MENU_STYLE)

        act_new  = QAction("📝  Nova nota", self)
        act_show = QAction("👁  Mostrar todas", self)
        act_hide = QAction("🙈  Ocultar todas", self)
        act_quit = QAction("✕  Sair", self)

        act_new.triggered.connect(self.new_postit)
        act_show.triggered.connect(self.show_all)
        act_hide.triggered.connect(self.hide_all)
        act_quit.triggered.connect(self.quit_app)

        menu.addAction(act_new)
        menu.addSeparator()
        menu.addAction(act_show)
        menu.addAction(act_hide)
        menu.addSeparator()
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.tray.contextMenu().popup(
                self.tray.geometry().center()
                if not self.tray.geometry().isNull()
                else self.screens()[0].geometry().center()
            )

    def _restore_windows(self):
        for pi in self.manager.postits:
            self._open_window(pi)

    def _open_window(self, postit):
        if postit.id in self.windows:
            self.windows[postit.id].show()
            return
        win = PostItWindow(postit, self.manager)
        win.deleted.connect(self._on_window_deleted)
        sc = QShortcut(QKeySequence("Ctrl+Y"), win)
        sc.activated.connect(self.new_postit)
        self.windows[postit.id] = win
        win.show()

    def _on_window_deleted(self, postit_id: str):
        self.windows.pop(postit_id, None)

    def new_postit(self):
        offset = (len(self.manager.postits) % 10) * 30
        pi = self.manager.create(x=120 + offset, y=120 + offset)
        self._open_window(pi)

    def show_all(self):
        for win in self.windows.values():
            win.show()

    def hide_all(self):
        for win in self.windows.values():
            win.hide()

    def quit_app(self):
        self.manager.save()
        if App._lock_socket:
            App._lock_socket.close()
        self.quit()
