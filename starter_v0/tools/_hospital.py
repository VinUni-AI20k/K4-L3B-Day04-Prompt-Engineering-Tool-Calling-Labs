from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools._shared import ROOT


DATA_DIR = ROOT / "hospital_data"
# Runtime action log. Robot state is always read from the seed snapshot so every
# eval run starts from the same fleet state; files here never change it.
MISSION_DIR = ROOT / "missions"
ROBOT_ID_PATTERN = re.compile(r"^AMR-\d{2}$")
MISSION_ID_PATTERN = re.compile(r"^MS-\d{4}$")
MISSION_FILE_PATTERN = re.compile(r"^(MS-\d{4})\.json$")


def load(name: str) -> dict[str, Any]:
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


def by_id(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {item[key]: item for item in items}


def fail(tool: str, code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"tool": tool, "error": code, "message": message, **extra}


def normalize_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip().upper()


def normalize_choice(value: Any, default: str) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip().lower() or default


def find_route(routes: dict[str, Any], origin: str, destination: str) -> dict[str, Any] | None:
    return next((route for route in routes["routes"] if {route["from"], route["to"]} == {origin, destination}), None)


def known_missions() -> dict[str, dict[str, Any]]:
    missions = by_id(load("missions")["missions"], "mission_id")
    if MISSION_DIR.is_dir():
        for path in sorted(MISSION_DIR.iterdir()):
            match = MISSION_FILE_PATTERN.fullmatch(path.name)
            if match and match.group(1) not in missions:
                missions[match.group(1)] = json.loads(path.read_text(encoding="utf-8"))
    return missions


def next_mission_id() -> str:
    highest = max(int(mission_id[3:]) for mission_id in known_missions())
    return f"MS-{highest + 1:04d}"


def write_mission_record(filename: str, payload: dict[str, Any]) -> Path:
    MISSION_DIR.mkdir(parents=True, exist_ok=True)
    path = MISSION_DIR / filename
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
