# Current VilaNet and sing-box setup

Verified on 2026-11-07 with native Windows and Ubuntu in WSL mirrored networking mode.

Windows runs VilaNet CLI as the shared proxy exit on a loopback listener. A separate Windows sing-box instance owns the TUN adapter and applies the routing rules. The startup tasks are `VilaNetCLI` and `VilaNetSingBox`.

WSL runs its own sing-box instance through `vilanet-sb.service`. It loads a separate copy of the rule files and sends proxy traffic to the Windows VilaNet CLI listener over mirrored loopback. The `vilanet-route-fix.service` handles the unwanted mirrored Windows TUN default route. Windows Zed hosted model requests use Windows routing. External agents running inside WSL use WSL routing.

Both sing-box instances apply these five rule sets in order, after any protocol handling or private address exceptions in their respective configs.

| Order | Rule set file | Action |
| --- | --- | --- |
| 1 | `category-ads-all.srs` | Reject |
| 2 | [`hk-ai-whitelist.srs`](../hk-ai-whitelist.srs) | Direct |
| 3 | [`ai-supplement.srs`](../ai-supplement.srs) | Proxy |
| 4 | [`hk-ai-upstream.srs`](../hk-ai-upstream.srs) | Proxy |
| 5 | [`hk-direct-fallback.srs`](../hk-direct-fallback.srs) | Direct |

The ads rule comes from [`vilavpn/meta-rules-dat`](https://github.com/vilavpn/meta-rules-dat/tree/sing/geo/geosite). The other four files are built by this repository's [GitHub Actions workflow](../.github/workflows/build-rules.yml). The combined `hk-ai-blocked.srs` example in the README is a separate setup option.

## Updating a rule

1. Add manually maintained proxy domains to [`supplement.json`](../supplement.json). The [`build_four_layer.py`](../scripts/build_four_layer.py) builder compiles that source into `ai-supplement.srs`.
2. Publish the reviewed change and check that `main` contains the rebuilt `.srs` file.
3. Back up and replace the corresponding `.srs` file at the path in each affected instance's `route.rule_set` configuration. Each instance uses `type: local`, so a commit to GitHub does not refresh either copy by itself.
4. Reload the affected sing-box instance and verify the application uses the expected route. For a Windows-only rule update, reload `VilaNetSingBox`. For a WSL update, restart `vilanet-sb.service`.

For Zed hosted models, the supplement matches `cloud.zed.dev`. The Windows test routed it through the proxy to Cloudflare's `LAX` location, and the previously affected hosted model replied successfully.
