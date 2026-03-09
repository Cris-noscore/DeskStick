from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMenu, QSizePolicy, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QCursor, QDesktopServices, QKeySequence, QShortcut

from models.postit import PostIt, COLORS
from models.block import Block


BLOCK_ICONS = {
    "text":      "📝",
    "checklist": "☐",
    "link":      "🔗",
    "comment":   "💬",
}


class BlockWidget(QWidget):
    deleted = pyqtSignal(str)
    changed = pyqtSignal(str, str, object)

    def __init__(self, block: Block, parent=None):
        super().__init__(parent)
        self.block = block
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        if self.block.type == "checklist":
            self.cb = QCheckBox()
            self.cb.setChecked(self.block.checked)
            self.cb.stateChanged.connect(self._on_check)
            layout.addWidget(self.cb)
        else:
            icon = QLabel(BLOCK_ICONS.get(self.block.type, "📝"))
            icon.setFixedWidth(18)
            layout.addWidget(icon)

        if self.block.type == "link":
            self._build_link_row(layout)
        else:
            self.edit = QLineEdit(self.block.content)
            self.edit.setPlaceholderText("Digite aqui…")
            self.edit.setFrame(False)
            self.edit.setStyleSheet("background: transparent; border: none;")
            self.edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.edit.textChanged.connect(self._on_text)
            layout.addWidget(self.edit)

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(18, 18)
        btn_del.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #888; font-size: 10px; }"
            "QPushButton:hover { color: #e00; }"
        )
        btn_del.clicked.connect(lambda: self.deleted.emit(self.block.id))
        layout.addWidget(btn_del)

    def _build_link_row(self, layout):
        self.edit = QLineEdit(self.block.content)
        self.edit.setPlaceholderText("https://…")
        self.edit.setFrame(False)
        self.edit.setStyleSheet("background: transparent; border: none; color: #1a56db;")
        self.edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.edit.textChanged.connect(self._on_text)
        layout.addWidget(self.edit)

        btn_open = QPushButton("↗")
        btn_open.setFixedSize(22, 22)
        btn_open.setToolTip("Abrir no navegador")
        btn_open.setStyleSheet(
            "QPushButton { background: rgba(26,86,219,0.12); border: none; border-radius: 4px;"
            "color: #1a56db; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background: rgba(26,86,219,0.30); }"
        )
        btn_open.clicked.connect(self._open_link)
        layout.addWidget(btn_open)

    def _open_link(self):
        url = self.edit.text().strip()
        if not url:
            return
        if not url.startswith(("http://", "https://", "ftp://")):
            url = "https://" + url
        QDesktopServices.openUrl(QUrl(url))

    def _on_check(self, state):
        self.changed.emit(self.block.id, "checked", bool(state))

    def _on_text(self, text):
        self.changed.emit(self.block.id, "content", text)


