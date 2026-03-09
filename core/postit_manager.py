from models.postit import PostIt
from models.block import Block
from storage.database import Database


class PostItManager:
    def __init__(self):
        self.db = Database()
        self.postits: list[PostIt] = []
        self._load()

    # ── LOAD / SAVE ──────────────────────────────────
    def _load(self):
        data = self.db.load()
        self.postits = [PostIt.from_dict(d) for d in data.get("postits", [])]

    def save(self):
        self.db.save({"postits": [p.to_dict() for p in self.postits]})

    # ── POSTIT CRUD ───────────────────────────────────
    def create(self, title: str = "Nova Nota", color: str = "yellow",
               x: int = 120, y: int = 120) -> PostIt:
        pi = PostIt(title=title, color=color, x=x, y=y)
        self.postits.append(pi)
        self.save()
        return pi

    def delete(self, postit_id: str):
        self.postits = [p for p in self.postits if p.id != postit_id]
        self.save()

    def update_title(self, postit_id: str, title: str):
        pi = self.get(postit_id)
        if pi:
            pi.title = title
            self.save()

    def update_color(self, postit_id: str, color: str):
        pi = self.get(postit_id)
        if pi:
            pi.color = color
            self.save()

    def update_position(self, postit_id: str, x: int, y: int):
        pi = self.get(postit_id)
        if pi:
            pi.x = x
            pi.y = y
            self.save()

    def get(self, postit_id: str) -> PostIt | None:
        return next((p for p in self.postits if p.id == postit_id), None)

    # ── BLOCK CRUD ────────────────────────────────────
    def add_block(self, postit_id: str, block_type: str, content: str = "") -> Block | None:
        pi = self.get(postit_id)
        if pi:
            b = Block(block_type=block_type, content=content)
            pi.add_block(b)
            self.save()
            return b
        return None

    def update_block(self, postit_id: str, block_id: str, content: str = None, checked: bool = None):
        pi = self.get(postit_id)
        if not pi:
            return
        for b in pi.blocks:
            if b.id == block_id:
                if content is not None:
                    b.content = content
                if checked is not None:
                    b.checked = checked
        self.save()

    def delete_block(self, postit_id: str, block_id: str):
        pi = self.get(postit_id)
        if pi:
            pi.remove_block(block_id)
            self.save()
