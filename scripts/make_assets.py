"""生成首页 README 用的 SVG 素材（头图 / 终端面板 / 语言卡 / 状态徽标），亮暗两套。

只依赖标准库，改文字或配色后重跑即可：

    python scripts/make_assets.py

产出（全部落在 assets/）：
    banner-light.svg / banner-dark.svg      顶部头图（名字 + 方向 + 雷达纹）
    terminal-light.svg / terminal-dark.svg  终端面板（带光标闪烁动画）
    langcard-light.svg / langcard-dark.svg  语言构成条（按公开仓库字节统计）
    status-<名称>-light.svg / -dark.svg     状态徽标（在做 / 已完成 / 在学）

约定：SVG 里只写系统字体族，不引用外部资源，所以在 GitHub 的 <img> 里也能正常显示；
CSS/SMIL 动画在 <img> 中同样会跑。
"""
from pathlib import Path
import json
import os
import sys
import time
import urllib.request
from datetime import date

ASSETS = Path(__file__).resolve().parents[1] / "assets"

OWNER = "junlume"
DISPLAY = "xinjun"

THEMES = {
    "light": {
        "bg": "#ffffff",
        "border": "#d8dee4",
        "grid": "#0969da",
        "title": "#0a0f16",
        "sub": "#57606a",
        "accent": "#0e7490",
        "accent2": "#b45309",
        "chip_bg": "#f6f8fa",
        "chip_border": "#d8dee4",
        "term_bg": "#f6f8fa",
        "term_head": "#eaEEF2".lower(),
        "term_dot": ("#ff5f57", "#febc2e", "#28c840"),
        "ok": "#1a7f37",
        "warn": "#9a6700",
        "dim": "#8c959f",
        "glow": "#0e7490",
    },
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "grid": "#58a6ff",
        "title": "#e6edf3",
        "sub": "#8b949e",
        "accent": "#22d3ee",
        "accent2": "#f59e0b",
        "chip_bg": "#161b22",
        "chip_border": "#30363d",
        "term_bg": "#0b0f14",
        "term_head": "#161b22",
        "term_dot": ("#ff5f57", "#febc2e", "#28c840"),
        "ok": "#3fb950",
        "warn": "#d29922",
        "dim": "#6e7681",
        "glow": "#22d3ee",
    },
}

MONO = ("ui-monospace, SFMono-Regular, Menlo, Consolas, 'Courier New', "
        "'Noto Sans SC', 'Microsoft YaHei', monospace")
SERIF = ("'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, "
         "'Noto Serif SC', 'Songti SC', 'SimSun', serif")
SANS = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', "
        "'Microsoft YaHei', sans-serif")


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chip(x: float, y: float, text: str, c: dict, h: int = 30, size: int = 14) -> tuple[str, float]:
    w = 22 + len(text) * 8.4
    svg = (
        f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="{h / 2:.0f}" '
        f'fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" />'
        f'<text x="{x + w / 2:.0f}" y="{y + h / 2 + 5:.0f}" text-anchor="middle" font-size="{size}" '
        f'font-family="{MONO}" fill="{c["sub"]}">{esc(text)}</text>'
    )
    return svg, w


