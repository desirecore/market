#!/usr/bin/env python3
"""给十款手写字准备带原稿的生图输入；可做白底字稿或按描述配场景。"""
import argparse
import json
from pathlib import Path

def prepare(style_id, title, break_after=None, scene=None):
    skill_root = Path(__file__).resolve().parents[1]
    profile_path = skill_root / "assets/style-catalog/handwriting/profiles.json"
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    styles = {item["id"]: item for item in data["styles"]}
    if style_id not in styles:
        raise ValueError("这里支持 F41–F50；原有 F01–F40 按分类说明选原图。")
    if not title.strip():
        raise ValueError("片名不能为空。")
    if break_after is not None and not 0 < break_after < len(title):
        raise ValueError("断行位置要在片名中间。")
    if scene is not None and not scene.strip():
        raise ValueError("场景描述不能为空。")
    profile = styles[style_id]
    refs = [profile_path.parent / profile[key] for key in ("master", "anchor")]
    for ref in refs:
        if not ref.is_file():
            raise FileNotFoundError("找不到字形参考图：" + str(ref))
    layout = ("整组单行，字的高低和宽窄按原稿自然错落。"
              if break_after is None else
              "分两行：上行「" + title[:break_after] + "」，下行「" + title[break_after:] + "」。")
    character_hints = [hint for char, hint in profile.get("character_hints", {}).items() if char in title]
    prompt = (
        data["frame_prompt" if scene is not None else "shared_prompt"] + "\n\n"
        + "本款：" + style_id + " " + profile["name"] + "。\n"
        + "必须延续的写法：\n" + "\n".join("- " + x for x in profile["rules"]) + "\n"
        + "容易跑偏的地方：" + "；".join(profile["avoid"]) + "。\n"
        + "这次只写：「" + title + "」。按顺序逐字：" + " / ".join(title) + "。\n"
        + layout + "\n"
        + (("本次场景：" + scene + "\n") if scene is not None else "")
        + (("本句的字形检查：" + "；".join(character_hints) + "\n") if character_hints else "")
        + "先选适合本款的一至两个重点笔画。只有本款需要长竖、长锋或长钩时才延长实际笔画，"
          "其余款保留短收笔与紧凑字身，不额外拉长。用大小和留白托住主字，不在字旁另画装饰线。"
    )
    return {
        "style_id": style_id, "style_name": profile["name"], "title": title,
        "kind": "film_title_frame" if scene is not None else "lettering_sample",
        "prompt_revision": data["version"],
        "reference_roles": ["字形主参考：用户原稿", "辅助参考：同款校准字稿"],
        "scene_example": str((profile_path.parent / profile["scene_example"]).resolve()),
        "imagegen_args": {
            "prompt": prompt,
            "referenced_image_paths": [str(ref.resolve()) for ref in refs],
            "transparent_background": False
        }
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--break-after", type=int)
    parser.add_argument("--scene", help="可选：描述要新生成的场景；不填时准备白底字稿。")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        result = prepare(args.style.upper(), args.title, args.break_after, args.scene)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

if __name__ == "__main__":
    main()