class PostItWindow(QWidget):
    # Sinal com postit_id — deletar definitivamente
    deleted  = pyqtSignal(str)
    modified = pyqtSignal(str)

    def __init__(self, postit: PostIt, manager, parent=None):
        super().__init__(parent)
        self.postit  = postit
        self.manager = manager
        self._drag_pos = None
        self._block_widgets: dict[str, BlockWidget] = {}

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMinimumWidth(240)
        self.setMaximumWidth(320)
        self.move(postit.x, postit.y)

        self._build_ui()
        self._apply_color(postit.color)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # HEADER
        self.header = QWidget()
        self.header.setFixedHeight(34)
        hlay = QHBoxLayout(self.header)
        hlay.setContentsMargins(8, 0, 6, 0)
        hlay.setSpacing(6)

        hlay.addWidget(QLabel("📌"))

        self.title_edit = QLineEdit(self.postit.title)
        self.title_edit.setFrame(False)
        self.title_edit.setStyleSheet("background: transparent; border: none; font-weight: bold;")
        self.title_edit.textChanged.connect(self._on_title_changed)
        hlay.addWidget(self.title_edit)

        btn_color = QPushButton("🎨")
        btn_color.setFixedSize(24, 24)
        btn_color.setStyleSheet(
            "QPushButton{background:transparent;border:none;}"
            "QPushButton:hover{background:rgba(0,0,0,0.1);border-radius:4px;}"
        )
        btn_color.clicked.connect(self._show_color_menu)
        hlay.addWidget(btn_color)

        # ✕ agora DELETA a nota definitivamente
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet(
            "QPushButton{background:transparent;border:none;font-weight:bold;}"
            "QPushButton:hover{background:rgba(200,0,0,0.2);border-radius:4px;}"
        )
        btn_close.clicked.connect(self._on_delete)
        hlay.addWidget(btn_close)

        root.addWidget(self.header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(0,0,0,0.15);")
        root.addWidget(line)

        # BODY
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(8, 6, 8, 4)
        self.body_layout.setSpacing(2)

        for block in self.postit.blocks:
            self._add_block_widget(block)

        root.addWidget(self.body)

        # FOOTER
        footer = QWidget()
        flay = QHBoxLayout(footer)
        flay.setContentsMargins(8, 2, 8, 6)
        flay.addStretch()

        btn_add = QPushButton("＋")
        btn_add.setFixedSize(26, 26)
        btn_add.setStyleSheet(
            "QPushButton{background:rgba(0,0,0,0.15);border:none;border-radius:13px;font-weight:bold;}"
            "QPushButton:hover{background:rgba(0,0,0,0.28);}"
        )
        btn_add.clicked.connect(self._show_add_menu)
        flay.addWidget(btn_add)

        root.addWidget(footer)

    def _add_block_widget(self, block: Block):
        bw = BlockWidget(block, self)
        bw.deleted.connect(self._on_block_deleted)
        bw.changed.connect(self._on_block_changed)
        self._block_widgets[block.id] = bw
        self.body_layout.addWidget(bw)
        self.adjustSize()

    def _apply_color(self, color: str):
        self.postit.color = color
        c = COLORS.get(color, COLORS["yellow"])
        self.setStyleSheet(f"""
            PostItWindow {{
                background: {c['bg']};
                border-radius: 10px;
                border: 1px solid rgba(0,0,0,0.15);
            }}
        """)
        self.header.setStyleSheet(f"""
            background: {c['header']};
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        """)
        self.body.setStyleSheet(f"background: {c['bg']};")

    def _show_color_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu{background:#fff;border:1px solid #ddd;border-radius:8px;padding:4px;}"
            "QMenu::item{padding:6px 16px;border-radius:4px;}"
            "QMenu::item:selected{background:#f0f0f0;}"
        )
        for name, label in [("yellow","🟡 Amarelo"),("green","🟢 Verde"),
                             ("blue","🔵 Azul"),("purple","🟣 Roxo"),("red","🔴 Vermelho")]:
            act = menu.addAction(label)
            act.triggered.connect(lambda _, n=name: self._change_color(n))
        menu.exec(QCursor.pos())

    def _change_color(self, color: str):
        self._apply_color(color)
        self.manager.update_color(self.postit.id, color)

    def _show_add_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu{background:#1e1e28;color:#e8e8f0;border:1px solid #2e2e38;"
            "border-radius:8px;padding:4px;}"
            "QMenu::item{padding:8px 16px;border-radius:4px;}"
            "QMenu::item:selected{background:#2e2e38;}"
        )
        for btype, label in [("text","📝  Texto livre"),("checklist","☑  Checklist"),
                              ("link","🔗  Link"),("comment","💬  Comentário")]:
            act = menu.addAction(label)
            act.triggered.connect(lambda _, t=btype: self._add_new_block(t))
        menu.exec(QCursor.pos())

    def _add_new_block(self, block_type: str):
        block = self.manager.add_block(self.postit.id, block_type)
        if block:
            self._add_block_widget(block)

    def _on_title_changed(self, text: str):
        self.manager.update_title(self.postit.id, text)

    def _on_block_deleted(self, block_id: str):
        bw = self._block_widgets.pop(block_id, None)
        if bw:
            self.body_layout.removeWidget(bw)
            bw.deleteLater()
        self.manager.delete_block(self.postit.id, block_id)
        self.adjustSize()

    def _on_block_changed(self, block_id: str, field: str, value):
        if field == "content":
            self.manager.update_block(self.postit.id, block_id, content=value)
        elif field == "checked":
            self.manager.update_block(self.postit.id, block_id, checked=value)

    def _on_delete(self):
        """Pergunta confirmação antes de excluir a nota."""
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Excluir nota")
        msg.setText(f"Tem certeza que deseja excluir <b>{self.postit.title}</b>?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg.button(QMessageBox.StandardButton.Yes).setText("Sim, excluir")
        msg.button(QMessageBox.StandardButton.Cancel).setText("Cancelar")
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.manager.delete(self.postit.id)
            self.deleted.emit(self.postit.id)
            self.close()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            new_pos = e.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)
            self.postit.x = new_pos.x()
            self.postit.y = new_pos.y()

    def mouseReleaseEvent(self, e):
        if self._drag_pos:
            self.manager.update_position(self.postit.id, self.postit.x, self.postit.y)
            self._drag_pos = None
