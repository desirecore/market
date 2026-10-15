#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    slides = manifest["slides"]
    manifest_json = json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
    document = f'''<!doctype html>
<meta charset="utf-8">
<title>{esc(manifest.get('session_id'))} · Presentation Forge Canvas</title>
<style>
  :root{{--panel:#191e2a;--line:#354052;--ink:#f3f6ff;--muted:#9da8bd;--accent:#4f7cff;--thumb-width:160px;--inspector-width:320px}}
  *{{box-sizing:border-box}} body{{margin:0;background:#0f131d;color:var(--ink);font:14px Inter,"PingFang SC",sans-serif}}
  button{{font:inherit;color:inherit}} .app{{height:100vh;display:grid;grid-template-rows:52px 1fr}}
  header{{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:0 16px;background:var(--panel);border-bottom:1px solid var(--line)}}
  .header-actions{{display:flex;align-items:center;gap:8px}} .toolbar{{border:1px solid var(--line);background:#111520;padding:7px 10px;cursor:pointer}}
  .status{{color:var(--muted)}} .export{{border:0;background:#315efb;padding:8px 14px;cursor:pointer}}
  .main{{display:grid;grid-template-columns:var(--thumb-width) minmax(0,1fr) var(--inspector-width);min-height:0;transition:grid-template-columns .18s ease}}
  body.thumbs-collapsed .main{{grid-template-columns:0 minmax(0,1fr) var(--inspector-width)}}
  body.inspector-collapsed .main{{grid-template-columns:var(--thumb-width) minmax(0,1fr) 0}}
  body.thumbs-collapsed.inspector-collapsed .main,body.focus-canvas .main{{grid-template-columns:0 minmax(0,1fr) 0}}
  body.thumbs-collapsed .thumbs,body.focus-canvas .thumbs{{display:none}}
  body.inspector-collapsed aside.props,body.focus-canvas aside.props{{display:none}}
  .thumbs{{overflow:auto;padding:12px;background:#151a25;border-right:1px solid var(--line)}}
  .thumb{{display:block;width:100%;margin:0 0 10px;padding:8px;text-align:left;background:#222938;border:1px solid #3a4353;cursor:pointer}}
  .thumb.active{{outline:2px solid #6e8dff}} .thumb-title{{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}} .thumb-meta{{color:var(--muted);font-size:11px}}
  .stage-wrap{{display:flex;align-items:center;justify-content:center;overflow:auto;padding:16px;background:#111520}}
  .stage{{position:relative;width:min(100%,calc((100vh - 84px)*16/9));min-width:746px;min-height:420px;aspect-ratio:16/9;background:#0a0f1e;overflow:hidden;box-shadow:0 18px 60px #0008}}
  .element{{position:absolute;transform-origin:center;white-space:pre-wrap;overflow:hidden}}
  .element[data-type=text]{{display:flex;padding:2px}}
  .element[data-editable=true]{{cursor:text}} .element.selected{{outline:2px solid #ffd056;outline-offset:2px}}
  .shape{{border-style:solid}} .connector{{height:0!important;transform-origin:left center;border-top-style:solid}}
  aside.props{{padding:14px;background:var(--panel);border-left:1px solid var(--line);overflow:auto}}
  .field{{margin:0 0 14px}} label{{display:block;color:var(--muted);margin-bottom:5px}} input{{width:100%;background:#111520;color:var(--ink);border:1px solid var(--line);padding:7px}}
  .empty{{color:var(--muted)}} .count{{color:#25d0d8}}
  @media(max-width:1100px){{:root{{--thumb-width:128px;--inspector-width:300px}}}}
</style>
<body class="inspector-collapsed">
<div class="app">
  <header><div><strong>{esc(manifest.get('session_id'))}</strong> <span class="status" id="status">画布编辑中 · <span class="count">{len(slides)} 页</span></span></div><div class="header-actions"><button class="toolbar" id="toggle-thumbs">页面列表</button><button class="toolbar" id="toggle-inspector">对象编辑</button><button class="toolbar" id="focus-canvas">专注画布</button><button class="export" id="export">导出 PPTX</button></div></header>
  <div class="main">
    <nav class="thumbs" id="thumbs"></nav>
    <main class="stage-wrap"><section class="stage" id="stage"></section></main>
    <aside class="props"><section id="object-panel"><h3 id="page-title">页面</h3><div id="props" class="empty">请选择文字对象进行编辑。</div></section></aside>
  </div>
</div>
<script type="application/json" id="manifest">{manifest_json}</script>
<script>
(() => {{
  const manifest = JSON.parse(document.querySelector('#manifest').textContent);
  if (manifest.slide_count !== manifest.slides.length) throw new Error('slide_count 与 slides 长度不一致');
  const state = structuredClone(manifest.slides);
  const thumbs = document.querySelector('#thumbs'), stage = document.querySelector('#stage'), props = document.querySelector('#props');
  let active = 0, selected = null, sourceMarkdown = manifest.authoring?.markdown || '';
  const pct = (v,total) => `${{v/total*100}}%`;
  const renderThumbs = () => {{
    thumbs.innerHTML = '';
    state.forEach((slide,index) => {{
      const b=document.createElement('button'); b.className='thumb'+(index===active?' active':''); b.type='button';
      b.innerHTML=`<span class="thumb-title">${{slide.slide_number}}. ${{slide.title}}</span><span class="thumb-meta">${{slide.archetype||'slide'}} · ${{slide.elements.length}} 个对象</span>`;
      b.onclick=()=>{{active=index; selected=null; render();}}; thumbs.appendChild(b);
    }});
  }};
  const renderProps = () => {{
    document.querySelector('#page-title').textContent=`第 ${{state[active].slide_number}} 页 · ${{state[active].title}}`;
    if(!selected || selected.type!=='text'){{props.className='empty'; props.textContent='请选择文字对象进行编辑。'; return;}}
    props.className=''; props.innerHTML=`<div class="field"><label>对象</label><input value="${{selected.id}}" disabled></div><div class="field"><label>文字</label><input id="text-value"></div><div class="field"><label>字号（pt）</label><input id="font-size" type="number" step="0.5"></div><div class="field"><label>颜色</label><input id="font-color" type="color"></div>`;
    document.querySelector('#text-value').value=selected.text||''; document.querySelector('#font-size').value=selected.style?.font_size_pt||18; document.querySelector('#font-color').value='#'+(selected.style?.font_color||'F7F9FF');
    document.querySelector('#text-value').oninput=e=>{{selected.text=e.target.value; renderStage();}};
    document.querySelector('#font-size').oninput=e=>{{selected.style.font_size_pt=Number(e.target.value); renderStage();}};
    document.querySelector('#font-color').oninput=e=>{{selected.style.font_color=e.target.value.slice(1).toUpperCase(); renderStage();}};
  }};
  const renderStage = () => {{
    const slide=state[active], c=slide.canvas||{{width:1920,height:1080}}; stage.innerHTML='';
    const preset=manifest.style_catalog.find(x=>x.style_id===slide.style.style_id&&x.variant_id===slide.style.variant_id)||manifest.style_catalog[0];
    const bg=Array.isArray(preset.design_tokens.background)?preset.design_tokens.background[0]:preset.design_tokens.background; stage.style.background=bg;
    [...slide.elements].sort((a,b)=>(a.z_index||0)-(b.z_index||0)).forEach(el=>{{
      const node=document.createElement('div'); node.dataset.type=el.type; node.dataset.editable=String(el.editable!==false); node.className='element '+(el.type==='shape'?'shape':el.type==='connector'?'connector':'')+(selected===el?' selected':'');
      const [x,y,w,h]=el.bbox; Object.assign(node.style,{{left:pct(x,c.width),top:pct(y,c.height),width:pct(w,c.width),height:pct(h,c.height),zIndex:el.z_index||0,transform:`rotate(${{el.rotation||0}}deg)`}});
      const s=el.style||{{}}; if(s.fill)node.style.background='#'+s.fill; if(s.line)node.style.borderColor='#'+s.line; node.style.borderWidth=(s.line_width_pt||0)+'px';
      if(el.type==='shape'){{node.style.borderRadius=['ellipse','oval'].includes(el.geometry)?'50%':el.geometry==='rounded_rectangle'?'12px':'0';}}
      if(el.type==='connector'){{const length=Math.hypot(w,h);node.style.width=pct(length,c.width);node.style.height='0';node.style.transform=`rotate(${{Math.atan2(h,w)*180/Math.PI+(el.rotation||0)}}deg)`;}}
      if(el.type==='text'){{node.textContent=el.text||''; node.contentEditable=el.editable!==false; node.style.fontSize=`${{(s.font_size_pt||18)*4/3*stage.clientWidth/c.width}}px`; node.style.color='#'+(s.font_color||'F7F9FF'); node.style.fontWeight=s.bold?'700':'400'; node.style.textAlign=s.align||'left'; node.style.alignItems=s.vertical_align==='top'?'flex-start':s.vertical_align==='bottom'?'flex-end':'center'; node.oninput=()=>{{el.text=node.textContent;}};}}
      node.onclick=e=>{{e.stopPropagation();selected=el;if(el.type==='text')document.body.classList.remove('inspector-collapsed','focus-canvas');renderProps();stage.querySelectorAll('.selected').forEach(n=>n.classList.remove('selected'));node.classList.add('selected');}}; stage.appendChild(node);
    }});
  }};
  const render=()=>{{renderThumbs();renderStage();renderProps();}}; stage.onclick=()=>{{selected=null;renderProps();}};
  document.querySelector('#toggle-thumbs').onclick=()=>{{document.body.classList.remove('focus-canvas');document.body.classList.toggle('thumbs-collapsed');}};
  document.querySelector('#toggle-inspector').onclick=()=>{{document.body.classList.remove('focus-canvas');document.body.classList.toggle('inspector-collapsed');}};
  document.querySelector('#focus-canvas').onclick=()=>document.body.classList.toggle('focus-canvas');
  document.querySelector('#export').onclick=async()=>{{
    const payload={{schema_version:1,session_id:manifest.session_id,base_revision:manifest.base_revision,document_sha256:manifest.document_sha256,canvas_sha256:manifest.canvas_sha256,slide_count:state.length,slides_markdown:sourceMarkdown,slides:state.map(s=>({{slide_number:s.slide_number,title:s.title,archetype:s.archetype,style:s.style,canvas:s.canvas,elements:s.elements}}))}};
    if(!window.openai||typeof window.openai.sendFollowUpMessage!=='function'){{document.querySelector('#status').textContent='当前环境不能提交导出';return;}}
    await window.openai.sendFollowUpMessage({{title:'导出画布同版 PPTX',prompt:`使用 presentation-forge 导出以下完整 Markdown + canvas-first 状态。先把 slides_markdown 写回 session/slides.md 并编译；再应用全部 ${{payload.slide_count}} 页 scene 的对象、坐标、样式和层级。若 Markdown 内容与画布对象文字冲突，以当前画布对象为准并回写 Markdown。PPTX 必须与画布同页数、同对象、同文字、同坐标、同样式；禁止另起布局或只提交封面。画布状态：${{JSON.stringify(payload)}}`}});
    document.querySelector('#status').textContent=`已提交 ${{payload.slide_count}} 页完整画布状态`;
  }};
  render();
}})();
</script>'''
    Path(args.out).write_text(document, encoding="utf-8")
    print(json.dumps({"status": "PASS", "slide_count": len(slides), "out": str(Path(args.out).resolve())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
