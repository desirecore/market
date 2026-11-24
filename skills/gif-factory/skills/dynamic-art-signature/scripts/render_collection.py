#!/usr/bin/env python3
"""Re-render a nine-signature manifest, then compose its actual MP4 files."""
import argparse
import json
from pathlib import Path

from render_ink_signature import InkAnimation
from make_grid import assemble


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--font',help='Font file for Chinese grid labels')
    args=parser.parse_args()
    manifest=args.manifest.resolve()
    cases=json.loads(manifest.read_text(encoding='utf-8'))
    if len(cases)!=9 or len({c['slug'] for c in cases})!=9:
        raise ValueError('The grid needs nine distinct signature output names')
    # Validate every config before starting any export.
    configs=[manifest.parent/c['config'] for c in cases]
    for config in configs:
        if not config.is_file():raise ValueError('Config not found: '+str(config))
    args.out.mkdir(parents=True,exist_ok=True)
    videos=[]
    for c,config in zip(cases,configs):
        base=args.out/c['slug']
        print('Rendering '+c['name']+' / '+c['family'],flush=True)
        InkAnimation(config).render(base)
        videos.append(base.with_suffix('.mp4'))
    assemble(videos,[c['label'] for c in cases],args.out/'MultiFont_Nine_Grid',args.font)


if __name__=='__main__':
    main()
