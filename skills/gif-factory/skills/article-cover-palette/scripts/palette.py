#!/usr/bin/env python3
"""查配色、计算字色、推荐方案和导出配色交接单。只用Python标准库，不生成封面。"""
import argparse
import colorsys
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
NEUTRALS = ['#000000', '#FFFFFF']
ALIASES = {'AI':'科技','人工智能':'科技','软件':'科技','投资':'财经','金融':'财经','咖啡':'饮食','美食':'饮食','户外':'自然','放松':'放松','平静':'安静','理性':'冷静','高能':'兴奋','克制':'克制','上市发布':'发布','分析':'解释'}


def normalize_hex(value):
    value = str(value).strip().upper()
    if not value.startswith('#'):
        value = '#'+value
    if re.fullmatch(r'#[0-9A-F]{3}', value):
        value = '#'+''.join(c*2 for c in value[1:])
    if not re.fullmatch(r'#[0-9A-F]{6}', value):
        raise ValueError('HEX需为三位或六位色号：'+value)
    return value


def luminance(value):
    value = normalize_hex(value)
    rgb = [int(value[i:i+2],16)/255 for i in (1,3,5)]
    linear = [c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb]
    return sum(c*w for c,w in zip(linear,[0.2126,0.7152,0.0722]))


def contrast(a,b):
    low,high=sorted([luminance(a),luminance(b)])
    return (high+0.05)/(low+0.05)


def pick_ink(background, colors, minimum):
    candidates=[c['hex'] if isinstance(c,dict) else c for c in colors]
    ranked=sorted(candidates,key=lambda c:contrast(c,background),reverse=True)
    ink=ranked[0]
    auxiliary=contrast(ink,background)<minimum
    if auxiliary:
        ink=max(NEUTRALS,key=lambda c:contrast(c,background))
    return {'hex':ink,'contrast':round(contrast(ink,background),3),'auxiliary':auxiliary}


def color_roles(palette, background='不限', background_hex=None):
    colors=palette['colors']
    codes=[c['hex'] for c in colors]
    base=palette.get('background_index',0)
    if background_hex:
        bg=normalize_hex(background_hex)
        if bg not in codes:
            raise ValueError('指定底色不在本组里；请改用自定义配色。')
    elif background=='浅底':
        bg=max(codes,key=luminance)
        if luminance(bg)<0.6:
            raise ValueError('本组没有足够浅的底色。')
    elif background=='深底':
        bg=min(codes,key=luminance)
        if luminance(bg)>0.2:
            raise ValueError('本组没有足够深的底色。')
    else:
        bg=codes[base]
    if (background=='浅底' and luminance(bg)<0.6) or (background=='深底' and luminance(bg)>0.2):
        raise ValueError('指定底色与浅底或深底要求冲突。')
    title=pick_ink(bg,colors,3.0)
    body=pick_ink(bg,colors,4.5)
    rest=[c for c in codes if c not in [bg,title['hex']]]
    def accent_score(code):
        rgb=[int(code[i:i+2],16)/255 for i in (1,3,5)]
        saturation=colorsys.rgb_to_hsv(*rgb)[1]
        return saturation*2+min(contrast(code,bg)/4.5,1)
    accent=max(rest,key=accent_score) if rest else next((c for c in codes if c!=bg),title['hex'])
    by_code={c['hex']:c['name'] for c in colors}
    return {'background':{'hex':bg,'name':by_code[bg]},
            'title':dict(title,name=by_code.get(title['hex'],'辅助字色'),large_only=title['contrast']<4.5),
            'body':dict(body,name=by_code.get(body['hex'],'辅助字色')),
            'accent':{'hex':accent,'name':by_code.get(accent,'点缀')},
            'swatch_inks':[dict(name=c['name'],swatch=c['hex'],**pick_ink(c['hex'],colors,4.5)) for c in colors]}


def load_catalog():
    return json.loads((ROOT/'references/catalog.json').read_text())['palettes']


def custom_palette(values,name='自定配色'):
    if not 2<=len(values)<=6:
        raise ValueError('自定义配色接收2到6个颜色。')
    colors=[{'name':v.get('name',f'颜色{i+1}'),'hex':normalize_hex(v['hex'])} if isinstance(v,dict)
            else {'name':f'颜色{i+1}','hex':normalize_hex(v)} for i,v in enumerate(values)]
    if len({c['hex'] for c in colors})!=len(colors):
        raise ValueError('自定义配色里有重复色号。')
    return {'id':None,'number':'自定','name':name,'colors':colors,'background_index':0,
            'topics':[],'moods':[],'purposes':[],'intensity':3,'preview':None}


def tags(values):
    if isinstance(values,str):
        values=[values]
    return {ALIASES.get(v,v) for v in (values or [])}


