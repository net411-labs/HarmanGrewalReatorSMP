#!/usr/bin/env python3
"""Render Harman Grewal branded social posts (1080x1350) from posts.json.

Usage: python3 build.py posts.json OUT_DIR
Each post in posts.json has a "template" key (stats_region, stats_city, insight,
brand, listing) plus that template's fields. Assets live in ../assets.
"""
import json, os, subprocess, sys, html, tempfile, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = (HERE.parent / "assets").as_uri()
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
W, H = 1080, 1350
e = html.escape

BASE_CSS = f"""
@font-face {{ font-family: 'PF'; src: url('{ASSETS}/pf.woff2'); font-weight: 400 900; }}
@font-face {{ font-family: 'PF'; src: url('{ASSETS}/pfi.woff2'); font-style: italic; font-weight: 400 900; }}
:root {{ --ink:#121214; --ink2:#1c1c20; --line:#2c2c32; --red:#E1262D; --red2:#ff5a5f;
         --gold:#C9AA6E; --paper:#F4F1EA; --mute:#9a9aa3; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{W}px; height:{H}px; overflow:hidden; background:var(--ink); }}
body {{ font-variant-numeric:lining-nums; font-family:'Inter',sans-serif; color:#fff; position:relative; }}
.serif {{ font-family:'PF',serif; font-variant-numeric:lining-nums; }}
.eyebrow {{ font-size:22px; letter-spacing:.32em; text-transform:uppercase; color:var(--gold); font-weight:600; }}
.frame {{ position:absolute; inset:0; padding:72px 72px 0; }}
.glow {{ position:absolute; border-radius:50%; filter:blur(10px); }}
.foot {{ position:absolute; left:0; right:0; bottom:0; height:150px; padding:0 72px;
        display:flex; align-items:center; gap:26px; border-top:1px solid var(--line); background:#0c0c0e; }}
.foot img.logo {{ width:96px; height:96px; }}
.foot .who {{ flex:1; }}
.foot .name {{ font-family:'PF',serif; font-size:34px; font-weight:700; }}
.foot .name i {{ color:var(--red2); }}
.foot .sub {{ font-size:16px; letter-spacing:.12em; white-space:nowrap; text-transform:uppercase; color:var(--mute); margin-top:6px; }}
.foot .ph {{ text-align:right; }}
.foot .ph b {{ display:block; font-size:36px; font-weight:700; letter-spacing:.02em; }}
.foot .ph span {{ font-size:16px; color:var(--mute); }}
.src {{ position:absolute; left:72px; right:72px; bottom:164px; font-size:15px; color:#6d6d75; line-height:1.4; }}
"""

def footer():
    return f"""<div class="foot">
  <img class="logo" src="{ASSETS}/hg_gold_t.png">
  <div class="who"><div class="name">Harman <i>Grewal</i></div>
    <div class="sub">Realtor® · Royal LePage Global Force Realty</div></div>
  <div class="ph"><b>604.562.4004</b><span>English · ਪੰਜਾਬੀ · हिन्दी</span></div>
</div>"""

def chg(v):
    """Format a signed % change; None means direction not published."""
    if v is None: return ""
    cls = "dn" if v < 0 else "up"
    arrow = "▼" if v < 0 else "▲"
    return f'<span class="chg {cls}">{arrow} {abs(v):.1f}%</span>'

def stats_region(p):
    rows = "".join(f"""<div class="row">
      <div class="k">{e(r['type'])}</div>
      <div class="v serif">{e(r['price'])}</div>
      <div class="c">{chg(r.get('yoy'))}<small>year over year</small></div></div>""" for r in p["rows"])
    kpis = "".join(f'<div class="kpi"><b class="serif">{e(k["value"])}</b><span>{e(k["label"])}</span></div>' for k in p["kpis"])
    return f"""<style>
.title {{ font-size:92px; line-height:1.02; font-weight:700; margin:22px 0 14px; }}
.title i {{ color:var(--red2); font-weight:500; }}
.lede {{ font-size:27px; color:#c8c8cf; line-height:1.4; max-width:880px; }}
.rows {{ margin-top:44px; border-top:1px solid var(--line); }}
.row {{ display:grid; grid-template-columns:1fr 1.1fr .9fr; align-items:center; padding:34px 0; border-bottom:1px solid var(--line); }}
.k {{ font-size:24px; color:#d9d9de; font-weight:500; }}
.v {{ font-size:60px; font-weight:700; }}
.c {{ text-align:right; }} .c small {{ display:block; font-size:15px; color:var(--mute); margin-top:4px; letter-spacing:.06em; }}
.chg {{ font-size:28px; font-weight:700; }} .dn {{ color:var(--red2); }} .up {{ color:#5fd38d; }}
.kpis {{ display:flex; gap:20px; margin-top:44px; }}
.kpi {{ flex:1; background:var(--ink2); border:1px solid var(--line); border-radius:18px; padding:22px 24px; }}
.kpi b {{ display:block; font-size:44px; color:var(--gold); }} .kpi span {{ font-size:18px; color:#b9b9c0; }}
</style>
<div class="glow" style="width:520px;height:520px;right:-180px;top:-200px;background:radial-gradient(circle,rgba(225,38,45,.55),transparent 65%)"></div>
<div class="frame">
  <div class="eyebrow">{e(p['eyebrow'])}</div>
  <h1 class="title serif">{p['title_html']}</h1>
  <p class="lede">{e(p['lede'])}</p>
  <div class="rows">{rows}</div>
  <div class="kpis">{kpis}</div>
</div>
<div class="src">{e(p['source'])}</div>{footer()}"""

