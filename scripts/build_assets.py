"""Generate the animated SVGs used by the profile README.

Edit the ROLES / TERMINAL lists below, then run:  python scripts/build_assets.py
All animation is SMIL + CSS inside the SVG, so it plays on GitHub with no external service.
"""

from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"

SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
CHAR = 0.6  # monospace advance in em; textLength pins every glyph to this grid

# Lines cycled by the typing effect in the header
ROLES = [
    "President @ Salva Import",
    "BSc AIDAMS @ CentraleSupélec × ESSEC",
    "Dassault UAV Challenge finalist",
    "ML · Computer Vision · Multi-agent AI",
    "Runner · Electroacoustic sound design",
]

# Terminal session: ("cmd", text) is typed, ("out", [(text, color), ...]) is printed, ("gap",) is a half line
TERMINAL = [
    ("cmd", "whoami"),
    ("out", [("Nicolas Salapete", "#e6edf3"), (" · 21 · Cergy, France", "#8b949e")]),
    ("out", [("BSc AI, Data & Management Sciences", "#d2a8ff"), (" @ CentraleSupélec × ESSEC ", "#e6edf3"),
             ("(2024–2027) · GPA 4.00/4", "#8b949e")]),
    ("gap",),
    ("cmd", "cat now.txt"),
    ("out", [("President @ Salva Import", "#ffa657"),
             (" — taking premium Colombian spirits, fine food & crafts to Europe", "#e6edf3")]),
    ("gap",),
    ("cmd", "ls ~/projects"),
    ("out", [("set-weaver/  football-scout-agent/  emoji-classifier/  serica/  olympus-uav/", "#79c0ff")]),
    ("gap",),
    ("cmd", "echo $LANG"),
    ("out", [("fr_FR", "#7ee787"), (" (native) · ", "#8b949e"), ("en_US", "#7ee787"), (" (C1) · ", "#8b949e"),
             ("es_ES", "#7ee787"), (" (bilingual)", "#8b949e")]),
    ("gap",),
    ("prompt",),
]