def palette_distance(a,b):
    def rgb(c):
        return [int(c['hex'][i:i+2],16)/255 for i in (1,3,5)]
    ac,bc=[rgb(c) for c in a['colors']],[rgb(c) for c in b['colors']]
    def nearest(xs,ys):
        return sum(min(math.sqrt(sum((x-y)**2 for x,y in zip(u,v))/3) for v in ys) for u in xs)/len(xs)
    return (nearest(ac,bc)+nearest(bc,ac))/2


def select_palettes(brief,limit=3):
    catalog=load_catalog()
    background=brief.get('background','不限')
    if background not in ['不限','浅底','深底']:
        raise ValueError('background使用不限、浅底或深底。')
    required={normalize_hex(c) for c in brief.get('required_colors',[])}
    excluded={normalize_hex(c) for c in brief.get('excluded_colors',[])}
    if required & excluded:
        raise ValueError('同一个色号不能同时要求保留和排除。')
    if brief.get('custom_colors') and brief.get('palette_id') is not None:
        raise ValueError('指定编号和自定义色号不能同时作为配色来源。')
    def explicit(p,reason):
        codes={c['hex'] for c in p['colors']}
        if not required<=codes or excluded&codes or (brief.get('color_count') and len(codes)!=int(brief['color_count'])):
            raise ValueError('指定配色与要求保留、排除的色号或颜色数量有冲突。')
        return [{'palette':p,'roles':color_roles(p,background,brief.get('background_hex')),'reason':[reason]}]
    if brief.get('custom_colors'):
        p=custom_palette(brief['custom_colors'],brief.get('palette_name','自定配色'))
        return explicit(p,'采用用户自定义色号。')
    if brief.get('palette_id') is not None:
        p=next((p for p in catalog if p['id']==int(brief['palette_id'])),None)
        if not p:
            raise ValueError('编号应在1—100之间。')
        return explicit(p,'采用用户指定编号，不重新排名。')
    requested_topics,requested_moods=tags(brief.get('topics')),tags(brief.get('moods'))
    if not requested_topics and not requested_moods:
        raise ValueError('先判断文章的题材或情绪，再用结构化brief查表。')
    intensity=int(brief.get('intensity',3))
    if not 1<=intensity<=5:
        raise ValueError('intensity应在1—5之间。')
    purpose=ALIASES.get(brief.get('purpose'),brief.get('purpose'))
    ranked=[]
    for p in catalog:
        codes={c['hex'] for c in p['colors']}
        if not required<=codes or excluded&codes:
            continue
        if brief.get('color_count') and len(p['colors'])!=int(brief['color_count']):
            continue
        try:
            role=color_roles(p,background,brief.get('background_hex'))
        except ValueError:
            continue
        tm=requested_topics&tags(p['topics'])
        mm=requested_moods&tags(p['moods'])
        if not tm and not mm and not required:
            continue
        topic_score=20*len(tm)/max(1,len(requested_topics))
        mood_score=35*len(mm)/max(1,len(requested_moods))
        task_score=25 if purpose and purpose in p['purposes'] else 0
        intensity_score=20*(1-abs(intensity-p['intensity'])/4)
        score=topic_score+mood_score+task_score+intensity_score
        reasons=[]
        if tm: reasons.append('题材：'+'、'.join(sorted(tm)))
        if mm: reasons.append('情绪：'+'、'.join(sorted(mm)))
        if task_score: reasons.append('适合任务：'+purpose)
        reasons.append(f'视觉强度{p["intensity"]}/5，文章目标{intensity}/5')
        ranked.append({'palette':p,'roles':role,'score':round(score,2),'reason':reasons})
    ranked.sort(key=lambda r:(-r['score'],r['palette']['id']))
    chosen=[]
    for r in ranked:
        if not any(palette_distance(r['palette'],s['palette'])<0.065 for s in chosen):
            chosen.append(r)
        if len(chosen)>=limit:
            break
    if not chosen:
        raise ValueError('原100组中没有满足硬条件的配色；请使用自定义配色或说明哪项条件可以调整。')
    return chosen


