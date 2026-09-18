# 香港专属 AI 分流规则集 (Sing-box / VilaNet / Clash)

[English](README.md) | [繁體中文](README.zh-Hant.md) | [简体中文](README.zh-Hans.md)

专为**香港**地区用户与开发者设计的自动化 Sing-box 规则集（Rule-set）。

---

## 🎯 背景与设计初衷

在香港，网络环境具有鲜明的特殊性：
- **原生外网优势**：绝大多数海外服务（Google、YouTube、Discord、X、GitHub、Steam 等）及国内服务均可直接高速低延迟访问。
- **特定 AI 地区封锁**：部分主流 AI 服务（如 **ChatGPT / OpenAI、Claude / Anthropic、Sora、Google AI Studio、NotebookLM、Groq** 等）不对香港 IP 提供服务，必须经过节点代理（Proxy）。
- **部分 AI 已对港开放**：部分知名 AI 服务（如 **xAI Grok、Gemini 网页版、GitHub Copilot、Perplexity、Cursor、Poe、Mistral** 等）在香港完全可直接访问，应当直连（Direct）以确保最快速度与稳定性。

### 遇到的痛点
大多数代理客户端（如 VilaNet 及标准 Sing-box 配置）通常以 `proxy` 作为未匹配流量的兜底策略（`route.final: "proxy"`）。在缺少精确规则覆盖时，正常的海外网站（如 Discord、X、Cloudflare CDN、Steam）会被迫全部走代理节点，白白浪费节点流量并大幅增加延迟。

### 解决方案
本项目利用 GitHub Actions 每日自动拉取上游社区 AI 规则，并依据香港实际网络情况进行精准差集计算：
1. **`hk-ai-blocked.srs`**：包含所有在香港受限、必须走代理的 AI 服务。**策略：PROXY**
2. **`hk-ai-whitelist.srs`**：包含在香港可直接使用的 AI 服务白名单。**策略：DIRECT**
3. **`hk-direct-fallback.srs`**：全网直连兜底规则，确保非 AI 的所有海外与本地流量均保持直连。**策略：DIRECT**

---

## 📦 规则集列表

| 规则集名称 | 目标流量 | 建议策略 | 订阅链接 (Raw) |
| :--- | :--- | :---: | :--- |
| **`hk-ai-blocked.srs`** | ChatGPT、Claude、Sora、AI Studio、NotebookLM、Groq 等 | **`proxy`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-blocked.srs) |
| **`hk-ai-whitelist.srs`** | Grok、Gemini 网页版、Copilot、Perplexity、Cursor 等 | **`direct`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-whitelist.srs) |
| **`hk-direct-fallback.srs`** | 香港本地及所有其他常规互联网流量（兜底） | **`direct`** | [`Raw .srs`](https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-direct-fallback.srs) |

> [!TIP]
> `hk-ai-blocked.srs` 在编译时已自动剔除香港可用 AI，因此在 VilaNet 中仅需配置 **`hk-ai-blocked`**（Proxy）与 **`hk-direct-fallback`**（Direct）两条自定义规则即可完美分流，免除任何规则顺序冲突！

---

## 🚀 快速配置教学

### 1. VilaNet 客户端配置

在 VilaNet（Windows / macOS / Linux / Android / iOS）：

1. 打开 **设置** -> **自定义规则 / 路由规则**。
2. 开启 **使用自定义规则** 以及 **使用远程规则集**。
3. 依序新增以下规则：

| 序号 | 规则集 URL | 反选 (Inverse) | 动作 (Action) | 说明 |
| :-: | :--- | :-: | :-: | :--- |
| 1 | `https://raw.githubusercontent.com/vilavpn/meta-rules-dat/sing/geo/geosite/category-ads-all.srs` | 关闭 | `block` | (可选) 广告拦截 |
| 2 | `https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-ai-blocked.srs` | 关闭 | **`proxy`** | 香港受限 AI 服务走代理 |
| 3 | `https://raw.githubusercontent.com/AndyZHENG0715/hk-ai-rules/main/hk-direct-fallback.srs` | 关闭 | **`direct`** | 香港全网直连兜底 |

4. 保存并重新连接即可。

---

### 2. Sing-box 标准配置

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

## 🛠️ 自动化每日构建

本仓库每天香港时间 06:00 (UTC 22:00) 自动触发 GitHub Actions 执行：
- 上游源：`vilavpn/meta-rules-dat` (`category-ai-!cn.json`)
- 自定义补充：`supplement.json`
- 香港白名单过滤：`scripts/hk-whitelist.txt`

### 如何贡献
若某项 AI 服务开始对香港开放，或有新增的不支持香港的 AI 服务：
1. Fork 本仓库。
2. 编辑 [`scripts/hk-whitelist.txt`](scripts/hk-whitelist.txt) 新增或移除对应域名/关键字。
3. 提交 Pull Request，合并后 GitHub Actions 会自动编译发布最新的 `.srs` 规则文件。

---

## 📄 开源许可

本项目采用 MIT 许可证。欢迎自由使用、转载与集成。
