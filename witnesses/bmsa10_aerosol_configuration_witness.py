#!/usr/bin/env python3
import argparse, importlib, json, sys, types
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--source", type=Path, required=True)
a = p.parse_args()
sys.dont_write_bytecode = True
tool_dir = (a.source / "tools/waf-tools").resolve()
sys.path.insert(0, str(tool_dir))
waflib = types.ModuleType("waflib")
configure = types.ModuleType("waflib.Configure")
node = types.ModuleType("waflib.Node")
class ConfigurationContext: pass
class Node: pass
def conf(function): return function
configure.ConfigurationContext = ConfigurationContext
configure.conf = conf
node.Node = Node
sys.modules.update({"waflib": waflib, "waflib.Configure": configure, "waflib.Node": node})
base = importlib.import_module("bms_config_validator_base")
validator = importlib.import_module("bms_config_validator")

validation = []
for sensor_type in ("can", "pwm", "typo", ""):
    try:
        sensor = base.AerosolSensor("honeywell", "bas6c-x00", sensor_type)
        validation.append({"type": sensor_type, "accepted": True, "stored_type": sensor.type})
    except Exception as exc:
        validation.append({"type": sensor_type, "accepted": False, "exception": type(exc).__name__})
try:
    base.AerosolSensor("honeywell", "unsupported", "can")
    unsupported_model_rejected = False
except base.InvalidConfigurationError:
    unsupported_model_rejected = True

class Env:
    def __init__(self, manufacturer="", model=""):
        self.FOXBMS_AS_MANUFACTURER = manufacturer
        self.FOXBMS_AS_MODEL = model
class Context:
    def __init__(self, manufacturer="", model=""):
        self.env = Env(manufacturer, model)
        self.defines = []
    def define(self, name, value, quote=False):
        self.defines.append(name)
    def is_aerosol_sensor_honeywell_bas6c_x00(self):
        return validator.is_aerosol_sensor_honeywell_bas6c_x00(self)

fresh = Context()
validator.set_aerosol_sensor(fresh, base.AerosolSensor("honeywell", "bas6c-x00", "can"))
stale = Context("honeywell", "bas6c-x00")
validator.set_aerosol_sensor(stale, base.AerosolSensor(None, None, None))
route_macro = "FOXBMS_AS_HONEYWELL_BAS6C_X00"
result = {
    "validation_matrix": validation,
    "unsupported_model_rejected": unsupported_model_rejected,
    "fresh_valid_route_defines": fresh.defines,
    "fresh_valid_route_macro_emitted": route_macro in fresh.defines,
    "stale_honeywell_to_none_defines": stale.defines,
    "stale_honeywell_to_none_route_macro_emitted": route_macro in stale.defines,
    "fresh_final_env": [fresh.env.FOXBMS_AS_MANUFACTURER, fresh.env.FOXBMS_AS_MODEL],
    "stale_final_env": [stale.env.FOXBMS_AS_MANUFACTURER, stale.env.FOXBMS_AS_MODEL],
}
accepted = {row["type"]: row["accepted"] for row in validation}
result["pass"] = (
    accepted.get("can") and accepted.get("pwm") and accepted.get("typo") and accepted.get("")
    and unsupported_model_rejected and not result["fresh_valid_route_macro_emitted"]
    and result["stale_honeywell_to_none_route_macro_emitted"]
)
print(json.dumps(result, sort_keys=True))
raise SystemExit(0 if result["pass"] else 1)
