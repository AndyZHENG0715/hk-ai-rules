# Hong Kong AI Routing Rules for Sing-box / VilaNet / Clash

[English](README.md) | [繁體中文](README.zh-Hant.md) | [简体中文](README.zh-Hans.md)

An automated, optimized rule-set tailored for users and developers in **Hong Kong**.

---

## 🎯 Background & Objectives

In Hong Kong, the internet environment has unique characteristics:
- **Direct Access**: Most global services (Google, YouTube, Discord, X, GitHub, Steam, Wikipedia, etc.) and mainland services work directly with native high speed and low latency.
- **Geoblocked AI Services**: Certain AI platforms (such as **ChatGPT / OpenAI, Claude / Anthropic, Sora, Google AI Studio, NotebookLM, Groq**) restrict or block access from Hong Kong IP addresses, necessitating a proxy.
- **Accessible AI Services**: Other popular AI platforms (such as **xAI Grok, Gemini Web, GitHub Copilot, Perplexity, Cursor, Poe, Mistral**) are fully accessible in Hong Kong and should connect directly for optimal speed and reliability.

### The Problem
Most proxy clients (including VilaNet and standard Sing-box configurations) set unmatched traffic to route through `proxy` as the final fallback (`route.final: "proxy"`). Without specialized rules, normal international traffic (Discord, X, Cloudflare CDN, Steam, etc.) gets mistakenly routed through the proxy node, wasting proxy bandwidth and degrading latency.

### The Solution
This repository maintains automated rule-sets updated daily via GitHub Actions:
1. **`hk-ai-blocked.srs`**: Contains all AI services geoblocked in Hong Kong. **Action: PROXY**
2. **`hk-ai-whitelist.srs`**: Contains all AI services natively accessible in Hong Kong. **Action: DIRECT**
3. **`hk-direct-fallback.srs`**: Catch-all direct fallback ensuring all general Hong Kong internet traffic stays direct. **Action: DIRECT**

---

## 📦 Rule-Sets Overview

| Rule Set | Target Traffic | Recommended Outbound | Raw Link |
| :--- | :--- | :---: | :--- |
| **`hk-ai-blocked.srs`** | ChatGPT, Claude, Sora, AI Studio, NotebookLM, Groq, etc. | **`proxy`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-blocked.srs) |
| **`hk-ai-whitelist.srs`** | Grok, Gemini Web, Copilot, Perplexity, Cursor, etc. | **`direct`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-whitelist.srs) |
| **`hk-direct-fallback.srs`** | All other general internet traffic | **`direct`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-direct-fallback.srs) |

> [!TIP]
> `hk-ai-blocked.srs` already has the Hong Kong whitelisted domains subtracted from upstream community AI rules. You only need **`hk-ai-blocked`** (Proxy) and **`hk-direct-fallback`** (Direct) to achieve complete, conflict-free split routing!

---

## 🚀 Quick Setup Guide

### 1. VilaNet Client Setup

In VilaNet (Windows / macOS / Linux / Android / iOS):

1. Go to **Settings** -> **Routing Rules / Custom Rules**.
2. Enable **Use Custom Rules** and **Use Remote Rule-Sets**.
3. Add the following rules in order:

| # | Rule-Set URL | Inverse | Action | Description |
| :-: | :--- | :-: | :-: | :--- |
| 1 | `https://raw.githubusercontent.com/vilavpn/meta-rules-dat/sing/geo/geosite/category-ads-all.srs` | Off | `block` | (Optional) Block Ads |
| 2 | `https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-blocked.srs` | Off | **`proxy`** | Blocked AI services |
| 3 | `https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-direct-fallback.srs` | Off | **`direct`** | Hong Kong Direct Fallback |

4. Save settings and reconnect.

---

### 2. Sing-box Standard Configuration

Add the remote rule-sets to your `route.rule_set`:

```json
{
  "route": {
    "rule_set": [
      {
        "tag": "hk-ai-blocked",
        "type": "remote",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-blocked.srs",
        "download_detour": "direct"
      },
      {
        "tag": "hk-direct-fallback",
        "type": "remote",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-direct-fallback.srs",
        "download_detour": "direct"
      }
    ],
    "rules": [
      {
        "rule_set": "hk-ai-blocked",
        "outbound": "proxy"
      },
      {
        "rule_set": "hk-direct-fallback",
        "outbound": "direct"
      }
    ],
    "final": "proxy"
  }
}
```

---

### 3. Clash / Mihomo Configuration

```yaml
rule-providers:
  hk-ai-blocked:
    type: http
    behavior: domain
    format: yaml
    url: "https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-blocked.json"
    path: ./ruleset/hk-ai-blocked.yaml
    interval: 86400

rules:
  - RULE-SET,hk-ai-blocked,PROXY
  - MATCH,DIRECT
```

---

## 🛠️ Automated Daily Builds

This repository automatically synchronizes with upstream rules every day at 06:00 HKT (UTC 22:00) using GitHub Actions:
- Upstream: `vilavpn/meta-rules-dat` (`category-ai-!cn.json`)
- Additions: `supplement.json`
- HK Whitelist Filter: `scripts/hk-whitelist.txt`

### How to Contribute
If an AI service opens access to Hong Kong, or if a new blocked AI service appears:
1. Fork this repository.
2. Edit [`scripts/hk-whitelist.txt`](scripts/hk-whitelist.txt) to add or remove domains.
3. Submit a Pull Request. Once merged, GitHub Actions automatically compiles and publishes the new `.srs` files.

---

## 📄 License

MIT License. Feel free to use, share, and integrate into your personal or organizational configurations.
