from __future__ import annotations

import argparse
import inspect
import itertools
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ARTIFACTS_DIR = ROOT / "artifacts"

from tools import TOOL_FUNCTIONS, _hospital, load_tool_declarations, to_openai_tools
from tools.dispatch_mission.tool import MISSION_TYPES, PRIORITIES
from tools.get_robot_status.tool import CHECKS
from tools.list_robots.tool import STATUSES


AMR_TOOLS = [
    "clarify",
    "get_robot_status",
    "list_robots",
    "get_location_info",
    "get_route_info",
    "dispatch_mission",
    "cancel_mission",
]


class Report:
    def __init__(self) -> None:
        self.passed = 0
        self.failed: list[str] = []

    def check(self, label: str, ok: bool, detail: Any = "") -> None:
        if ok:
            self.passed += 1
            print(f"PASS {label}")
        else:
            self.failed.append(label)
            print(f"FAIL {label}  {detail}")


def check_declarations(report: Report, declarations: list[dict[str, Any]]) -> None:
    print("\n== tools.yaml vs registry ==")
    names = [item["name"] for item in declarations]
    report.check("declares exactly the 7 AMR tools", sorted(names) == sorted(AMR_TOOLS), names)
    for item in declarations:
        name = item["name"]
        func = TOOL_FUNCTIONS.get(name)
        report.check(f"{name}: registered", func is not None)
        if func is None:
            continue
        signature = inspect.signature(func).parameters
        properties = item.get("parameters", {}).get("properties", {})
        report.check(f"{name}: parameters match signature", set(properties) == set(signature),
                     f"yaml={sorted(properties)} code={sorted(signature)}")
        required = set(item.get("parameters", {}).get("required", []))
        report.check(f"{name}: required is subset of parameters", required <= set(properties), sorted(required))
        for param, spec in properties.items():
            if "default" not in spec or param not in signature:
                continue
            code_default = signature[param].default
            code_default = [] if code_default is None else code_default
            report.check(f"{name}.{param}: default matches code", spec["default"] == code_default,
                         f"yaml={spec['default']!r} code={code_default!r}")
    report.check("converts to provider tool format", len(to_openai_tools(declarations)) == len(declarations))


def check_enums(report: Report, declarations: list[dict[str, Any]]) -> None:
    print("\n== enums vs code and data ==")
    properties = {item["name"]: item["parameters"]["properties"] for item in declarations}
    location_ids = [item["location_id"] for item in _hospital.load("locations")["locations"]]
    pairs = {
        "get_robot_status.check": ("get_robot_status", "check", CHECKS),
        "list_robots.status": ("list_robots", "status", STATUSES),
        "dispatch_mission.mission_type": ("dispatch_mission", "mission_type", MISSION_TYPES),
        "dispatch_mission.priority": ("dispatch_mission", "priority", PRIORITIES),
        "get_location_info.location_id": ("get_location_info", "location_id", location_ids),
        "get_route_info.destination_id": ("get_route_info", "destination_id", location_ids),
        "dispatch_mission.destination_id": ("dispatch_mission", "destination_id", location_ids),
    }
    for label, (tool, param, allowed) in pairs.items():
        declared = properties.get(tool, {}).get(param, {}).get("enum")
        report.check(f"{label}: enum matches", declared is not None and sorted(declared) == sorted(allowed),
                     f"yaml={declared} code/data={list(allowed)}")


def check_data(report: Report) -> None:
    print("\n== hospital_data consistency ==")
    robots = _hospital.by_id(_hospital.load("robots")["robots"], "robot_id")
    locations = _hospital.by_id(_hospital.load("locations")["locations"], "location_id")
    routes = _hospital.load("routes")
    missions = _hospital.by_id(_hospital.load("missions")["missions"], "mission_id")
    elevators = _hospital.by_id(routes["elevators"], "elevator_id")
    segments = _hospital.by_id(routes["blocked_segments"], "segment_id")

    for robot in robots.values():
        rid = robot["robot_id"]
        report.check(f"{rid}: id format", bool(_hospital.ROBOT_ID_PATTERN.fullmatch(rid)))
        location = locations.get(robot["location_id"])
        report.check(f"{rid}: location exists and floor matches",
                     location is not None and location["floor"] == robot["floor"], robot["location_id"])
        mission_id = robot["current_mission_id"]
        report.check(f"{rid}: on_mission iff it has an in-progress mission",
                     (robot["status"] == "on_mission") == bool(mission_id)
                     and (not mission_id or (missions.get(mission_id, {}).get("status") == "in_progress"
                                             and missions[mission_id]["robot_id"] == rid)))
    for mission in missions.values():
        report.check(f"{mission['mission_id']}: robot and locations exist",
                     mission["robot_id"] in robots
                     and mission["origin_id"] in locations
                     and mission["destination_id"] in locations)

    route_pairs = [frozenset((route["from"], route["to"])) for route in routes["routes"]]
    expected_pairs = {frozenset(pair) for pair in itertools.combinations(locations, 2)}
    report.check("routes cover every location pair once",
                 len(route_pairs) == len(set(route_pairs)) and set(route_pairs) == expected_pairs)
    for route in routes["routes"]:
        label = f"route {route['from']}-{route['to']}"
        floors = {locations[route["from"]]["floor"], locations[route["to"]]["floor"]}
        elevator = elevators.get(route["elevator"]) if route["elevator"] else None
        if len(floors) == 1:
            ok = route["elevator"] is None
        else:
            ok = elevator is not None and elevator["status"] == "available" and floors <= set(elevator["floors"])
        report.check(f"{label}: elevator serves both floors", ok, route["elevator"])
        report.check(f"{label}: blocked segments exist", all(s in segments for s in route["blocked_segments"]))