def f(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def discrete(attr, events, total, base=None):
    """SMIL animate that jumps through (time, value) events and loops every `total` seconds."""
    events = sorted(events)
    times, values = [], []
    for t, v in events:
        k = t / total
        if times and k <= times[-1]:
            k = times[-1] + 1e-4
        times.append(k)
        values.append(v)
    if times[0] != 0:
        times.insert(0, 0)
        values.insert(0, base if base is not None else values[0])
    return (f'<animate attributeName="{attr}" calcMode="discrete" dur="{f(total)}s" repeatCount="indefinite" '
            f'keyTimes="{";".join(f(k) for k in times)}" values="{";".join(f(v) if isinstance(v, float) else str(v) for v in values)}"/>')


# --------------------------------------------------------------------------- header

def build_header():
    W, H = 1000, 330
    fs, cw = 20, 20 * CHAR
    x_prompt, x_text, y_text = 60, 84, 254
    type_dt, delete_dt, hold, gap = 0.075, 0.035, 1.9, 0.35

    windows, t = [], 0.4
    for role in ROLES:
        n = len(role)
        windows.append((t, n))
        t += n * type_dt + hold + n * delete_dt + gap
    total = t

    clips, texts, cursor_events = [], [], [(0, x_text)]
    for i, (role, (start, n)) in enumerate(zip(ROLES, windows)):
        ev = [(0, 0.0)]
        for k in range(1, n + 1):
            ev.append((start + k * type_dt, k * cw))
        end_type = start + n * type_dt + hold
        for k in range(1, n + 1):
            ev.append((end_type + k * delete_dt, (n - k) * cw))
        cursor_events += [(tt, x_text + w) for tt, w in ev[1:]]
        base = n * cw if i == 0 else 0
        clips.append(f'<clipPath id="r{i}"><rect x="{x_text}" y="{y_text - fs - 2}" width="{f(base)}" height="{fs + 12}">'
                     f'{discrete("width", ev, total)}</rect></clipPath>')
        texts.append(f'<text class="mono role" x="{x_text}" y="{y_text}" textLength="{f(n * cw)}" lengthAdjust="spacing" '
                     f'clip-path="url(#r{i})">{escape(role)}</text>')

    # Neural net on the right: three layers, pulses travelling input -> output
    layers = [(700, [110, 165, 220]), (800, [85, 138, 192, 245]), (900, [135, 195])]
    edges = []
    for (xa, ya), (xb, yb) in zip(layers, layers[1:]):
        for y1 in ya:
            for y2 in yb:
                edges.append(f'<line x1="{xa}" y1="{y1}" x2="{xb}" y2="{y2}"/>')
    routes = [(0, 0, 0), (1, 2, 1), (2, 3, 1), (0, 1, 0), (1, 1, 1), (2, 2, 0), (0, 3, 1), (1, 0, 0)]
    pulses = []
    for i, (a, b, c) in enumerate(routes):
        d = f"M{layers[0][0]} {layers[0][1][a]} L{layers[1][0]} {layers[1][1][b]} L{layers[2][0]} {layers[2][1][c]}"
        begin = f(i * 0.45)
        pulses.append(
            f'<circle r="3.2" class="pulse"><animateMotion dur="2.4s" begin="{begin}s" repeatCount="indefinite" path="{d}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="2.4s" begin="{begin}s" repeatCount="indefinite"/></circle>')
    nodes = []
    for li, (x, ys) in enumerate(layers):
        for j, y in enumerate(ys):
            cls = "node out" if li == 2 else "node"
            delay = f((li * 4 + j) * 0.37)
            nodes.append(
                f'<circle cx="{x}" cy="{y}" r="7" class="ring{" out" if li == 2 else ""}" fill="none">'
                f'<animate attributeName="r" values="7;17" dur="3s" begin="{delay}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0.6;0" dur="3s" begin="{delay}s" repeatCount="indefinite"/></circle>'
                f'<circle cx="{x}" cy="{y}" r="7" class="{cls}"/>')

    def drift(dx, dy, dur):
        return (f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" keyTimes="0;0.5;1" '
                f'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" dur="{dur}s" repeatCount="indefinite"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
<title id="title">Nicolas Salapete — BSc AI, Data &amp; Management Sciences at CentraleSupélec × ESSEC</title>
<style>
  .sans {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .hello {{ font-size: 17px; fill: #7dd3fc; letter-spacing: 0.5px; }}
  .name {{ font-size: 60px; font-weight: 800; letter-spacing: -1.5px; }}
  .sub {{ font-size: 19px; fill: #a5b4fc; }}
  .role {{ font-size: {fs}px; fill: #e2e8f0; }}
  .prompt {{ font-size: {fs}px; fill: #f472b6; font-weight: 700; }}
  .caption {{ font-size: 13px; fill: #64748b; }}
  .net line {{ stroke: #a5b4fc; stroke-opacity: 0.16; stroke-width: 1; }}
  .node {{ fill: #0b1024; stroke: #818cf8; stroke-width: 2; }}
  .node.out {{ stroke: #f472b6; }}
  .ring {{ stroke: #818cf8; stroke-width: 1.5; }}
  .ring.out {{ stroke: #f472b6; }}
  .pulse {{ fill: #7dd3fc; }}
  .rise {{ animation: rise 0.9s cubic-bezier(.2,.7,.2,1) both; }}
  .d1 {{ animation-delay: 0.15s; }} .d2 {{ animation-delay: 0.3s; }} .d3 {{ animation-delay: 0.45s; }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  .bar {{ transform-origin: 60px 0; animation: grow 0.8s 0.5s cubic-bezier(.2,.7,.2,1) both; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .cursor {{ fill: #7dd3fc; animation: blink 1s steps(1) infinite; }}
  @media (prefers-reduced-motion: reduce) {{ .rise, .bar {{ animation: none; opacity: 1; transform: none; }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#060a17"/><stop offset="1" stop-color="#121a3d"/></linearGradient>
  <linearGradient id="ink" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset="0.55" stop-color="#c7d2fe"/><stop offset="1" stop-color="#f9a8d4"/></linearGradient>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8"/><stop offset="0.5" stop-color="#818cf8"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
  <filter id="blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="55"/></filter>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="#ffffff" fill-opacity="0.06"/></pattern>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="20"/></clipPath>
  {"".join(clips)}
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g filter="url(#blur)" opacity="0.6">
    <circle cx="790" cy="70" r="130" fill="#6366f1">{drift(-70, 45, 16)}</circle>
    <circle cx="930" cy="310" r="115" fill="#db2777">{drift(-50, -60, 19)}</circle>
    <circle cx="120" cy="340" r="150" fill="#0284c7" opacity="0.55">{drift(90, -30, 22)}</circle>
  </g>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <g class="net">{"".join(edges)}{"".join(pulses)}{"".join(nodes)}</g>
  <text class="mono hello rise" x="62" y="88">hello, world! I'm</text>
  <text class="sans name rise d1" x="58" y="152" fill="url(#ink)">Nicolas Salapete</text>
  <rect class="bar" x="60" y="172" width="86" height="4" rx="2" fill="url(#accent)"/>
  <text class="sans sub rise d2" x="60" y="206">BSc AI, Data &amp; Management Sciences — CentraleSupélec × ESSEC</text>
  <g class="rise d3">
    <text class="mono prompt" x="{x_prompt}" y="{y_text}">$</text>
    {"".join(texts)}
    <rect class="cursor" x="{x_text}" y="{y_text - fs + 2}" width="{f(cw * 0.55)}" height="{fs + 2}" rx="1">{discrete("x", cursor_events, total)}</rect>
  </g>
  <text class="mono caption" x="{W - 40}" y="{H - 24}" text-anchor="end">// model.fit(curiosity, epochs=∞)</text>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
</svg>
'''
    (ASSETS / "header.svg").write_text(svg, encoding="utf-8")


# --------------------------------------------------------------------------- terminal

def build_terminal():
    W = 1000
    fs, cw, lh = 15, 15 * CHAR, 25
    x0, y0, bar = 28, 74, 40
    type_dt, out_delay, next_delay, hold = 0.07, 0.25, 0.55, 6.0
    prompt_len = len("nicolas@salapete:~$ ")

    rows, y = [], y0
    for step in TERMINAL:
        if step[0] == "gap":
            y += lh // 2
            continue
        rows.append((step, y))
        y += lh
    H = y - lh + 30

    # Timeline: when each row appears, and where the cursor sits while commands are typed
    t, prev, timed = 0.6, None, []
    for step, y in rows:
        kind = step[0]
        if kind in ("cmd", "prompt") and prev == "out":
            t += next_delay
        timed.append((step, y, t))
        if kind == "cmd":
            t += len(step[1]) * type_dt + out_delay
        elif kind == "out":
            t += 0.12
        prev = kind
    total = t + hold

    cursor = []
    for step, y, start in timed:
        if step[0] in ("cmd", "prompt"):
            n = len(step[1]) if step[0] == "cmd" else 0
            cursor += [(start + k * type_dt, x0 + (prompt_len + k) * cw, y) for k in range(n + 1)]

    def show(start):
        return discrete("opacity", [(0, 0), (start, 1)], total)

    def prompt_text(y):
        return (f'<text class="mono t" x="{x0}" y="{y}" textLength="{f((prompt_len - 1) * cw)}" lengthAdjust="spacing">'
                f'<tspan fill="#7ee787">nicolas@salapete</tspan><tspan fill="#e6edf3">:</tspan>'
                f'<tspan fill="#79c0ff">~</tspan><tspan fill="#e6edf3">$</tspan></text>')

    body, clips = [], []
    for i, (step, y, start) in enumerate(timed):
        if step[0] in ("cmd", "prompt"):
            parts = [prompt_text(y)]
            if step[0] == "cmd":
                text, n = step[1], len(step[1])
                xc = x0 + prompt_len * cw
                ev = [(0, 0.0)] + [(start + k * type_dt, k * cw) for k in range(1, n + 1)]
                clips.append(f'<clipPath id="c{i}"><rect x="{f(xc)}" y="{y - fs - 2}" width="{f(n * cw)}" height="{fs + 10}">'
                             f'{discrete("width", ev, total)}</rect></clipPath>')
                parts.append(f'<text class="mono t" x="{f(xc)}" y="{y}" fill="#e6edf3" textLength="{f(n * cw)}" '
                             f'lengthAdjust="spacing" clip-path="url(#c{i})">{escape(text)}</text>')
            body.append(f'<g>{show(start)}{"".join(parts)}</g>')
        else:
            spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in step[1])
            body.append(f'<text class="mono t" x="{x0 + 2 * cw}" y="{y}">{show(start)}{spans}</text>')

    first_y = rows[0][1]
    cur_x = discrete("x", [(tt, f(x)) for tt, x, _ in cursor], total)
    cur_y = discrete("y", [(tt, f(yy - fs + 2)) for tt, _, yy in cursor], total)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
<title id="title">Terminal: whoami — Nicolas Salapete, BSc AI, Data &amp; Management Sciences at CentraleSupélec × ESSEC; President of Salva Import; projects and languages</title>
<style>
  .mono {{ font-family: {MONO}; }}
  .t {{ font-size: {fs}px; }}
  .title {{ font-size: 13px; fill: #8b949e; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .cursor {{ fill: #e6edf3; fill-opacity: 0.85; animation: blink 1s steps(1) infinite; }}
</style>
<defs>{"".join(clips)}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="#0d1117" stroke="#30363d"/>
<path d="M0.5 {bar} V12.5 A12 12 0 0 1 12.5 0.5 H{W - 12.5} A12 12 0 0 1 {W - 0.5} 12.5 V{bar} Z" fill="#161b22"/>
<line x1="0.5" y1="{bar}" x2="{W - 0.5}" y2="{bar}" stroke="#30363d"/>
<circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/><circle cx="62" cy="20" r="6" fill="#28c840"/>
<text class="mono title" x="{W / 2}" y="25" text-anchor="middle">nicolas@salapete: ~</text>
{"".join(body)}
<rect class="cursor" x="{f(x0 + prompt_len * cw)}" y="{first_y - fs + 2}" width="{f(cw)}" height="{fs + 3}">{cur_x}{cur_y}</rect>
</svg>
'''
    (ASSETS / "terminal.svg").write_text(svg, encoding="utf-8")


# --------------------------------------------------------------------------- footer

def build_footer():
    W, H, period = 1000, 120, 500

    def wave(base, amp, phase):
        y1, y2 = base - amp * phase, base + amp * phase
        d = f"M0 {base} Q{period / 4} {y1} {period / 2} {base} T{period} {base}"
        for x in range(period + period // 2, 2 * W + period, period // 2):
            d += f" T{x} {base}"
        return d + f" L{2 * W + period} {H} L0 {H} Z"

    layers = [
        (wave(58, 22, 1), "#0ea5e9", 0.35, 13),
        (wave(70, 18, -1), "#6366f1", 0.45, 9),
        (wave(84, 14, 1), "#ec4899", 0.4, 6),
    ]
    paths = "".join(
        f'<path d="{d}" fill="{c}" fill-opacity="{o}"><animateTransform attributeName="transform" type="translate" '
        f'from="0 0" to="-{period} 0" dur="{s}s" repeatCount="indefinite"/></path>'
        for d, c, o, s in layers)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated waves">
<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.35" stop-color="#fff"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>
<g mask="url(#m)">{paths}</g>
</svg>
'''
    (ASSETS / "footer.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    build_header()
    build_terminal()
    build_footer()
    print("wrote", ", ".join(p.name for p in sorted(ASSETS.glob("*.svg"))))