def banner(theme: str, eyebrow: str, name: str, tagline: str, chips: list[str],
           radar_label: str) -> str:
    c = THEMES[theme]
    w, h = 1280, 292
    parts = []
    x = 64
    for text in chips:
        svg, cw = chip(x, 220, text, c)
        parts.append(svg)
        x += cw + 12

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(name)} — {esc(tagline)}">
  <defs>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M28 0H0V28" fill="none" stroke="{c["grid"]}" stroke-opacity="0.06" stroke-width="1" />
    </pattern>
    <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{c["accent"]}" />
      <stop offset="100%" stop-color="{c["accent2"]}" />
    </linearGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{c["glow"]}" stop-opacity="0.34" />
      <stop offset="100%" stop-color="{c["glow"]}" stop-opacity="0" />
    </linearGradient>
  </defs>

  <rect width="{w}" height="{h}" rx="20" fill="{c["bg"]}" stroke="{c["border"]}" />
  <rect width="{w}" height="{h}" rx="20" fill="url(#grid)" />
  <rect x="0" y="40" width="5" height="{h - 80}" rx="2.5" fill="url(#bar)" />

  <text x="64" y="88" font-size="13" letter-spacing="4.2"
        font-family="{MONO}" fill="{c["accent"]}">{esc(eyebrow)}</text>
  <text x="62" y="158" font-size="60" font-weight="700" letter-spacing="0.5"
        font-family="{SERIF}" fill="{c["title"]}">{esc(name)}</text>
  <text x="66" y="198" font-size="18.5" letter-spacing="1.1"
        font-family="{MONO}" fill="{c["sub"]}">{esc(tagline)}</text>
  {"".join(parts)}

  <g transform="translate(1104,146)">
    <circle r="100" fill="none" stroke="{c["grid"]}" stroke-opacity="0.10" />
    <circle r="72" fill="none" stroke="{c["grid"]}" stroke-opacity="0.13" />
    <circle r="44" fill="none" stroke="{c["grid"]}" stroke-opacity="0.16" />
    <line x1="-100" y1="0" x2="100" y2="0" stroke="{c["grid"]}" stroke-opacity="0.08" />
    <line x1="0" y1="-100" x2="0" y2="100" stroke="{c["grid"]}" stroke-opacity="0.08" />
    <g>
      <path d="M0 0 L55 -45 A71 71 0 0 0 0 -71 Z" fill="url(#sweep)" />
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="7s" repeatCount="indefinite" />
    </g>
    <circle r="3.5" fill="{c["accent2"]}" />
    <circle cx="42" cy="-20" r="3" fill="{c["ok"]}" />
    <circle cx="-50" cy="32" r="2.6" fill="{c["accent"]}" />
    <circle cx="18" cy="56" r="2.2" fill="{c["warn"]}" />
    <circle cx="-26" cy="-44" r="2" fill="{c["accent"]}" />
    <text x="0" y="132" text-anchor="middle" font-size="12.5" letter-spacing="3"
          font-family="{MONO}" fill="{c["dim"]}">{esc(radar_label)}</text>
  </g>
</svg>
'''


def terminal(theme: str, title: str, lines: list[tuple[str, str]]) -> str:
    c = THEMES[theme]
    w = 640
    line_h = 26
    top = 74
    h = top + line_h * len(lines) + 26
    dots = "".join(
        f'<circle cx="{24 + i * 20}" cy="26" r="6" fill="{col}" />'
        for i, col in enumerate(c["term_dot"])
    )
    body = []
    for i, (kind, text) in enumerate(lines):
        y = top + i * line_h
        if kind == "cmd":
            body.append(
                f'<text x="24" y="{y}" font-size="15" font-family="{MONO}" fill="{c["title"]}" '
                f'xml:space="preserve"><tspan fill="{c["ok"]}">$ </tspan>{esc(text)}</text>'
            )
        elif kind == "hl":
            body.append(
                f'<text x="40" y="{y}" font-size="15" font-family="{MONO}" fill="{c["accent"]}" '
                f'xml:space="preserve">{esc(text)}</text>'
            )
        elif kind == "dim":
            body.append(
                f'<text x="24" y="{y}" font-size="15" font-family="{MONO}" fill="{c["dim"]}" '
                f'xml:space="preserve">{esc(text)}</text>'
            )
        else:
            body.append(
                f'<text x="40" y="{y}" font-size="15" font-family="{MONO}" fill="{c["sub"]}" '
                f'xml:space="preserve">{esc(text)}</text>'
            )
    cursor_y = top + len(lines) * line_h
    body.append(
        f'<rect x="24" y="{cursor_y - 14}" width="9" height="17" fill="{c["accent"]}">'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.5;0.5;0.99;1" '
        f'dur="1.4s" repeatCount="indefinite" /></rect>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
  <rect width="{w}" height="{h}" rx="14" fill="{c["term_bg"]}" stroke="{c["border"]}" />
  <path d="M0 14a14 14 0 0 1 14-14h{w - 28}a14 14 0 0 1 14 14v38H0z" fill="{c["term_head"]}" />
  <line x1="0" y1="52" x2="{w}" y2="52" stroke="{c["border"]}" />
  {dots}
  <text x="{w / 2:.0f}" y="31" text-anchor="middle" font-size="14" font-family="{MONO}"
        fill="{c["sub"]}">{esc(title)}</text>
  {"".join(body)}
</svg>
'''


def status_badge(theme: str, label: str, color_key: str) -> str:
    c = THEMES[theme]
    color = c[color_key]
    w = 26 + len(label) * 13.0
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="32" viewBox="0 0 {w:.0f} 32" role="img" aria-label="{esc(label)}">
  <rect width="{w:.0f}" height="32" rx="16" fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" />
  <circle cx="16" cy="16" r="4.5" fill="{color}" />
  <text x="29" y="21" font-size="14" font-family="{SANS}" fill="{c["sub"]}">{esc(label)}</text>