# (label, tool, kwargs, expected subset of the result)
BEHAVIOR_CASES: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = [
    ("status reads one robot", "get_robot_status", {"robot_id": "AMR-02", "check": "location"}, {"robot_id": "AMR-02", "check": "location"}),
    ("status normalizes id and check", "get_robot_status", {"robot_id": " amr-04 ", "check": "MISSION"}, {"robot_id": "AMR-04", "check": "mission"}),
    ("status rejects AMR-2", "get_robot_status", {"robot_id": "AMR-2"}, {"error": "invalid_robot_id"}),
    ("status rejects non-string id", "get_robot_status", {"robot_id": 2}, {"error": "invalid_robot_id"}),
    ("status unknown robot", "get_robot_status", {"robot_id": "AMR-09"}, {"error": "robot_not_found"}),
    ("status unknown check", "get_robot_status", {"robot_id": "AMR-01", "check": "speed"}, {"error": "invalid_check"}),
    ("list all robots", "list_robots", {}, {"count": 5}),
    ("list idle with battery >= 20", "list_robots", {"status": "idle", "min_battery": 20}, {"count": 2}),
    ("list rejects unknown status", "list_robots", {"status": "busy"}, {"error": "invalid_status"}),
    ("list rejects battery 150", "list_robots", {"min_battery": 150}, {"error": "invalid_min_battery"}),
    ("list rejects boolean battery", "list_robots", {"min_battery": True}, {"error": "invalid_min_battery"}),
    ("location reads ICU", "get_location_info", {"location_id": "icu"}, {"location_id": "ICU"}),
    ("location rejects free text", "get_location_info", {"location_id": "Lab B"}, {"error": "location_not_found"}),
    ("route PHARMACY -> LAB_B", "get_route_info", {"robot_id": "AMR-02", "destination_id": "LAB_B"}, {"from_location_id": "PHARMACY", "eta_min": 6, "elevator": "A"}),
    ("route works in reverse direction", "get_route_info", {"robot_id": "AMR-04", "destination_id": "PHARMACY"}, {"eta_min": 6}),
    ("route when already at destination", "get_route_info", {"robot_id": "AMR-05", "destination_id": "DOCK_1"}, {"eta_min": 0, "distance_m": 0}),
    ("route rejects free-text destination", "get_route_info", {"robot_id": "AMR-02", "destination_id": "Lab B"}, {"error": "location_not_found"}),
    ("dispatch rejects bad robot id", "dispatch_mission", {"robot_id": "AMR2", "destination_id": "LAB_B", "confirmed": True}, {"error": "invalid_robot_id"}),
    ("dispatch rejects free-text destination", "dispatch_mission", {"robot_id": "AMR-02", "destination_id": "Lab B", "confirmed": True}, {"error": "invalid_destination_id"}),
    ("dispatch rejects bad mission type", "dispatch_mission", {"robot_id": "AMR-02", "destination_id": "LAB_B", "mission_type": "drive", "confirmed": True}, {"error": "invalid_mission_type"}),
    ("dispatch rejects bad priority", "dispatch_mission", {"robot_id": "AMR-02", "destination_id": "LAB_B", "priority": "asap", "confirmed": True}, {"error": "invalid_priority"}),
    ("dispatch unknown robot", "dispatch_mission", {"robot_id": "AMR-09", "destination_id": "LAB_B", "confirmed": True}, {"error": "robot_not_found"}),
    ("dispatch return_to_base must target DOCK_1", "dispatch_mission", {"robot_id": "AMR-01", "destination_id": "ER", "mission_type": "return_to_base", "confirmed": True}, {"error": "invalid_destination_for_mission_type"}),
    ("dispatch blocks restricted ICU", "dispatch_mission", {"robot_id": "AMR-01", "destination_id": "ICU", "confirmed": True}, {"error": "restricted_destination"}),
    ("dispatch blocks OR_1", "dispatch_mission", {"robot_id": "AMR-01", "destination_id": "OR_1", "confirmed": True}, {"error": "restricted_destination"}),
    ("dispatch blocks robot in E-STOP", "dispatch_mission", {"robot_id": "AMR-03", "destination_id": "LAB_B", "confirmed": True}, {"error": "robot_unavailable", "error_codes": ["E_STOP_ACTIVE"]}),
    ("dispatch blocks robot on mission", "dispatch_mission", {"robot_id": "AMR-04", "destination_id": "LAB_B", "confirmed": True}, {"error": "robot_unavailable", "current_mission_id": "MS-0012"}),
    ("dispatch blocks low battery", "dispatch_mission", {"robot_id": "AMR-05", "destination_id": "ER", "confirmed": True}, {"error": "low_battery"}),
    ("dispatch without confirmation", "dispatch_mission", {"robot_id": "AMR-02", "destination_id": "LAB_B"}, {"status": "needs_confirmation"}),
    ("dispatch string 'true' is not confirmation", "dispatch_mission", {"robot_id": "AMR-02", "destination_id": "LAB_B", "confirmed": "true"}, {"status": "needs_confirmation"}),
    ("cancel rejects bad id", "cancel_mission", {"mission_id": "MS-12", "confirmed": True}, {"error": "invalid_mission_id"}),
    ("cancel unknown mission", "cancel_mission", {"mission_id": "MS-0999", "confirmed": True}, {"error": "mission_not_found"}),
    ("cancel completed mission", "cancel_mission", {"mission_id": "MS-0011", "confirmed": True}, {"error": "mission_not_cancellable"}),
    ("cancel without confirmation", "cancel_mission", {"mission_id": "MS-0012"}, {"status": "needs_confirmation"}),
    ("clarify pauses for the operator", "clarify", {"question": "Robot nào?", "response_type": "choice"}, {"awaiting_user": True}),
]

