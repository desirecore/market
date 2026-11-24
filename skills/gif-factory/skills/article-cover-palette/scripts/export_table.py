#!/usr/bin/env python3
"""从catalog.json导出同一张表的Markdown和可用Excel打开的CSV。"""
import argparse
import csv
import json
from os.path import relpath
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def export(csv_path=None,cards_path=None):
    palettes=json.loads((ROOT/'references/catalog.json').read_text())['palettes']
    headers=['编号','名称','颜色及HEX','适用题材','情绪','适合的文章任务','底色','标题字','正文小字','点缀','搭配说明']
    rows=[]
    for p in palettes:
        r=p['default_roles']
        def label(role):
            return role['name']+' '+role['hex']+('（只限大字）' if role.get('large_only') else '')
        rows.append([p['number'],p['name'],' / '.join(c['name']+' '+c['hex'] for c in p['colors']),
                     '、'.join(p['topics']),'、'.join(p['moods']),'、'.join(p['purposes']),
                     label(r['background']),label(r['title']),label(r['body']),label(r['accent']),p['usage']])
    lines=['# 100套文章配色表','',
           '编号与已生成的100张窄横色卡一一对应。题材和情绪是推荐方向，不是只能这样用；先看文章想表达什么。',
           '“辅助字色”只用于读字，不改原HEX、不冒充原配色。“只限大字”表示正文小字需改用表中的正文色。',
           '机器数据以 [catalog.json](catalog.json) 为准；本表由同一份数据生成。','',
           '| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']
    lines+=['| '+' | '.join(str(c).replace('|','／') for c in row)+' |' for row in rows]
    md=ROOT/'references/palette-table.md';md.write_text('\n'.join(lines)+'\n')
    if csv_path:
        path=Path(csv_path).expanduser();path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(headers);w.writerows(rows)
    if cards_path:
        path=Path(cards_path).expanduser();path.parent.mkdir(parents=True,exist_ok=True)
        lines=['# 100 套配色色卡','',
               '按001—100排列，每组都列出卡片和原始HEX。展开一组看十张，点击卡片看原图。',
               '色卡是AI视觉预览；实际用色按旁边的HEX。用途、情绪和标题搭法见[完整配色表](palette-table.md)。','']
        for start in range(0,len(palettes),10):
            group=palettes[start:start+10]
            lines+=['<details>','<summary>'+group[0]['number']+'—'+group[-1]['number']+'</summary>','',
                    '| 编号与名称 | 色卡 | 原始色号 |','| --- | --- | --- |']
            for p in group:
                preview=Path(relpath(ROOT/p['preview'],path.parent)).as_posix()
                colors='<br>'.join(c['name']+' '+c['hex'] for c in p['colors'])
                lines.append('| '+p['number']+' '+p['name']+' | !['+p['name']+']('+preview+') | '+colors+' |')
            lines+=['','</details>','']
        path.write_text('\n'.join(lines).rstrip()+'\n')
    return {'rows':len(rows),'markdown':str(md),'csv':str(csv_path) if csv_path else None,'cards':str(cards_path) if cards_path else None}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv')
    parser.add_argument('--cards',help='同时导出带100张色卡和HEX的Markdown表')
    args=parser.parse_args()
    print(json.dumps(export(args.csv,args.cards),ensure_ascii=False))
