---
name: douyin-video-download
description: >-
  Download Douyin (抖音) videos without watermark over the H5-header route:
  resolve the share short link, obtain the ttwid device cookie via a two-pass
  request to the iesdouyin share page, extract the play address from the
  embedded videoInfoRes JSON, swap playwm for play to drop the watermark,
  download and verify with ffprobe. No login, no browser rendering, no cookie
  harvesting from user browsers. Use when the user asks to download, save, or
  de-watermark a Douyin video, or when a message contains a v.douyin.com short
  link, an iesdouyin share link, or a bare video ID. Trigger words: 下载抖音,
  抖音无水印, 保存抖音视频, 解析抖音链接, 抖音视频下载.
license: MIT
version: 1.0.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - douyin
  - video
  - download
  - watermark-free
metadata:
  author: yi-ge
  updated_at: '2026-11-17'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 抖音视频下载
      short_desc: 抖音视频无水印下载：H5 header 两段式路线，免登录免浏览器
      description: 抖音视频无水印下载（H5 header 路线）：短链解析、两段式请求 iesdouyin 分享页取得 ttwid 并提取 videoInfoRes 播放地址、playwm 改 play 去水印下载、ffprobe 校验。免登录、免浏览器渲染，不读取用户浏览器凭据。Use when 用户要求下载/保存/解析抖音视频、去水印，或消息含 v.douyin.com 短链、iesdouyin 分享链接、纯视频 ID；触发词：下载抖音、抖音无水印、保存抖音视频、解析抖音链接、抖音视频下载。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:52f9ef92ca43f7da
      translated_by: human
    en-US:
      name: Douyin Video Download
      short_desc: Watermark-free Douyin downloads over the H5-header two-pass route, no login or browser needed
      description: >-
        Download Douyin videos without watermark over the H5-header route:
        resolve the share short link, obtain the ttwid device cookie via a
        two-pass request to the iesdouyin share page, extract the play address
        from the embedded videoInfoRes JSON, swap playwm for play, download and
        verify with ffprobe. No login, no browser rendering, no user-browser
        credential access. Use when the user asks to download, save, or
        de-watermark a Douyin video, or when a message contains a
        v.douyin.com short link, an iesdouyin share link, or a bare video ID.
      body: ./SKILL.md
      source_hash: sha256:52f9ef92ca43f7da
      translated_by: ai
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="5" width="18" height="14" rx="3"
    stroke="#007AFF" stroke-width="1.5"/><path d="M10 9.5v5l4.5-2.5L10 9.5z"
    fill="#34C759"/><path d="M7 2v3M17 2v3" stroke="#007AFF"
    stroke-width="1.5" stroke-linecap="round"/></svg>
  short_desc: 抖音视频无水印下载：H5 header 两段式路线，免登录免浏览器
  category: productivity
  channel: latest
  maintainer:
    name: yi-ge
    verified: false
---

# douyin-video-download Skill

## L0: One-line Summary

Download Douyin videos without watermark via the mobile H5-header route and verify with ffprobe — no login required.

## L1: Overview and Use Cases

### Capability

Run the full chain on a Douyin short link / share link / video ID: resolve the
short link, make a two-pass request to the iesdouyin share page to obtain the
ttwid cookie and extract `videoInfoRes.play_addr`, swap `playwm` for `play` to
drop the watermark, download, and verify with ffprobe. The bundled
`scripts/download_douyin.py` does all of this in one command (stdlib only).

### Use Cases

The user provides a v.douyin.com short link, an iesdouyin share link, or a bare
video ID and asks to download, save, or de-watermark it; or a previous download
attempt failed and needs a reliable path.

### Core Value

No user-browser credentials, no login bridge, no browser rendering — pure
HTTP. Works even for videos whose desktop web API is blocked by msToken/Argus
signing (verified 2026-11).

## L2: Detailed Specification

### Quick start (recommended)

```bash
python3 scripts/download_douyin.py "https://v.douyin.com/<short_id>/" -o out_dir/
python3 scripts/download_douyin.py 7708667389918858496 -o out_dir/
```

The script resolves the short link, obtains ttwid, extracts the play address,
swaps playwm→play, downloads, and runs ffprobe verification. Output:
`<video_id>.mp4` plus metadata. Python standard library only.

### Manual steps (when the script is unavailable)

1. **Resolve the short link**: `curl -sIL -A "$H5UA" "https://v.douyin.com/<short_id>/"`
   and take `https://www.iesdouyin.com/share/video/<video_id>/?...&share_sign=...`
   from the 302 Location header.
2. **Prepare H5UA**: an iPhone Safari UA, e.g.
   `Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1`;
   requests must also carry browser-style `Accept`/`Accept-Language` headers.
3. **Two-pass fetch of videoInfoRes**: request
   `https://www.iesdouyin.com/share/video/<video_id>/`. The first response only
   sets a `ttwid` device-session cookie on the `.iesdouyin.com` domain (not a
   login credential); **re-request with that cookie** and the response embeds
   `videoInfoRes` at `videoInfoRes.item_list[0].video.play_addr.url_list[0]`,
   e.g. `https://aweme.snssdk.com/aweme/v1/playwm/?video_id=<vid>&ratio=720p&line=0`.
   Extraction snippet:

   ```python
   block = html[html.find('"videoInfoRes":{'):]
   m = re.search(r'"play_addr":\{"uri":"[^"]*","url_list":(\[.*?\])', block)
   url = json.loads(m.group(1).replace('\\u002F', '/'))[0]
   ```

4. **Watermark-free download**: replace `playwm` with `play` in the URL and
   download with `curl -sL`, again with the H5 UA + Referer. `url_list` may hold
   several addresses — try them in order; the `ratio` tier comes from the share
   page.
5. **Verify**: ffprobe for container/duration/resolution; compare with the page
   `duration` field (unit may be milliseconds — trust ffprobe).

### Failure memo (verified 2026-11 — do not retry these)

| Path | Symptom |
| --- | --- |
| Desktop web API (/aweme/v1/web/aweme/detail) | Blocked by ArgusSecurityPlugin Uifid Not Found (msToken signing required) |
| yt-dlp 2026.10.26 | Fresh cookies needed (msToken requires JS) |
| Single share-page request (no prior ttwid) | Only Set-Cookie returned; no videoInfoRes |
| Requests without browser-style Accept headers | Slimmed response without videoInfoRes |
| Jina Reader anonymous | IP-reputation rate limit 401 |
| Rendering the Douyin page in a browser | Heavy page — quota kills / navigation timeouts |

### Error handling

- `页面无 videoInfoRes` (no videoInfoRes): confirm the two-pass request ran
  (second request carries ttwid) and headers are complete.
- Cannot resolve video_id: the short link may have expired — ask the user to
  re-share, or use the bare numeric ID directly.
- Downloaded body < 10KB: likely an error page — try the next `url_list` entry.
- CDN rejects: the download request must also carry the H5 UA + Referer.

### Compliance boundary

Only download content the user is entitled to keep (their own or authorized
material); respect platform terms and copyright; no bulk scraping or
infringing redistribution. Never read user-browser cookies or inject login
credentials.
