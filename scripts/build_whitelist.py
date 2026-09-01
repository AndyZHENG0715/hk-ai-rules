#!/usr/bin/env python3
"""从上游 category-ai-!cn.json 提取香港可用 AI 服务的域名，生成白名单 srs。
用法: python3 build_whitelist.py <hk-whitelist.txt> <output.srs>
hk-whitelist.txt 每行一个关键字/域名，匹配上游 !cn 中的条目即加入白名单。
"""
import json, subprocess, sys, tempfile, os

def load_patterns(path):
    return [l.split('#')[0].strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('#')]

def matches(domain, patterns):
    for p in patterns:
        if p.startswith('*') and p.endswith('*'):
            if p[1:-1] in domain: return True
        elif p.startswith('*'):
            if domain.endswith(p[1:]): return True
        elif p.endswith('*'):
            if domain.startswith(p[:-1]): return True
        elif domain == p or p in domain:
            return True
    return False

def main():
    patterns_file, out_srs = sys.argv[1], sys.argv[2]
    patterns = load_patterns(patterns_file)

    # 拉取上游
    import urllib.request
    url = "https://raw.githubusercontent.com/vilavpn/meta-rules-dat/sing/geo/geosite/category-ai-%21cn.json"
    data = json.load(urllib.request.urlopen(url, timeout=30))

    # 收集匹配的域名
    matched = set()
    for rule in data['rules']:
        for key in ('domain', 'domain_suffix'):
            for d in rule.get(key, []):
                if matches(d, patterns):
                    matched.add(d)

    # 生成 sing-box JSON
    rule = {}
    if matched:
        rule['domain_suffix'] = sorted(matched)
    payload = {"version": 2, "rules": [rule]}
    print(f'白名单域名: {len(matched)} 个')
    for d in sorted(matched): print(f'  {d}')

    # 编译 srs
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(payload, f, ensure_ascii=False)
        tmp = f.name
    subprocess.run(['sing-box', 'rule-set', 'compile', '--output', out_srs, tmp], check=True)
    os.unlink(tmp)
    print(f'生成 {out_srs}')

if __name__ == '__main__':
    main()
