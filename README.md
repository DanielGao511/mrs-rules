# MRS rules

将 [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules) 的 11 份公共 YAML 规则转换为 Mihomo MRS，保持域名覆盖和 IP 网络范围一致。

- `main`：来源清单、构建/校验脚本和 GitHub Actions。
- `release`：`.mrs` 文件、`manifest.json`、`SHA256SUMS`。
- 每天 UTC 04:00（北京时间 12:00）构建，也可在 Actions 页面手动运行。GitHub 的定时执行可能延迟或漏跑；公开仓库长时间无活动可能暂停调度。
- 使用固定版本 Mihomo v1.19.30，下载时校验官方发布的 SHA256。
- 每份 MRS 解码后进行双向域名覆盖/IP 网络等价比较，全部通过才提交，失败保留上一版。
- 仅内容或来源元数据变化时提交，无时间戳空更新，无强制推送。

下载示例：

```text
https://raw.githubusercontent.com/DanielGao511/mrs-rules/release/reject.mrs
https://cdn.jsdelivr.net/gh/DanielGao511/mrs-rules@release/reject.mrs
```

Clash/Mihomo provider 示例：

```yaml
reject:
  type: http
  behavior: domain
  format: mrs
  url: https://cdn.jsdelivr.net/gh/DanielGao511/mrs-rules@release/reject.mrs
  path: ./ruleset/reject.mrs
  interval: 86400
```

`icloud/apple/proxy/direct/private/gfw/tld-not-cn` 同为 domain；`telegramcidr/cncidr/lancidr` 为 ipcidr。`applications` 是 classical，继续使用上游原文件，不转换。此仓库不转换 GEOSITE，不包含用户订阅、代理节点或凭据。

GitHub Raw 和 CDN 的可达性取决于客户端网络；CDN 分支地址可能有缓存延迟。完整批次在同一个 Git 提交中发布，但固定分支 URL 的跨文件 CDN 更新不保证同时生效。

上游规则项目使用 GPL-3.0，保留其来源及许可证；规则来源的进一步归属请参阅上游 README。构建脚本同样按 GPL-3.0 发布。Mihomo 仅在 runner 临时下载使用，不提交到此仓库。
