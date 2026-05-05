from __future__ import annotations

from pathlib import Path
import re


DEFAULT_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"SCT[0-9A-Za-z_-]{12,}"),
    re.compile(r"SPT_[0-9A-Za-z_-]{12,}"),
    re.compile(r"AT_[0-9A-Za-z_-]{12,}"),
    re.compile(r"UID_[0-9A-Za-z_-]{12,}"),
]

ASSIGNMENT_PATTERN = re.compile(
    r"(?i)(api[_-]?key|secret|password|token|sendkey)\s*[:=]\s*['\"]?([^'\"\s#]+)"
)

PLACEHOLDER_VALUES = {
    "",
    "changeme",
    "change_me",
    "example",
    "placeholder",
    "replace_me",
    "your_token_here",
    "your_key_here",
}


def scan_path(root: Path | str) -> list[tuple[Path, int, str]]:
    root_path = Path(root).resolve()
    findings: list[tuple[Path, int, str]] = []
    for path in root_path.rglob("*"):
        if not path.is_file() or _skip(path, root_path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _is_placeholder_assignment(line):
                continue
            if _contains_secret(line):
                findings.append((path, line_number, line.strip()))
    return findings


def _skip(path: Path, root_path: Path) -> bool:
    root_level_skip = {
        ".git",
        ".venv",
        "bundle",
        "cache",
        "data",
        "downloads",
        "outputs",
        "vendor",
    }
    skip_anywhere = {
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
    }
    try:
        parts = path.resolve().relative_to(root_path).parts
    except ValueError:
        parts = path.parts
    if not parts:
        return False
    return parts[0] in root_level_skip or any(part in skip_anywhere for part in parts)


def _is_placeholder_assignment(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return False
    key, raw_value = stripped.split("=", 1)
    if not re.search(r"(?i)(api[_-]?key|secret|password|token|sendkey|spt|uid)", key):
        return False
    value = raw_value.split("#", 1)[0].strip().strip("'\"").lower()
    return value in PLACEHOLDER_VALUES


def _contains_secret(line: str) -> bool:
    if any(pattern.search(line) for pattern in DEFAULT_PATTERNS):
        return True
    match = ASSIGNMENT_PATTERN.search(line)
    if not match:
        return False
    value = match.group(2).strip().strip("'\"").lower()
    if value in PLACEHOLDER_VALUES:
        return False
    benign_prefixes = ("os.getenv(", "getenv(", "env.get(", "settings.", "config.")
    return not value.startswith(benign_prefixes)
