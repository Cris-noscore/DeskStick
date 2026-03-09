from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor, QKeySequence, QShortcut, QAction

from core.postit_manager import PostItManager
from ui.postit_window import PostItWindow


def _make_tray_icon() -> QIcon:
    px = QPixmap(32, 32)
    px.fill(QColor("#F5C842"))
    return QIcon(px)


class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        self.manager = PostItManager()
        self.windows: dict[str, PostItWindow] = {}

        self._build_tray()
        self._restore_windows()

    def _build_tray(self):
        self.tray = QSystemTrayIcon(_make_tray_icon(), self)
        self.tray.setToolTip("Sticky Desktop")

        menu = QMenu()

        act_new  = QAction("📝  Novo Post-it", self)
        act_show = QAction("👁  Mostrar todos", self)
        act_hide = QAction("🙈  Ocultar todos", self)
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
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.new_postit()

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
        """Remove a janela do dicionário quando nota é excluída."""
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
        self.quit()
