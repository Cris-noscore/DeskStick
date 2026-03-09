import uuid

BLOCK_TYPES = ["text", "checklist", "link", "comment"]

class Block:
    def __init__(self, block_type: str, content: str = "", checked: bool = False, block_id: str = None):
        self.id = block_id or str(uuid.uuid4())[:8]
        self.type = block_type  # text | checklist | link | comment
        self.content = content
        self.checked = checked  # only used for checklist

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "checked": self.checked,
        }

    @staticmethod
    def from_dict(data: dict) -> "Block":
        return Block(
            block_type=data.get("type", "text"),
            content=data.get("content", ""),
            checked=data.get("checked", False),
            block_id=data.get("id"),
        )
