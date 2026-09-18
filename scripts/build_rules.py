#!/usr/bin/env python3
"""Build Sing-box rule-sets for Hong Kong AI routing.

Generates:
1. hk-ai-blocked.srs / .json: All AI services blocked in Hong Kong (ChatGPT, Claude, AI Studio, NotebookLM, Groq, etc.) -> PROXY
2. hk-ai-whitelist.srs / .json: AI services accessible in Hong Kong (Grok, Gemini Web, Copilot, Perplexity, etc.) -> DIRECT
3. hk-direct-fallback.srs / .json: Direct fallback for all normal internet traffic in Hong Kong -> DIRECT
"""
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

UPSTREAM_URL = "https://raw.githubusercontent.com/vilavpn/meta-rules-dat/sing/geo/geosite/category-ai-%21cn.json"


def load_patterns(path):
    patterns = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if line:
                patterns.append(line)
    return patterns


def domain_matches(domain, patterns):
    for p in patterns:
        if p.startswith("*") and p.endswith("*"):
            if p[1:-1] in domain:
                return True
        elif p.startswith("*"):
            if domain.endswith(p[1:]):
                return True
        elif p.endswith("*"):
            if domain.startswith(p[:-1]):
                return True
        elif domain == p or p in domain:
            return True
    return False


def fetch_upstream(local_fallback=None):
    try:
        req = urllib.request.Request(UPSTREAM_URL, headers={"User-Agent": "hk-ai-rules-builder"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        if local_fallback and os.path.exists(local_fallback):
            print(f"Warning: Failed to fetch upstream ({e}), using local fallback: {local_fallback}")
            with open(local_fallback, "r", encoding="utf-8") as f:
                return json.load(f)
        raise


def compile_srs(sing_box_bin, json_data, output_srs):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
        tmp_name = f.name
    try:
        subprocess.run([sing_box_bin, "rule-set", "compile", "--output", output_srs, tmp_name], check=True)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    whitelist_txt = os.path.join(base_dir, "scripts", "hk-whitelist.txt")
    supplement_json = os.path.join(base_dir, "supplement.json")
    local_fallback = os.path.join(os.path.dirname(base_dir), "category-ai-not-cn.json")
    sing_box_bin = "sing-box"

    # Find sing-box binary
    if not subprocess.run(["which", "sing-box"], capture_output=True).returncode == 0:
        local_sb = os.path.join(os.path.dirname(base_dir), "sing-box")
        if os.path.exists(local_sb):
            sing_box_bin = local_sb
        else:
            raise FileNotFoundError("sing-box binary not found in PATH or parent directory")

    patterns = load_patterns(whitelist_txt)
    upstream_data = fetch_upstream(local_fallback)

    # Collect domains and regexes
    upstream_exact = set()
    upstream_suffix = set()
    upstream_regex = []

    for rule in upstream_data.get("rules", []):
        upstream_exact.update(rule.get("domain", []))
        upstream_suffix.update(rule.get("domain_suffix", []))
        r = rule.get("domain_regex")
        if r:
            if isinstance(r, list):
                upstream_regex.extend(r)
            else:
                upstream_regex.append(r)

    # Load supplement domains
    supplement_suffix = set()
    if os.path.exists(supplement_json):
        with open(supplement_json, "r", encoding="utf-8") as f:
            supp_data = json.load(f)
            for rule in supp_data.get("rules", []):
                supplement_suffix.update(rule.get("domain_suffix", []))

    all_suffix = upstream_suffix | supplement_suffix

    # Partition into whitelist (HK direct) and blocked (HK proxy)
    wl_exact = set()
    wl_suffix = set()
    blocked_exact = set()
    blocked_suffix = set()
    blocked_regex = list(upstream_regex)

    for d in sorted(upstream_exact):
        if domain_matches(d, patterns):
            wl_exact.add(d)
        else:
            blocked_exact.add(d)

    for d in sorted(all_suffix):
        if domain_matches(d, patterns):
            wl_suffix.add(d)
        else:
            blocked_suffix.add(d)

    # 1. Build hk-ai-blocked (needs proxy in HK)
    blocked_rule = {}
    if blocked_exact:
        blocked_rule["domain"] = sorted(blocked_exact)
    if blocked_suffix:
        blocked_rule["domain_suffix"] = sorted(blocked_suffix)
    if blocked_regex:
        blocked_rule["domain_regex"] = blocked_regex
    blocked_payload = {"version": 2, "rules": [blocked_rule]}

    blocked_json_path = os.path.join(base_dir, "hk-ai-blocked.json")
    blocked_srs_path = os.path.join(base_dir, "hk-ai-blocked.srs")
    with open(blocked_json_path, "w", encoding="utf-8") as f:
        json.dump(blocked_payload, f, ensure_ascii=False, indent=2)
    compile_srs(sing_box_bin, blocked_payload, blocked_srs_path)
    print(f"Compiled hk-ai-blocked.srs: {len(blocked_exact)} exact, {len(blocked_suffix)} suffix domains (PROXY)")

    # 2. Build hk-ai-whitelist (accessible in HK)
    wl_rule = {}
    if wl_exact:
        wl_rule["domain"] = sorted(wl_exact)
    if wl_suffix:
        wl_rule["domain_suffix"] = sorted(wl_suffix)
    wl_payload = {"version": 2, "rules": [wl_rule]}

    wl_json_path = os.path.join(base_dir, "hk-ai-whitelist.json")
    wl_srs_path = os.path.join(base_dir, "hk-ai-whitelist.srs")
    with open(wl_json_path, "w", encoding="utf-8") as f:
        json.dump(wl_payload, f, ensure_ascii=False, indent=2)
    compile_srs(sing_box_bin, wl_payload, wl_srs_path)
    print(f"Compiled hk-ai-whitelist.srs: {len(wl_exact)} exact, {len(wl_suffix)} suffix domains (DIRECT)")

    # Backwards compatibility: ai-whitelist.srs
    compile_srs(sing_box_bin, wl_payload, os.path.join(base_dir, "ai-whitelist.srs"))

    # 3. Build hk-direct-fallback (all-direct)
    fallback_payload = {
        "version": 2,
        "rules": [
            {"domain_regex": [".*"]},
            {"ip_cidr": ["0.0.0.0/0", "::/0"]}
        ]
    }
    fallback_json_path = os.path.join(base_dir, "hk-direct-fallback.json")
    fallback_srs_path = os.path.join(base_dir, "hk-direct-fallback.srs")
    with open(fallback_json_path, "w", encoding="utf-8") as f:
        json.dump(fallback_payload, f, ensure_ascii=False, indent=2)
    compile_srs(sing_box_bin, fallback_payload, fallback_srs_path)
    print("Compiled hk-direct-fallback.srs (DIRECT)")

    # Backwards compatibility: all-direct.srs
    compile_srs(sing_box_bin, fallback_payload, os.path.join(base_dir, "all-direct.srs"))

    # Backwards compatibility: ai-supplement.srs
    if os.path.exists(supplement_json):
        with open(supplement_json, "r", encoding="utf-8") as f:
            supp_data = json.load(f)
        compile_srs(sing_box_bin, supp_data, os.path.join(base_dir, "ai-supplement.srs"))


if __name__ == "__main__":
    main()
