# Current VilaNet and sing-box setup

Last updated 2026-11-09. The Windows and WSL setup was verified with a reboot on 2026-11-04 and with native Windows and Ubuntu in WSL mirrored networking mode on 2026-11-07.

## Rule order

Every device applies these five rule sets in order. On Windows and WSL they come after any protocol handling or private address exceptions in the sing-box configs.

| Order | Rule set file | Action |
| --- | --- | --- |
| 1 | `category-ads-all.srs` | Reject |
| 2 | [`hk-ai-whitelist.srs`](../hk-ai-whitelist.srs) | Direct |
| 3 | [`ai-supplement.srs`](../ai-supplement.srs) | Proxy |
| 4 | [`hk-ai-upstream.srs`](../hk-ai-upstream.srs) | Proxy |
| 5 | [`hk-direct-fallback.srs`](../hk-direct-fallback.srs) | Direct |

`hk-direct-fallback.srs` matches every domain and every IP address, so only domains listed in layers 3 and 4 use the proxy. A connection whose domain cannot be recovered, such as one made to a hard-coded IP address, matches only layer 5 and goes direct.

The ads rule comes from [`vilavpn/meta-rules-dat`](https://github.com/vilavpn/meta-rules-dat/tree/sing/geo/geosite). The other four files are built by this repository's [GitHub Actions workflow](../.github/workflows/build-rules.yml). The combined `hk-ai-blocked.srs` example in the README is a separate setup option.

## Windows

VilaNet CLI runs with `--no-tun` as the shared proxy exit on a loopback listener. A separate sing-box instance owns the TUN adapter and applies the routing rules. Two startup scheduled tasks, `VilaNetCLI` and `VilaNetSingBox`, start them at boot, and the VilaNet GUI no longer starts automatically. This replaced the GUI because the GUI connects only after login, so restored apps such as Claude and Codex sometimes sent requests before the VPN was ready. The official CLI Windows service was not used because it hit SCM startup timeouts.

## WSL

WSL runs its own sing-box instance through `vilanet-sb.service`. It loads its own copy of the rule sets and sends proxy traffic to the Windows VilaNet CLI listener over mirrored loopback. The `vilanet-route-fix.service` handles the unwanted mirrored Windows TUN default route. Windows Zed hosted model requests use Windows routing. External agents running inside WSL use WSL routing.

## Mac mini

The Mac uses the VilaNet GUI from the App Store, with the five rule sets entered as custom rules. Rule-set downloads must go through the VPN. Direct downloads failed on the Mac even though the URLs open normally in Hong Kong.

## iPhone

The iPhone uses the VilaNet iOS app with the same five custom rules. DNS settings:

- Tunnel DNS: `https://1.0.0.1/dns-query`
- Direct DNS: `223.5.5.5`
- IP preference: Prefer IPv4

FakeIP was turned off (RealIP mode) on 2026-11-09 because WhatsApp media and stickers were delayed or failed while it was on. This is still being observed. In RealIP mode, turn on **Prevent DNS leak**. If a proxied AI service ever reports an unsupported region, a likely cause is a connection whose domain was not sniffed and therefore fell through to layer 5. Turning FakeIP back on is the first thing to test.

## Updating a rule

1. Add manually maintained proxy domains to [`supplement.json`](../supplement.json). The [`build_four_layer.py`](../scripts/build_four_layer.py) builder compiles that source into `ai-supplement.srs`.
2. Publish the reviewed change and check that `main` contains the rebuilt `.srs` file.
3. Windows and WSL use remote rule sets that check for updates every hour. A local file and the persistent cache keep the rules available at startup before the first download. To apply a change immediately, reload `VilaNetSingBox` on Windows or restart `vilanet-sb.service` in WSL. On the Mac and iPhone, reconnect VilaNet.
4. Verify that the application uses the expected route.

For Zed hosted models, the supplement matches `cloud.zed.dev`. The Windows test routed it through the proxy to Cloudflare's `LAX` location, and the previously affected hosted model replied successfully.
