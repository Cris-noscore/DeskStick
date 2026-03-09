import json
from pathlib import Path

# Salva em ~/.local/share/sticky-desktop/postits.json
# Funciona independente de onde o script é executado
DATA_DIR  = Path.home() / ".local" / "share" / "sticky-desktop" / "data"
DATA_FILE = DATA_DIR / "postits.json"


class Database:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not DATA_FILE.exists():
            DATA_FILE.write_text('{"postits": []}', encoding="utf-8")

    def save(self, data: dict):
        try:
            tmp = DATA_FILE.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(DATA_FILE)
        except Exception as e:
            print(f"[Database] Erro ao salvar: {e}")

    def load(self) -> dict:
        try:
            text = DATA_FILE.read_text(encoding="utf-8").strip()
            if not text:
                return {"postits": []}
            return json.loads(text)
        except Exception as e:
            print(f"[Database] Erro ao carregar: {e}")
            return {"postits": []}
