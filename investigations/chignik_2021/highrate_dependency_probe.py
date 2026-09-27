from __future__ import annotations
import json, pathlib, platform

OUT=pathlib.Path("artifacts/chignik_highrate_probe/DEPENDENCY_PROBE.json")
OUT.parent.mkdir(parents=True,exist_ok=True)
mods={}
for name in ["numpy","scipy","statsmodels","sklearn"]:
    try:
        m=__import__(name)
        mods[name]={"available":True,"version":getattr(m,"__version__",None)}
    except Exception as e:
        mods[name]={"available":False,"error":repr(e)}
report={"python":platform.python_version(),"modules":mods}
OUT.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