def make_handoff(palette,title=None,background=None,background_hex=None,brief=None):
    """仅导出颜色与用法，不编排封面、不调用图像工具或其他Skill。"""
    brief=brief or {}
    background=background if background is not None else brief.get('background','不限')
    background_hex=background_hex if background_hex is not None else brief.get('background_hex')
    if brief.get('palette_id') is not None and (palette['id'] is None or int(brief['palette_id'])!=palette['id']):
        raise ValueError('交接编号与brief指定的编号冲突。')
    if brief.get('custom_colors') and palette['id'] is not None:
        raise ValueError('指定编号与brief自定义颜色不能同时使用。')
    constraints={k:brief[k] for k in ['required_colors','excluded_colors','color_count'] if k in brief}
    constraints.update(background=background,background_hex=background_hex)
    if palette['id'] is None:
        constraints.update(custom_colors=palette['colors'],palette_name=palette['name'])
    else:
        constraints['palette_id']=palette['id']
    roles=select_palettes(constraints,1)[0]['roles']
    def field(value,default):
        if isinstance(value,list):
            return '；'.join(str(v) for v in value) or default
        return str(value) if value is not None and str(value).strip() else default
    area_note='按主底、次色和少量点缀分工，不要求每个颜色均分面积。'
    if palette.get('source_usage_ratio'):
        if roles['background']['hex']==palette['colors'][0]['hex']:
            area_note='原清单建议按原色顺序约6:3:1使用，实际面积配合后续版式。'
        else:
            area_note='原清单有6:3:1建议；本次更换底色，以当前分工为准。'
    values={
        'title':field(title or brief.get('title'),'未提供标题'),
        'article_summary':field(brief.get('article_summary'),'未提供正文，只按已有信息提出选色建议。'),
        'article_message':field(brief.get('message'),'沿用文章原意，不增加结论。'),
        'article_moods':field(brief.get('moods'), '按文章语气判断'),
        'number':palette['number'],'palette_name':palette['name'],
        'color_lines':'\n'.join('- '+c['name']+' '+c['hex'] for c in palette['colors']),
        'background_hex':roles['background']['hex'],'title_hex':roles['title']['hex'],
        'body_hex':roles['body']['hex'],'accent_hex':roles['accent']['hex'],
        'title_note':'标题色仅适合大字，小字改用正文色。' if roles['title']['large_only'] else '仍需按实际落字区域复核对比。',
        'area_note':area_note,
        'style_context':field(brief.get('style_context',brief.get('visual_direction')),'未指定，由后续封面Skill决定。'),
        'palette_scope':field(brief.get('palette_scope'),'可设计的底面、标题字、关键词衬底和少量点缀；照片、肤色、产品原色和数据图例保留。'),
        'preserve_requirements':field(brief.get('preserve'),'保留用户标题、已有素材和明确要求。')}
    template=(ROOT/'templates/palette-handoff.md').read_text()
    missing=set(re.findall(r'\{\{(\w+)\}\}',template))-values.keys()
    if missing:
        raise ValueError('交接模板变量缺失：'+','.join(sorted(missing)))
    handoff=re.sub(r'\{\{(\w+)\}\}',lambda match:values[match.group(1)],template)
    return {'selection_only':True,'image_generated':False,'palette_id':palette['id'],
            'palette_name':palette['name'],'colors':palette['colors'],'roles':roles,
            'preview':str(ROOT/palette['preview']) if palette.get('preview') else None,
            'handoff':handoff,'next_step':'需要制作封面时，把配色方案交给另行安装的Punk或其他封面Skill；本脚本不会自动调用。'}


def load_brief(path):
    value=json.loads(Path(path).expanduser().read_text())
    if not isinstance(value,dict):
        raise ValueError('brief需为JSON对象。')
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    show=sub.add_parser('show');show.add_argument('id',type=int)
    sub.add_parser('vocabulary')
    select=sub.add_parser('select');select.add_argument('--brief',required=True);select.add_argument('--limit',type=int,default=3)
    handoff=sub.add_parser('handoff',help='导出配色方案交接单，不生成图片')
    source=handoff.add_mutually_exclusive_group(required=True)
    source.add_argument('--id',type=int);source.add_argument('--custom',nargs='+')
    handoff.add_argument('--name',default='自定配色');handoff.add_argument('--title')
    handoff.add_argument('--background',choices=['不限','浅底','深底']);handoff.add_argument('--background-hex')
    handoff.add_argument('--brief');handoff.add_argument('--out')
    args=parser.parse_args()
    try:
        if args.command=='vocabulary':
            catalog=load_catalog()
            result={key:sorted({v for p in catalog for v in p[key]}) for key in ['topics','moods','purposes']}
        elif args.command=='show':
            p=next((p for p in load_catalog() if p['id']==args.id),None)
            if p is None: raise ValueError('编号应在1—100之间。')
            result={'selection_only':True,'palette':p,'roles':color_roles(p),'preview':str(ROOT/p['preview'])}
        elif args.command=='select':
            if not 1<=args.limit<=10: raise ValueError('limit应在1—10之间。')
            brief=load_brief(args.brief)
            result={'selection_only':True,'article_summary':brief.get('article_summary'),'message':brief.get('message'),
                    'recommendations':select_palettes(brief,args.limit),'note':'按助手提炼的题材、情绪和任务排序，不代表脚本已经阅读或验证全文。'}
        else:
            if args.custom:
                p=custom_palette(args.custom,args.name)
            else:
                p=next((p for p in load_catalog() if p['id']==args.id),None)
                if p is None: raise ValueError('编号应在1—100之间。')
            brief=load_brief(args.brief) if args.brief else None
            result=make_handoff(p,args.title,args.background,args.background_hex,brief)
            if args.out:
                out=Path(args.out).expanduser();out.mkdir(parents=True,exist_ok=True)
                (out/'palette-handoff.md').write_text(result['handoff'])
                (out/'plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
                result['saved_to']=str(out.resolve())
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__=='__main__':
    main()
