#!/usr/bin/env python3
"""Prepare reference-guided English lettering inputs without calling an API."""
import argparse
import json
from pathlib import Path
import tempfile


def make_font_specimen(font_path, title, destination):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise ValueError('Custom fonts need Pillow: python3 -m pip install Pillow') from exc
    try:
        low, high = 8, 300
        while low < high:
            size = (low + high + 1) // 2
            font = ImageFont.truetype(str(font_path), size)
            box = font.getbbox(title)
            if box[2] - box[0] <= 1750 and box[3] - box[1] <= 400:
                low = size
            else:
                high = size - 1
        font = ImageFont.truetype(str(font_path), low)
        box = font.getbbox(title)
        if box[2] - box[0] > 1750 or box[3] - box[1] > 400:
            raise ValueError('Title is too long for a readable single-line font specimen.')
        image = Image.new('RGB', (1920, 600), 'white')
        ImageDraw.Draw(image).text(((1920 - (box[2] - box[0])) / 2 - box[0],
                                    (600 - (box[3] - box[1])) / 2 - box[1]),
                                   title, font=font, fill='black')
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, 'PNG')
    except OSError as exc:
        raise ValueError('Could not read the supplied font file: ' + str(font_path)) from exc


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style',required=True,help='EN01–EN50, original R id, or font name')
    parser.add_argument('--title',required=True)
    parser.add_argument('--font',type=Path,help='Optional custom TTF or OTF font; style supplies the decoration reference')
    parser.add_argument('--scene',default='')
    parser.add_argument('--photo',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    catalog=json.loads((root/'assets/english-titles/catalog.json').read_text(encoding='utf-8'))
    key=args.style.strip().casefold()
    item=next((s for s in catalog['items'] if key in (s['id'].casefold(),s['font_id'].casefold(),s['font_name'].casefold())),None)
    if item is None:parser.error('Unknown style; use an EN id, R id, or exact font name from the catalog.')
    title=args.title.strip()
    if not title:parser.error('Title must not be blank.')
    font_file = root/item['font_file']
    font_name = item['font_name']
    specimen = root/item['specimen']
    if args.font:
        font_file = args.font.expanduser().resolve()
        if not font_file.is_file():parser.error('Font file does not exist: '+str(font_file))
        if font_file.suffix.lower() not in ('.ttf', '.otf'):parser.error('Custom font must be a TTF or OTF file.')
        folder = Path(tempfile.mkdtemp(prefix='english-title-font-'))
        specimen = folder/'font-specimen.png'
        try:make_font_specimen(font_file,title,specimen)
        except ValueError as exc:parser.error(str(exc))
        font_name = font_file.stem
    references=[str(specimen),str(root/item['frame'])]
    if args.photo:
        photo=args.photo.expanduser().resolve()
        if not photo.is_file():parser.error('Photo does not exist: '+str(photo))
        references.append(str(photo))
    prompt=(
        'Use case: ads-marketing. Create one English cinematic title design. '
        'Image 1 is a real font specimen: use its letter skeleton, stroke weight, joins and counters, '
        'and ignore its sample words and font labels. Image 2 is the decorative lettering reference: '
        'use its scale contrast and stroke-to-scene relationships, not its old title or photograph. '
        'Exact new title, each word once in the supplied order: '+json.dumps(title,ensure_ascii=False)+'. '
        'Base font: '+font_name+'. Decoration direction: '+item['lettering_notes']+' '
        'The decoration notes describe the example; adapt their anchor letters and word groups to the NEW title. '
        'Use only the new title as visible wording. Thin handwriting stays thin; chunky print stays print. '
        'Grow decoration from actual letters rather than detached icons. Preserve clear spelling and counters. '
        'Keep every ascender, descender and flourish inside frame with breathing room. '
        'No copied example wording, Chinese text, labels, logos, credits or watermarks. '
    )
    if args.photo:
        prompt+='Image 3 is the final scene photograph. Preserve its framing, objects, lighting and material texture; change only the title and its decoration. '
    elif args.scene:
        prompt+='Make a new photorealistic scene: '+args.scene+'. One ultrawide frame, approximately 2.38:1. '
    else:
        prompt+='Create lettering only on a plain white background; no scene or extra captions. '
    if args.font:
        prompt+='Image 1 is the user-supplied font: preserve its actual stroke weight and letter shapes. Use the example only for decoration and composition; ignore any conflicting font description. '
    prompt+='Final visible text must be exactly '+json.dumps(title,ensure_ascii=False)+'. Do not use any example title from the references or decoration notes. '
    value={'style':item['id'],'font_id':None if args.font else item['font_id'],'font_name':font_name,'title':title,
           'base_font_file':str(font_file),
           'imagegen_args':{'prompt':prompt,'referenced_image_paths':references,'transparent_background':False}}
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding='utf-8')
    else:print(text,end='')


if __name__=='__main__':main()
