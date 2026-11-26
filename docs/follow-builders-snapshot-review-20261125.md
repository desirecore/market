# Follow Builders exact-snapshot review / 固定快照复审

Reviewer: mashagua. Review date: 2026-11-25.

- Previous pin: `22c2e72e1a4bb0fc0f3e19f992fc55615b48989e`
- Accepted target: `65452b9258f31ed2893734c86481216d2e4105ff`
- Install scope: whole upstream repository, unchanged; no repackaging, exclusions or resource removal.

| Check / 检查 | Evidence / 证据 | Decision / 结论 |
| --- | --- | --- |
| License exception / 许可例外 | README.md SHA256 `ed622ec7b1c36417b3b5d684cb995611ce55c2f1987d8a7a6815c314f4447db7`; identical at both pins; ends with License / MIT; no standalone LICENSE | Explicitly accept the existing catalog-specific exception for this exact new pin only. 不自动沿用到未来版本。 |
| License delivery / 许可携带 | README.md lies inside the unchanged whole-repository install scope | No parent-directory notice attachment is required for this entry. |
| Source delta / 来源差异 | Git compare is one commit ahead; exactly four JSON files below; all parse and retain their top-level keys | Feed/state data update only; no script, workflow, skill instruction, source configuration, dependency or lockfile changes. |
| Third-party material / 第三方内容 | Feeds contain public posts/transcripts/links | Retain respective rights and service terms; the repository MIT mention is not a grant to relicense all third-party content. |
| Runtime and authority / 运行与授权 | Node.js/npm prerequisites and Telegram/Resend credentials, fees and explicit send/schedule permission remain disclosed | No upstream code or external service executed; not runtime, safety, or actual-delivery acceptance. |

## Changed data hashes

| Path | Previous SHA256 | Target SHA256 |
| --- | --- | --- |
| `feed-blogs.json` | `d186789a3f7fb592b157e9ff2da1270fa7a6264da9661afb6417fa3b54c4b511` | `e1ded1bb139beadab78e683a054bb44fbf9eabbd6db7e11e4e865d2f3bb637c2` |
| `feed-podcasts.json` | `633a61c9bf2dd698d74677244e10c35c0c4c2ef0267c61c218869e434dd1aab0` | `b60cc450c226a889b3a8faf0030545f362dc81f6ded4a6643caecdae023c46b0` |
| `feed-x.json` | `65acae0050a81034b729e8dc3d34df1a4be1958d23463b58f80b900abb7a0b99` | `fb0cf7af4b80e2bf91093616d5124e2670b2d8c5e434fc1c1bc6f27fb113fe55` |
| `state-feed.json` | `e7637359bb2e7c137b5abaee78e1524761785dde252c1a4a610e689a18523256` | `4c14217a518bc289ec501adc045480c9c251cb658d61eccd85acecced437978b` |

`SKILL.md` SHA256 `c0e801510917befd8efe89b190993472673bad1b79c5c81b95203f0a58c185fa` and `scripts/package.json` SHA256 `e06010b593051752f71c432318aee9f99e78d0b04254f6ae5d4e32a03bca16bd` are unchanged. All other upstream files are unchanged according to the exact-pin full diff. The machine audit is regenerated separately and stays attributed to `automated:source-license-metadata-v1`; this human review does not impersonate it.
