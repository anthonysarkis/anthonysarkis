import json
from pathlib import Path

from .lines import RULES_FINGERPRINT, LineCount


def load_counts(path: Path) -> dict[str, LineCount]:
    if not path.exists():
        return {}

    saved = json.loads(path.read_text(encoding="utf-8"))
    if saved.get("rules") != RULES_FINGERPRINT:
        return {}

    return {sha: LineCount(added, removed) for sha, (added, removed) in saved["commits"].items()}


def save_counts(path: Path, counts: dict[str, LineCount]) -> None:
    rows = [f'    "{sha}": [{count.added}, {count.removed}]' for sha, count in sorted(counts.items())]
    entries = ",\n".join(rows)
    text = f'{{\n  "rules": "{RULES_FINGERPRINT}",\n  "commits": {{\n{entries}\n  }}\n}}\n'
    path.write_text(text, encoding="utf-8")
