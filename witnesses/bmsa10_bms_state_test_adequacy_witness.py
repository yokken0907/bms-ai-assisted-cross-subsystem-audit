#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--source", type=Path, required=True)
a = p.parse_args()
root = a.source
h = (root / "src/app/application/bms/bms.h").read_text(encoding="utf-8")
c = (root / "src/app/application/bms/bms.c").read_text(encoding="utf-8")
t = (root / "tests/unit/app/application/bms/test_bms.c").read_text(encoding="utf-8")
y = (root / "conf/unit/app_project_posix.yml").read_text(encoding="utf-8")
states = sorted(set(re.findall(r"\bBMS_FSM_STATE_[A-Z0-9_]+\b", h)))
substates = sorted(set(re.findall(r"\bBMS_FSM_SUBSTATE_[A-Z0-9_]+\b", h)))
result = {
    "states_declared": len(states),
    "substates_declared": len(substates),
    "state_literals_in_test": sum(t.count(x) for x in states),
    "substate_literals_in_test": sum(t.count(x) for x in substates),
    "trigger_calls_in_test": t.count("BMS_Trigger();"),
    "test_functions": len(re.findall(r"^void test\w+\(", t, re.M)),
    "state_assignments_in_source": len(re.findall(r"bms_state\.state\s*=", c)),
    "substate_assignments_in_source": len(re.findall(r"bms_state\.substate\s*=", c)),
    "check_string_closed_assignments_in_source": len(re.findall(r"bms_state\.substate\s*=\s*BMS_FSM_SUBSTATE_CHECK_STRING_CLOSED", c)),
    "check_string_closed_literals_in_test": t.count("BMS_FSM_SUBSTATE_CHECK_STRING_CLOSED"),
    "two_string_test_define_for_bms": bool(re.search(r":/test_bms\.c/:\s*\n\s*- TEST_BS_NR_OF_STRINGS=2u", y)),
    "todos_in_test": t.count("TODO"),
}
result["pass"] = (
    result["states_declared"] == 13 and result["substates_declared"] == 34
    and result["state_literals_in_test"] == 0 and result["substate_literals_in_test"] == 0
    and result["trigger_calls_in_test"] == 3 and result["check_string_closed_assignments_in_source"] == 0
    and result["check_string_closed_literals_in_test"] == 0 and result["two_string_test_define_for_bms"]
)
print(json.dumps(result, sort_keys=True))
raise SystemExit(0 if result["pass"] else 1)
