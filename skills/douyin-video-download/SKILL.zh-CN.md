<!-- locale: zh-CN -->

# douyin-video-download Skill

## L0：一句话摘要

用移动端 H5 header 请求抖音分享页提取播放地址，免登录下载无水印视频并校验。

## L1：概述与使用场景

### 能力描述

对抖音短链/分享链接/视频 ID 执行完整链路：短链解析 → 两段式请求 iesdouyin 分享页取得
ttwid 并提取 videoInfoRes.play_addr → playwm 改 play 去水印 → 下载 → ffprobe 校验，
产出无水印 MP4。配套脚本 `scripts/download_douyin.py` 一条命令完成。

### 使用场景

用户发来 v.douyin.com 短链、iesdouyin 分享链接或纯视频 ID，要求下载、保存或去水印；
下载失败需要按可靠路径排查。

### 核心价值

不读浏览器凭据、不启动登录桥接、不需要浏览器渲染，纯 HTTP 完成；对桌面 API 被
msToken/Argus 签名拦截的视频同样有效（2026-11 实测）。

## L2：详细规范

### 快速使用（推荐）

```bash
python3 scripts/download_douyin.py "https://v.douyin.com/<short_id>/" -o out_dir/
python3 scripts/download_douyin.py 7708667389918858496 -o out_dir/
```

脚本自动完成：短链解析、ttwid 获取、播放地址提取、playwm→play、下载、ffprobe 校验。
输出 `<video_id>.mp4` 与元数据。脚本仅依赖 Python 标准库。

### 手动步骤（脚本不可用时）

1. **短链解析**：`curl -sIL -A "$H5UA" "https://v.douyin.com/<short_id>/"`，从 302
   Location 取 `https://www.iesdouyin.com/share/video/<video_id>/?...&share_sign=...`。
2. **准备 H5UA**：iPhone Safari UA，例如
   `Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1`；
   请求需附带浏览器式 `Accept`/`Accept-Language` 头。
3. **两段式取得 videoInfoRes**：请求 `https://www.iesdouyin.com/share/video/<video_id>/`。
   首次响应只在 `.iesdouyin.com` 域下发 `ttwid`（设备会话标识，非登录凭据）；**带上该
   cookie 再次请求**，响应才内嵌 `videoInfoRes`。路径：
   `videoInfoRes.item_list[0].video.play_addr.url_list[0]`，形如
   `https://aweme.snssdk.com/aweme/v1/playwm/?video_id=<vid>&ratio=720p&line=0`。
   提取片段：

   ```python
   block = html[html.find('"videoInfoRes":{'):]
   m = re.search(r'"play_addr":\{"uri":"[^"]*","url_list":(\[.*?\])', block)
   url = json.loads(m.group(1).replace('\\u002F', '/'))[0]
   ```

4. **去水印下载**：URL 中 `playwm` 替换为 `play`，`curl -sL` 同样带 H5 UA + Referer
   下载。`url_list` 可能有多个地址，逐个尝试；`ratio` 档位由分享页给出。
5. **校验**：ffprobe 查容器/时长/分辨率，与页面 `duration` 字段比对（单位可能是毫秒，
   以 ffprobe 为准）。

### 失败路径备忘（2026-11 实测，勿再走弯路）

| 路径 | 现象 |
| --- | --- |
| 桌面 web API（/aweme/v1/web/aweme/detail） | Blocked by ArgusSecurityPlugin Uifid Not Found（需 msToken 签名） |
| yt-dlp 2026.10.26 | Fresh cookies needed（msToken 需 JS 生成） |
| 分享页单次请求（无既有 ttwid） | 只拿到 Set-Cookie，响应无 videoInfoRes |
| 不带浏览器式 Accept 头 | 响应精简，无 videoInfoRes |
| Jina Reader 匿名 | IP 信誉限流 401 |
| 浏览器渲染抖音页 | 页面资源重，易触发配额终止/导航超时 |

### 错误处理

- `页面无 videoInfoRes`：确认两段式已执行（第二次请求带 ttwid）且请求头完整。
- `无法解析 video_id`：短链可能过期，让用户重新分享；或直接用纯数字 ID。
- 下载返回体过小（<10KB）：多半是错误页，换 `url_list` 下一个地址。
- CDN 拒绝：下载请求必须同样带 H5 UA + Referer。

### 合规边界

仅下载用户有权保存的内容（自有/获授权素材）；遵守平台服务条款与版权，不用于批量
抓取或传播侵权内容。不读取浏览器 Cookie、不注入登录凭据。
