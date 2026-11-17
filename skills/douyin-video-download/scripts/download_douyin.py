#!/usr/bin/env python3
"""抖音视频无水印下载（H5 header 路线）。

用法:
    python3 download_douyin.py "https://v.douyin.com/<short_id>/" -o out_dir/
    python3 download_douyin.py 7708667389918858496 -o out_dir/

原理: 短链解析 -> ttwid cookie -> iPhone UA + Referer 请求 iesdouyin 分享页
-> videoInfoRes.item_list[0].video.play_addr.url_list -> playwm 改 play -> 下载 -> 校验。
"""
import argparse
import http.cookiejar
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

H5UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)
REFERER = "https://www.iesdouyin.com/"


def _opener(cj: http.cookiejar.CookieJar):
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


HEADERS = {
    "User-Agent": H5UA,
    "Referer": REFERER,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def fetch(url: str, cj: http.cookiejar.CookieJar, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with _opener(cj).open(req, timeout=timeout) as resp:
        return resp.read()


def resolve_video_id(source: str, cj: http.cookiejar.CookieJar) -> str:
    if re.fullmatch(r"\d{15,25}", source):
        return source
    req = urllib.request.Request(source, headers={"User-Agent": H5UA})
    with _opener(cj).open(req, timeout=30) as resp:
        final = resp.geturl()
    m = re.search(r"/(?:share/)?video/(\d+)", final)
    if not m:
        raise SystemExit(f"无法从跳转地址解析 video_id: {final}")
    return m.group(1)


def extract_play_urls(html: str):
    """返回 (播放地址列表[已去水印], 页面duration数值或None)。"""
    i = html.find('"videoInfoRes":{')
    if i < 0:
        raise SystemExit(
            "页面无 videoInfoRes：请确认同时提供了 iPhone H5 UA、"
            "Referer: https://www.iesdouyin.com/ 与 ttwid cookie（三要素缺一不可）"
        )
    block = html[i:]
    m = re.search(r'"play_addr":\{"uri":"[^"]*","url_list":(\[.*?\])', block)
    if not m:
        raise SystemExit("videoInfoRes 中未找到 play_addr.url_list")
    urls = json.loads(m.group(1).replace("\\u002F", "/"))
    dur = re.search(r'"duration":(\d+)', block)
    urls = [u.replace("playwm", "play") for u in urls]
    return urls, (int(dur.group(1)) if dur else None)


def verify(path: str) -> None:
    ffprobe = shutil.which("ffprobe") or os.environ.get("FFPROBE") or (
        "/Users/yige/.desirecore/runtime/toolkits/ffmpeg/7.1.5-dc1/bin/ffprobe"
        if os.name == "darwin" else ""
    )
    if not ffprobe or not os.path.exists(ffprobe):
        print("ffprobe 不可用，跳过元数据校验（文件已下载）")
        return
    out = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries",
         "format=duration,size:stream=codec_type,codec_name,width,height",
         "-of", "default=noprint_wrappers=1", path],
        capture_output=True, text=True,
    )
    print("=== ffprobe ===")
    print(out.stdout.strip())


def main() -> None:
    ap = argparse.ArgumentParser(description="抖音视频无水印下载（H5 header 路线）")
    ap.add_argument("source", help="抖音短链 / 分享链接 / 纯 video_id")
    ap.add_argument("-o", "--out", default=".", help="输出目录（默认当前目录）")
    ap.add_argument("-n", "--name", default=None, help="输出文件名（默认 <video_id>.mp4）")
    args = ap.parse_args()

    cj = http.cookiejar.CookieJar()
    try:  # ttwid 是设备会话 cookie，不是登录凭据
        fetch("https://www.douyin.com/", cj)
    except Exception:
        pass

    vid = resolve_video_id(args.source, cj)
    print(f"video_id: {vid}")
    share_url = f"https://www.iesdouyin.com/share/video/{vid}/"
    html = fetch(share_url, cj).decode("utf-8", "replace")
    if '"videoInfoRes"' not in html:
        # iesdouyin 首次响应只下发 ttwid；带 cookie 二次请求才返回 videoInfoRes
        html = fetch(share_url, cj).decode("utf-8", "replace")
    urls, duration = extract_play_urls(html)
    if duration:
        print(f"页面 duration: {duration}（注意单位，可能是毫秒）")

    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, args.name or f"{vid}.mp4")
    for u in urls:
        print(f"尝试播放地址: {u[:100]}...")
        try:
            data = fetch(u, cj)
            if len(data) < 10_000:
                print("  返回过小，判定无效，换下一个", file=sys.stderr)
                continue
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"下载完成: {out_path} ({len(data)} bytes)")
            verify(out_path)
            return
        except Exception as exc:  # noqa: BLE001
            print(f"  失败: {exc}", file=sys.stderr)
    raise SystemExit("所有播放地址均下载失败")


if __name__ == "__main__":
    main()
