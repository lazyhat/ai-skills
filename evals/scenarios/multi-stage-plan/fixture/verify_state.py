from pathlib import Path


assert Path("alpha.txt").read_text(encoding="utf-8").strip() == "done"
assert Path("beta.txt").read_text(encoding="utf-8").strip() == "done"