def stats_city(p):
    cards = "".join(f"""<div class="pc"><span>{e(r['type'])}</span><b class="serif">{e(r['price'])}</b></div>""" for r in p["prices"])
    return f"""<style>
.city {{ font-size:170px; line-height:.9; font-weight:700; margin-top:18px; letter-spacing:-.01em; }}
.city i {{ color:var(--red2); font-weight:500; }}
.tag {{ display:inline-block; margin-top:26px; padding:12px 22px; border-radius:999px; background:var(--red); font-weight:700; font-size:22px; letter-spacing:.12em; text-transform:uppercase; }}
.pcs {{ display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:52px; }}
.pc {{ background:var(--ink2); border:1px solid var(--line); border-radius:20px; padding:28px 24px; }}
.pc span {{ font-size:19px; color:#b9b9c0; letter-spacing:.08em; text-transform:uppercase; }}
.pc b {{ display:block; font-size:50px; margin-top:12px; }}
.lbl {{ font-size:18px; color:var(--mute); letter-spacing:.2em; text-transform:uppercase; margin-top:22px; }}
.big {{ display:flex; gap:18px; margin-top:44px; }}
.big div {{ flex:1; border-top:2px solid var(--gold); padding-top:18px; }}
.big b {{ font-size:76px; font-family:'PF',serif; }} .big span {{ display:block; font-size:20px; color:#b9b9c0; margin-top:4px; }}
.note {{ margin-top:44px; font-size:29px; line-height:1.45; color:#dcdce1; max-width:900px; }}
.note b {{ color:var(--gold); font-weight:600; }}
.gauge {{ position:relative; margin-top:56px; }}
.gbar {{ display:flex; height:16px; border-radius:999px; overflow:hidden; }}
.gbar div {{ height:100%; }}
.gl {{ display:flex; margin-top:14px; font-size:17px; letter-spacing:.14em; text-transform:uppercase; color:var(--mute); }}
.gl span {{ text-align:center; }}
.pin {{ position:absolute; top:-12px; width:6px; height:40px; background:#fff; border-radius:3px; transform:translateX(-3px); box-shadow:0 0 0 4px rgba(18,18,20,.9); }}
</style>
<div class="glow" style="width:640px;height:640px;left:-260px;top:-260px;background:radial-gradient(circle,rgba(201,170,110,.28),transparent 65%)"></div>
<div class="frame">
  <div class="eyebrow">{e(p['eyebrow'])}</div>
  <div class="city serif">{p['city_html']}</div>
  <div class="tag">{e(p['tag'])}</div>
  <div class="lbl">Benchmark price</div>
  <div class="pcs" style="margin-top:14px">{cards}</div>
  <div class="big">{''.join(f'<div><b>{e(k["value"])}</b><span>{e(k["label"])}</span></div>' for k in p['kpis'])}</div>
  <div class="gauge">{gauge(p['ratio'])}</div>
  <p class="note">{p['note_html']}</p>
</div>
<div class="src">{e(p['source'])}</div>{footer()}"""

def gauge(r, top=25.0):
    """Sales-to-active bar: buyer's <12, balanced 12-20, seller's >20 (FVREB/GVR convention)."""
    a, b = 12 / top * 100, 8 / top * 100; c = 100 - a - b
    return (f'<div class="gbar"><div style="width:{a}%;background:#E1262D"></div>'
            f'<div style="width:{b}%;background:#C9AA6E"></div><div style="width:{c}%;background:#3a3a42"></div></div>'
            f'<div class="pin" style="left:{min(r, top) / top * 100}%"></div>'
            f'<div class="gl"><span style="width:{a}%">Buyer\'s</span><span style="width:{b}%">Balanced</span><span style="width:{c}%">Seller\'s</span></div>')