WRITE_CASES: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = [
    ("dispatch creates mission", "dispatch_mission", {"robot_id": "amr-02", "destination_id": "lab_b", "confirmed": True}, {"status": "created", "mission_id": "MS-0013", "robot_id": "AMR-02", "destination_id": "LAB_B"}),
    ("dispatch return_to_base ignores low battery", "dispatch_mission", {"robot_id": "AMR-05", "destination_id": "DOCK_1", "mission_type": "return_to_base", "confirmed": True}, {"status": "created", "mission_id": "MS-0014"}),
    ("cancel in-progress mission", "cancel_mission", {"mission_id": "ms-0012", "confirmed": True}, {"status": "cancelled", "robot_id": "AMR-04"}),
    ("cancel mission created at runtime", "cancel_mission", {"mission_id": "MS-0013", "confirmed": True}, {"status": "cancelled", "robot_id": "AMR-02"}),
]


def run_cases(report: Report, cases: list[tuple[str, str, dict[str, Any], dict[str, Any]]]) -> None:
    for label, tool, kwargs, expected in cases:
        result = TOOL_FUNCTIONS[tool](**kwargs)
        mismatches = {key: (value, result.get(key)) for key, value in expected.items() if result.get(key) != value}
        report.check(f"{tool}: {label}", not mismatches, f"{mismatches} -> {result}")


def check_behavior(report: Report) -> None:
    print("\n== tool behavior ==")
    original_dir = _hospital.MISSION_DIR
    with tempfile.TemporaryDirectory() as temp:
        _hospital.MISSION_DIR = Path(temp) / "missions"
        try:
            run_cases(report, BEHAVIOR_CASES)
            report.check("no mission file written by rejected or unconfirmed actions", not _hospital.MISSION_DIR.exists())
            run_cases(report, WRITE_CASES)
            robot = TOOL_FUNCTIONS["get_robot_status"](robot_id="AMR-02")["robot"]
            report.check("fleet state still read from seed snapshot after writes", robot["status"] == "idle", robot)
            written = sorted(path.name for path in _hospital.MISSION_DIR.iterdir())
            report.check("only expected mission records written",
                         written == ["MS-0012.cancelled.json", "MS-0013.cancelled.json", "MS-0013.json", "MS-0014.json"], written)
        finally:
            _hospital.MISSION_DIR = original_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline smoke test for AMR tool declarations, mock data and tool behavior.")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    args = parser.parse_args()

    report = Report()
    declarations = load_tool_declarations(args.tools)
    check_declarations(report, declarations)
    check_enums(report, declarations)
    check_data(report)
    check_behavior(report)

    print(f"\n{report.passed} passed, {len(report.failed)} failed")
    if report.failed:
        raise SystemExit("Smoke test failed: " + "; ".join(report.failed))


if __name__ == "__main__":
    main()
