import uuid
from datetime import datetime
from models.block import Block

COLORS = {
    "yellow": {"bg": "#FEF08A", "header": "#FDE047"},
    "green":  {"bg": "#BBF7D0", "header": "#86EFAC"},
    "blue":   {"bg": "#BFDBFE", "header": "#93C5FD"},
    "purple": {"bg": "#E9D5FF", "header": "#C4B5FD"},
    "red":    {"bg": "#FECACA", "header": "#FCA5A5"},
}

class PostIt:
    def __init__(self, title: str = "Nova Nota", color: str = "yellow",
                 x: int = 100, y: int = 100, postit_id: str = None,
                 created_at: str = None):
        self.id = postit_id or str(uuid.uuid4())[:8]
        self.title = title
        self.color = color
        self.x = x
        self.y = y
        self.created_at = created_at or datetime.now().isoformat()
        self.blocks: list[Block] = []

    def add_block(self, block: Block):
        self.blocks.append(block)

    def remove_block(self, block_id: str):
        self.blocks = [b for b in self.blocks if b.id != block_id]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "color": self.color,
            "x": self.x,
            "y": self.y,
            "created_at": self.created_at,
            "blocks": [b.to_dict() for b in self.blocks],
        }

    @staticmethod
    def from_dict(data: dict) -> "PostIt":
        pi = PostIt(
            title=data.get("title", "Nova Nota"),
            color=data.get("color", "yellow"),
            x=data.get("x", 100),
            y=data.get("y", 100),
            postit_id=data.get("id"),
            created_at=data.get("created_at"),
        )
        for b in data.get("blocks", []):
            pi.add_block(Block.from_dict(b))
        return pi