def insight(p):
    return f"""<style>
.num {{ font-size:230px; line-height:.9; font-weight:700; color:var(--paper); margin-top:60px; letter-spacing:-.02em; }}
.num i {{ color:var(--red2); }}
.cap {{ font-size:46px; line-height:1.18; margin-top:28px; max-width:900px; font-weight:500; }}
.cap i {{ color:var(--gold); }}
.body {{ font-size:28px; line-height:1.5; color:#c9c9cf; margin-top:36px; max-width:880px; }}
.cta {{ position:absolute; left:72px; bottom:230px; display:flex; align-items:center; gap:18px; font-size:26px; font-weight:600; }}
.cta span {{ background:var(--red); padding:16px 26px; border-radius:999px; }}
</style>
<div class="glow" style="width:900px;height:900px;right:-420px;bottom:-200px;background:radial-gradient(circle,rgba(225,38,45,.45),transparent 62%)"></div>
<div class="frame">
  <div class="eyebrow">{e(p['eyebrow'])}</div>
  <div class="num serif">{p['number_html']}</div>
  <div class="cap serif">{p['caption_html']}</div>
  <p class="body">{e(p['body'])}</p>
</div>
<div class="cta"><span>{e(p['cta'])}</span></div>
<div class="src">{e(p['source'])}</div>{footer()}"""

def brand(p):
    return f"""<style>
.disc {{ position:absolute; width:720px; height:720px; border-radius:50%; right:-260px; top:300px; background:var(--red); }}
.ring {{ position:absolute; width:860px; height:860px; border-radius:50%; right:-330px; top:230px; border:1px solid rgba(201,170,110,.5); }}
.photo {{ position:absolute; right:-150px; bottom:150px; height:980px; }}
.t {{ font-size:84px; line-height:1.02; font-weight:700; margin-top:22px; max-width:520px; position:relative; z-index:2; }}
.t i {{ color:var(--red2); font-weight:500; display:block; }}
.pts {{ margin-top:40px; position:relative; z-index:2; }}
.pts div {{ font-size:25px; padding:16px 0; border-bottom:1px solid var(--line); width:430px; background:linear-gradient(90deg,var(--ink) 80%,transparent); color:#dcdce1; }}
.pts b {{ color:var(--gold); font-family:'PF',serif; margin-right:14px; }}
</style>
<div class="ring"></div><div class="disc"></div>
<img class="photo" src="{ASSETS}/harman_cut.png">
<div class="frame">
  <div class="eyebrow">{e(p['eyebrow'])}</div>
  <div class="t serif">{p['title_html']}</div>
  <div class="pts">{''.join(f'<div><b>{i+1:02d}</b>{e(t)}</div>' for i,t in enumerate(p['points']))}</div>
</div>{footer()}"""

def listing(p):
    photo = f"url('{p['photo']}')" if p.get("photo") else "linear-gradient(135deg,#3a3a42,#1d1d22)"
    facts = "".join(f'<div><b class="serif">{e(v)}</b><span>{e(k)}</span></div>' for k, v in p["facts"])
    return f"""<style>
.hero {{ position:absolute; left:0; right:0; top:0; height:760px; background:{photo} center/cover; }}
.hero:after {{ content:''; position:absolute; inset:0; background:linear-gradient(180deg,rgba(0,0,0,.25),transparent 30%,transparent 60%,var(--ink)); }}
.badge {{ position:absolute; top:60px; left:60px; z-index:2; background:var(--red); padding:16px 28px; font-weight:800; letter-spacing:.2em; font-size:26px; text-transform:uppercase; }}
.info {{ position:absolute; left:72px; right:72px; top:690px; z-index:2; }}
.price {{ font-size:96px; font-weight:700; }}
.addr {{ font-size:34px; margin-top:6px; color:#e6e6ea; }} .area {{ color:var(--gold); font-size:22px; letter-spacing:.24em; text-transform:uppercase; margin-top:12px; }}
.facts {{ display:flex; gap:16px; margin-top:34px; }}
.facts div {{ flex:1; border:1px solid var(--line); background:var(--ink2); border-radius:16px; padding:18px 20px; }}
.facts b {{ display:block; font-size:42px; }} .facts span {{ font-size:18px; color:#b9b9c0; }}
</style>
<div class="hero"></div><div class="badge">{e(p['badge'])}</div>
<div class="info"><div class="price serif">{e(p['price'])}</div><div class="addr">{e(p['address'])}</div>
<div class="area">{e(p['area'])}</div><div class="facts">{facts}</div></div>
<div class="src">{e(p.get('source',''))}</div>{footer()}"""

TEMPLATES = dict(stats_region=stats_region, stats_city=stats_city, insight=insight, brand=brand, listing=listing)

def render(post, out_png):
    body = TEMPLATES[post["template"]](post)
    doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE_CSS}</style></head><body>{body}</body></html>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(doc); tmp = f.name
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--allow-file-access-from-files", f"--window-size={W},{H+200}", "--virtual-time-budget=3000",
                    f"--screenshot={out_png}", pathlib.Path(tmp).as_uri()],
                   check=True, capture_output=True)
    os.unlink(tmp)
    from PIL import Image
    Image.open(out_png).crop((0, 0, W, H)).save(out_png)

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    md = [f"# {spec['title']}\n"]
    for post in spec["posts"]:
        png = out / f"{post['id']}.png"
        render(post, str(png)); print("rendered", png)
        md.append(f"## {post['id']}  ·  post on {post['date']}\n\nImage: `{png.name}`\n\n{post['caption'].strip()}\n")
    (out / "captions.md").write_text("\n".join(md))