</svg>
'''


FALLBACK_LANG_DATE = "2026-11-01"
FALLBACK_LANGS = {
    "Python": 2418736, "Vue": 101841, "C++": 61928, "JavaScript": 20292,
    "Batchfile": 21069, "CSS": 18385, "Shell": 18702, "PowerShell": 6791,
}
LANG_COLORS = {
    "Python": "#3776AB", "Vue": "#41B883", "C++": "#00599C", "JavaScript": "#E8B100",
    "Batchfile": "#C1F12E", "CSS": "#663399", "Shell": "#89E051", "TypeScript": "#3178C6",
    "Go": "#00ADD8", "PowerShell": "#5391FE", "HTML": "#E34F26", "Java": "#B07219",
    "C": "#555555", "C#": "#178600", "Jupyter Notebook": "#DA5B0B", "Rust": "#DEA584",
    "其他 · Others": "#8B949E", "Others": "#8B949E",
}


def fetch_languages(user: str) -> tuple[dict[str, int], str]:
    """汇总公开仓库语言字节数（跳过 fork）；失败就退回离线快照。

    优先用 gh CLI（本机网络下最稳），没有 gh 再直连 / 走代理，最后才用快照。
    """
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "profile-assets"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def gh_json(path: str):
        try:
            import subprocess
            out = subprocess.run(
                ["gh", "api", path], capture_output=True, text=True,
                timeout=40, encoding="utf-8",
            )
            if out.returncode == 0 and out.stdout.strip():
                return json.loads(out.stdout)
        except Exception:
            pass
        return None

    def gh_collect() -> dict[str, int]:
        repos = gh_json(f"users/{user}/repos?per_page=100")
        if not repos:
            raise RuntimeError("gh api returned nothing")
        totals: dict[str, int] = {}
        for repo in repos:
            if repo.get("fork"):
                continue
            langs = gh_json(f"repos/{user}/{repo['name']}/languages")
            if langs is None:
                raise RuntimeError(f"gh api failed for {repo['name']}")
            for lang, size in langs.items():
                totals[lang] = totals.get(lang, 0) + size
        return totals

    def make_get(opener):
        def get(url: str):
            last = None
            for _ in range(2):
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with opener.open(req, timeout=12) as resp:
                        return json.load(resp)
                except Exception as exc:
                    last = exc
                    time.sleep(1)
            raise last
        return get

    def http_collect(get) -> dict[str, int]:
        repos = get(f"https://api.github.com/users/{user}/repos?per_page=100")
        totals: dict[str, int] = {}
        for repo in repos:
            if repo.get("fork"):
                continue
            # 任一仓库失败就整体作废，避免缓存的占比是残缺数据
            langs = get(f"https://api.github.com/repos/{user}/{repo['name']}/languages")
            for lang, size in langs.items():
                totals[lang] = totals.get(lang, 0) + size
        return totals

    attempts = [
        ("gh CLI", gh_collect),
        ("直连", lambda: http_collect(make_get(urllib.request.build_opener(urllib.request.ProxyHandler({}))))),
        ("代理", lambda: http_collect(make_get(urllib.request.build_opener()))),
    ]
    for label, collect in attempts:
        try:
            totals = collect()
            if totals:
                return totals, date.today().isoformat()
        except Exception as exc:
            print(f"  [提示] {label}拉取语言数据失败（{type(exc).__name__}）")
    return {}, ""


SNAPSHOT = Path(__file__).resolve().parent / "languages.json"


def load_languages(refresh: bool = False) -> tuple[dict[str, int], str]:
    """优先读 scripts/languages.json（可复现、不依赖网络）；--refresh 时重新拉取并落盘。"""
    if not refresh and SNAPSHOT.exists():
        data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        if data.get("totals"):
            return data["totals"], data.get("as_of", "unknown")

    totals, as_of = fetch_languages(OWNER)
    if totals:
        SNAPSHOT.write_text(json.dumps(
            {"as_of": as_of, "note": "公开仓库语言字节数（不含 fork）。--refresh 重新拉取并覆盖本文件。",
             "totals": dict(sorted(totals.items(), key=lambda kv: -kv[1]))},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  已更新 {SNAPSHOT.name}")
        return totals, as_of

    print("  [提示] 全部拉取失败，改用内置离线快照")
    return FALLBACK_LANGS, FALLBACK_LANG_DATE


def langcard(theme: str, totals: dict[str, int], as_of: str, top: int = 6) -> str:
    c = THEMES[theme]
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    head, rest = ranked[:top], ranked[top:]
    if rest:
        head = head + [("其他 · Others", sum(v for _, v in rest))]
    total = sum(v for _, v in head) or 1

    # 按 README 实际显示宽度（约 790px）设计，缩放后字号仍然可读
    w, h = 880, 222
    pad = 40
    bar_x, bar_y, bar_w, bar_h = pad, 88, w - pad * 2, 24
    segs, legend = [], []
    x = bar_x
    for i, (lang, size) in enumerate(head):
        frac = size / total
        seg_w = bar_w * frac
        color = LANG_COLORS.get(lang.split(" · ")[0], c["dim"])
        segs.append(
            f'<rect x="{x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_h}" '
            f'fill="{color}" rx="{3 if i in (0, len(head) - 1) else 0}" />'
        )
        if frac >= 0.07:
            segs.append(
                f'<text x="{x + seg_w / 2:.1f}" y="{bar_y + 17}" text-anchor="middle" '
                f'font-size="12" font-family="{MONO}" fill="#ffffff" '
                f'fill-opacity="0.94">{frac * 100:.1f}%</text>'
            )
        legend.append((lang, color, frac))
        x += seg_w

    size_bits = []
    lx, row = pad, 0
    row_limit = pad + bar_w * 0.62  # 两行更均衡，避免最后一行只剩一个孤立小条
    for lang, color, frac in legend:
        text = f"{lang} {frac * 100:.1f}%"
        cw = 27 + len(text) * 8.0
        if lx + cw > row_limit and lx > pad:
            lx, row = pad, row + 1
        ly = 132 + row * 34
        size_bits.append(
            f'<rect x="{lx:.0f}" y="{ly}" width="{cw:.0f}" height="29" rx="14.5" '
            f'fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" />'
            f'<circle cx="{lx + 15:.0f}" cy="{ly + 14.5:.0f}" r="4.5" fill="{color}" />'
            f'<text x="{lx + 26:.0f}" y="{ly + 19:.0f}" font-size="13" font-family="{MONO}" '
            f'fill="{c["sub"]}">{esc(text)}</text>'
        )
        lx += cw + 10

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="语言构成">
  <rect width="{w}" height="{h}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}" />
  <text x="{pad}" y="48" font-size="20" font-weight="600" font-family="{MONO}" fill="{c["title"]}">Language Mix</text>
  <text x="{w - pad}" y="48" text-anchor="end" font-size="12" font-family="{MONO}" fill="{c["dim"]}">公开仓库 · 字节占比 · 不含 fork · {esc(as_of)}</text>
  {"".join(segs)}
  {"".join(size_bits)}
</svg>
'''


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    written = []

    langs, lang_date = load_languages(refresh="--refresh" in sys.argv[1:])
    print(f"  语言数据：{len(langs)} 种，日期 {lang_date}")

    for theme in ("light", "dark"):
        written.append(("banner-%s.svg" % theme, banner(
            theme,
            eyebrow="HELLO THERE  ·  你好，我是",
            name=DISPLAY,
            tagline="AI 安全  /  LLM Agent  /  算子与推理加速",
            chips=["Python", "MCP / Agent", "PyTorch / SUPA", "FastAPI", "Docker"],
            radar_label="RECON → VERIFY",
        )))
        written.append(("terminal-%s.svg" % theme, terminal(
            theme,
            title="xinjun@junlume — zsh",
            lines=[
                ("cmd", "whoami"),
                ("out", "中北大学 · 翻斗花园 · AI 安全 / 算子与推理加速"),
                ("cmd", "ls ~/projects --sort=impact"),
                ("hl", "corehacker/              AI 渗透测试框架（多 Agent + MCP）"),
                ("hl", "birensupa-spectralconv/  SUPA 算子 + FNO-NS"),
                ("hl", "textbook-exercise-rag/   教材习题解析（RAG）"),
                ("hl", "fandou-t-mac/            T-MAC 移植鸿蒙 · 22 tok/s"),
                ("cmd", "pytest -q && python eval.py"),
                ("out", "158 passed · 引用命中 98.3%"),
            ],
        )))
        written.append(("langcard-%s.svg" % theme, langcard(theme, langs, lang_date)))
        for key, label, color_key in (
            ("building", "在做 · Building", "accent"),
            ("shipped", "已完成 · Shipped", "ok"),
            ("learning", "在学 · Learning", "warn"),
        ):
            written.append(("status-%s-%s.svg" % (key, theme), status_badge(theme, label, color_key)))

    for name, content in written:
        (ASSETS / name).write_text(content, encoding="utf-8")
        print(f"  写出 assets/{name}  ({len(content.encode('utf-8'))} B)")
    print(f"\n共 {len(written)} 个素材，目录：{ASSETS}")


if __name__ == "__main__":
    main()
