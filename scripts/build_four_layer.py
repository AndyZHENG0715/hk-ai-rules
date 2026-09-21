#!/usr/bin/env python3
import json, os, shutil, subprocess, urllib.request, tempfile
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
SB=Path(shutil.which("sing-box") or (BASE.parent/"sing-box"))
if not SB.exists():
    raise FileNotFoundError("sing-box executable not found on PATH or repository parent")
UP="https://raw.githubusercontent.com/vilavpn/meta-rules-dat/sing/geo/geosite/category-ai-%21cn.json"
def compile(data,out):
    with tempfile.NamedTemporaryFile("w",suffix=".json",delete=False) as f:
        json.dump(data,f,ensure_ascii=False); n=f.name
    try: subprocess.run([str(SB),"rule-set","compile","--output",str(out),n],check=True)
    finally: os.unlink(n)
def load(path): return json.loads(Path(path).read_text())
def main():
    try:
        with urllib.request.urlopen(UP,timeout=30) as r: upstream=json.load(r)
    except Exception:
        upstream=load(BASE.parent/"category-ai-not-cn.json")
    compile(upstream,BASE/"hk-ai-upstream.srs")
    (BASE/"hk-ai-upstream.json").write_text(json.dumps(upstream,ensure_ascii=False,indent=2)+chr(10))
    supplement=load(BASE/"supplement.json"); compile(supplement,BASE/"ai-supplement.srs")
    whitelist=load(BASE/"hk-ai-whitelist.json"); compile(whitelist,BASE/"hk-ai-whitelist.srs")
    fallback=load(BASE/"hk-direct-fallback.json"); compile(fallback,BASE/"hk-direct-fallback.srs")
    print("Layer order: hk-ai-whitelist (DIRECT) -> ai-supplement (PROXY) -> hk-ai-upstream (PROXY) -> hk-direct-fallback (DIRECT)")
if __name__=="__main__": main()
