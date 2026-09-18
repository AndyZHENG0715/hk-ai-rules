# 香港專用 AI 分流規則集 (Sing-box / VilaNet / Clash)

[English](README.md) | [繁體中文](README.zh-Hant.md) | [简体中文](README.zh-Hans.md)

專為**香港**地區用戶與開發者設計的自動化 Sing-box 規則集（Rule-set）。

---

## 🎯 背景與設計初衷

在香港，網絡環境具有鮮明的特殊性：
- **原生外網優勢**：絕大部分海外服務（Google、YouTube、Discord、X、GitHub、Steam 等）及內地服務均可直接高速低延遲訪問。
- **特定 AI 地區封鎖**：部分主流 AI 服務（如 **ChatGPT / OpenAI、Claude / Anthropic、Sora、Google AI Studio、NotebookLM、Groq** 等）不對香港 IP 提供服務，必須經過節點代理（Proxy）。
- **部分 AI 已對港開放**：部分知名 AI 服務（如 **xAI Grok、Gemini 網頁版、GitHub Copilot、Perplexity、Cursor、Poe、Mistral** 等）在香港完全可直接訪問，應當直連（Direct）以確保最快速度與穩定性。

### 遇到的痛點
大多數代理客戶端（如 VilaNet 及標準 Sing-box 配置）通常以 `proxy` 作為未匹配流量的兜底策略（`route.final: "proxy"`）。在缺少精確規則覆蓋時，正常的海外網站（如 Discord、X、Cloudflare CDN、Steam）會被迫全部走代理節點，白白浪費節點流量並大幅增加延遲。

### 解決方案
本專案利用 GitHub Actions 每日自動拉取上游社區 AI 規則，並依據香港實際網絡情況進行精準差集計算：
1. **`hk-ai-blocked.srs`**：包含所有在香港受限、必須走代理的 AI 服務。**策略：PROXY**
2. **`hk-ai-whitelist.srs`**：包含在香港可直接使用的 AI 服務白名單。**策略：DIRECT**
3. **`hk-direct-fallback.srs`**：全網直連兜底規則，確保非 AI 的所有海外與本地流量均保持直連。**策略：DIRECT**

---

## 📦 規則集列表

| 規則集名稱 | 目標流量 | 建議策略 | 訂閱連結 (Raw) |
| :--- | :--- | :---: | :--- |
| **`hk-ai-blocked.srs`** | ChatGPT、Claude、Sora、AI Studio、NotebookLM、Groq 等 | **`proxy`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-blocked.srs) |
| **`hk-ai-whitelist.srs`** | Grok、Gemini 網頁版、Copilot、Perplexity、Cursor 等 | **`direct`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-whitelist.srs) |
| **`hk-direct-fallback.srs`** | 香港本地及所有其他常規互聯網流量（兜底） | **`direct`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-direct-fallback.srs) |

> [!TIP]
> `hk-ai-blocked.srs` 在編譯時已自動剔除香港可用 AI，因此在 VilaNet 中僅需配置 **`hk-ai-blocked`**（Proxy）與 **`hk-direct-fallback`**（Direct）兩條自定義規則即可完美分流，免除任何規則順序衝突！

---

## 🚀 快速配置教學

### 1. VilaNet 客戶端配置

在 VilaNet（Windows / macOS / Linux / Android / iOS）：

1. 打開 **設定** -> **自定義規則 / 路由規則**。
2. 開啟 **使用自定義規則** 以及 **使用遠程規則集**。
3. 依序新增以下規則：

| 序號 | 規則集 URL | 反選 (Inverse) | 動作 (Action) | 說明 |
| :-: | :--- | :-: | :-: | :--- |
| 1 | `https://raw.githubusercontent.com/vilavpn/meta-rules-dat/sing/geo/geosite/category-ads-all.srs` | 關閉 | `block` | (可選) 廣告攔截 |
| 2 | `https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-blocked.srs` | 關閉 | **`proxy`** | 香港受限 AI 服務走代理 |
| 3 | `https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-direct-fallback.srs` | 關閉 | **`direct`** | 香港全網直連兜底 |

4. 保存並重新連接即可。

---

### 2. Sing-box 標準配置

在 Sing-box 的 `config.json` 中添加：

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

### 3. Clash / Mihomo 配置

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

## 🛠️ 自動化每日構建

本倉庫每天香港時間 06:00 (UTC 22:00) 自動觸發 GitHub Actions 執行：
- 上游源：`vilavpn/meta-rules-dat` (`category-ai-!cn.json`)
- 自定義補充：`supplement.json`
- 香港白名單過濾：`scripts/hk-whitelist.txt`

### 如何貢獻
若某項 AI 服務開始對香港開放，或有新增的不支援香港的 AI 服務：
1. Fork 本倉庫。
2. 編輯 [`scripts/hk-whitelist.txt`](scripts/hk-whitelist.txt) 新增或移除對應域名/關鍵字。
3. 提交 Pull Request，合併後 GitHub Actions 會自動編譯發布最新的 `.srs` 規則檔案。

---

## 📄 開源許可

本專案採用 MIT 許可證。歡迎自由使用、轉載與集成。
